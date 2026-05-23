__version__ = "1.0"

"""
CourseraGrab - a friendly desktop app for downloading the Coursera courses you
are enrolled in (videos, subtitles, quizzes, notebooks and other resources),
organised week by week just like on the site.

This is the GUI front-end. The heavy lifting (talking to Coursera, parsing the
syllabus, downloading files) is done by the bundled engine, which is adapted
from the open-source coursera-dl project (see README).
"""

import os
import sys
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QRadioButton, QComboBox, QFileDialog, QMessageBox, QVBoxLayout, QHBoxLayout,
    QGridLayout, QAction, QGroupBox, QListWidget, QListWidgetItem, QPlainTextEdit,
    QProgressBar, QDialog, QSizePolicy, QToolButton, QStyle, QCheckBox
)
from PyQt5.QtGui import QIcon, QPixmap, QCursor
from PyQt5.QtCore import Qt, QSize, QProcess, QUrl, QEvent, pyqtSignal
from PyQt5.QtGui import QDesktopServices

from threading import Thread

import app_helpers as general
import theme
from courses_api import fetch_enrolled_courses, build_session
from localdb import SimpleDB

APP_NAME = "CourseraGrab"
APP_DIR = os.path.abspath(os.path.dirname(__file__))

# Developer links
GITHUB_PROFILE = "https://github.com/Hesamsamani"
REPO_URL = "https://github.com/Hesamsamani/CourseraGrab"

# True when running from a PyInstaller-built .exe.
IS_FROZEN = getattr(sys, 'frozen', False)
# Special flag the GUI passes to a second copy of the .exe to run it in
# "download worker" mode instead of opening the window (frozen builds only).
WORKER_FLAG = '--coursera-worker'
# A writable working directory for the download subprocess.
WORK_DIR = os.path.dirname(sys.executable) if IS_FROZEN else APP_DIR


def resource_path(*parts):
    """Resolve a read-only bundled resource (e.g. the icon).

    PyInstaller unpacks bundled data into a temp folder exposed as
    sys._MEIPASS; in normal runs we just use the project directory.
    """
    base = getattr(sys, '_MEIPASS', APP_DIR)
    return os.path.join(base, *parts)


class MainWindow(QMainWindow):

    # Signals (so worker threads can talk safely to the GUI thread)
    courses_loaded = pyqtSignal(list, str)     # (courses, error_message)
    thumb_loaded = pyqtSignal(str, bytes)      # (slug, image_bytes)

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} - Coursera Course Downloader")
        self.setMinimumSize(1050, 900)
        for _cand in ('icon.ico', 'icon.png'):
            _p = resource_path('icon', _cand)
            if os.path.exists(_p):
                self.setWindowIcon(QIcon(_p))
                break

        self.localdb = SimpleDB('data.bin')
        self.theme = self.localdb.read('theme') or 'dark'
        self.course_view = self.localdb.read('course_view') or 'list'
        self.options = self.localdb.read('options') or {
            'subtitles': True, 'quizzes': True, 'notebooks': True}

        self.allowed_browsers = general.ALLOWED_BROWSERS
        self.sllangschoices = general.LANG_NAME_TO_CODE_MAPPING

        self.shouldResume = False
        self.process = None            # QProcess for the active download
        self._courses = []             # cached course list
        self._current_dl_meta = None   # info about the in-flight download

        self.initUI()
        self.apply_theme(self.theme)

        # wire signals
        self.courses_loaded.connect(self.on_courses_loaded)
        self.thumb_loaded.connect(self.on_thumb_loaded)
        self.showMaximized()
        

    # ------------------------------------------------------------------ UI
    def initUI(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout()
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(12)
        central.setLayout(root)

        # ----- Header bar
        header = QHBoxLayout()
        header.setSpacing(8)

        # App logo (top-left)
        self.logo_label = QLabel()
        logo_pm = self._load_logo_pixmap(72)
        if logo_pm is not None:
            self.logo_label.setPixmap(logo_pm)
        self.logo_label.setFixedSize(76, 76)
        self.logo_label.setAlignment(Qt.AlignCenter)
        header.addWidget(self.logo_label, alignment=Qt.AlignVCenter)

        title = QLabel(APP_NAME)
        title.setObjectName("appTitle")
        subtitle = QLabel("Download your enrolled Coursera courses, week by week.")
        subtitle.setObjectName("subheading")
        title_box = QVBoxLayout()
        title_box.setSpacing(0)
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch(1)

        # Top-bar action buttons (replace the old Menu dropdown)
        self.about_btn = self._make_topbar_button(
            QStyle.SP_MessageBoxInformation, "About", "About CourseraGrab", self.show_about)
        self.help_btn = self._make_topbar_button(
            QStyle.SP_MessageBoxQuestion, "Help", "How to use the app", self.show_help)
        self.history_btn = self._make_topbar_button(
            QStyle.SP_FileDialogDetailedView, "History", "Download history", self.show_history)
        for b in (self.about_btn, self.help_btn, self.history_btn):
            header.addWidget(b, alignment=Qt.AlignVCenter)

        self.theme_btn = QPushButton()
        self.theme_btn.setObjectName("ghost")
        self.theme_btn.setFixedWidth(120)
        self.theme_btn.clicked.connect(self.toggle_theme)
        header.addWidget(self.theme_btn, alignment=Qt.AlignVCenter)
        root.addLayout(header)

        # ----- Main content: left controls + right course library
        self._root_layout = root
        content = QHBoxLayout()
        content.setSpacing(12)
        content.addWidget(self._build_controls_panel(), 3)
        content.addWidget(self._build_library_panel(), 2)
        self._content_layout = content
        root.addLayout(content, 1)

        # ----- Progress console (collapsible; auto-collapses when not maximized)
        self.console_group = self._build_console_panel()
        root.addWidget(self.console_group)

        # ----- Footer: tip (left) | version (center) | GitHub + Star (right)
        footer = QGridLayout()
        footer.setContentsMargins(0, 0, 0, 0)
        for col in (0, 1, 2):
            footer.setColumnStretch(col, 1)

        tip = QLabel("Tip: select the browser you use for Coursera, then "
                     "click Load my courses to pull your enrollments.")
        tip.setObjectName("muted")
        ##tip.setWordWrap(True)
        tip.setMaximumWidth(940)
        tip.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        footer.addWidget(tip, 0, 0, Qt.AlignLeft | Qt.AlignVCenter)
        footer.setColumnStretch(0, 1)

        version_lbl = QLabel(f"CourseraGrab v{__version__}")
        version_lbl.setObjectName("version")
        version_lbl.setAlignment(Qt.AlignCenter)
        version_lbl.setToolTip("Installed version")
        footer.addWidget(version_lbl, 0, 1, Qt.AlignCenter)

        self.github_btn = QPushButton("  GitHub")
        self.github_btn.setObjectName("githubBadge")
        gh_icon = resource_path('icon', 'github-white.png')
        if os.path.exists(gh_icon):
            self.github_btn.setIcon(QIcon(gh_icon))
            self.github_btn.setIconSize(QSize(17, 17))
        self.github_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.github_btn.setToolTip("Open my GitHub profile")
        self.github_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(GITHUB_PROFILE)))

        self.star_btn = QPushButton("★  Star")
        self.star_btn.setObjectName("starBadge")
        self.star_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.star_btn.setToolTip("Open the repository on GitHub and give it a star")
        self.star_btn.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(REPO_URL)))

        badge_row = QHBoxLayout()
        badge_row.setSpacing(8)
        badge_row.addStretch(1)
        badge_row.addWidget(self.github_btn)
        badge_row.addWidget(self.star_btn)
        footer.addLayout(badge_row, 0, 2)
        root.addLayout(footer)

        # start with the log collapsed (window opens un-maximized)
        self._set_console_collapsed(True)
        self._refresh_theme_button_text()

    def _load_logo_pixmap(self, size):
        """Return the app logo scaled to `size` px, or None if not found."""
        for cand in ('icon.png', 'icon.ico'):
            p = resource_path('icon', cand)
            if os.path.exists(p):
                pm = QPixmap(p)
                if not pm.isNull():
                    return pm.scaled(size, size, Qt.KeepAspectRatio,
                                     Qt.SmoothTransformation)
        return None

    def _make_topbar_button(self, std_icon, text, tooltip, slot):
        """Build a flat icon+text button for the header (replaces the menu)."""
        btn = QToolButton()
        btn.setIcon(self.style().standardIcon(std_icon))
        btn.setText(text)
        btn.setToolTip(tooltip)
        btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        btn.setAutoRaise(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(slot)
        return btn

    def _build_controls_panel(self):
        group = QGroupBox("⚙  Download settings")
        layout = QVBoxLayout()
        layout.setSpacing(10)
        group.setLayout(layout)

        info = QLabel("CourseraGrab grabs the courses on your enrollment list. "
                      "Sign in to Coursera in your chosen browser before you start.")
        info.setObjectName("muted")
        info.setWordWrap(True)
        layout.addWidget(info)

        grid = QGridLayout()
        grid.setVerticalSpacing(8)
        grid.setHorizontalSpacing(10)
        layout.addLayout(grid)

        # Browser
        grid.addWidget(QLabel("Logged-in browser:"), 0, 0)
        self.browser_combo = QComboBox()
        self.browser_combo.addItems(self.allowed_browsers)
        default_browser = self.localdb.read('browser')
        if default_browser in self.allowed_browsers:
            self.browser_combo.setCurrentText(default_browser)
        grid.addWidget(self.browser_combo, 0, 1)

        # Course URL
        grid.addWidget(QLabel("Course URL or slug:"), 1, 0)
        self.classname_edit = QLineEdit(self.localdb.read('argdict').get('classname', ''))
        self.classname_edit.setPlaceholderText("https://www.coursera.org/learn/machine-learning")
        grid.addWidget(self.classname_edit, 1, 1)

        # Folder
        grid.addWidget(QLabel("Download folder:"), 2, 0)
        folder_row = QHBoxLayout()
        self.path_btn = QPushButton("📂  Browse")
        self.path_btn.clicked.connect(self.getPath)
        folder_row.addWidget(self.path_btn)
        self.open_folder_btn = QPushButton("Open")
        self.open_folder_btn.setObjectName("ghost")
        self.open_folder_btn.clicked.connect(self.open_download_folder)
        folder_row.addWidget(self.open_folder_btn)
        grid.addLayout(folder_row, 2, 1)
        self.path_label = QLabel(self.localdb.read('argdict').get('path', '') or "No folder selected")
        self.path_label.setObjectName("muted")
        self.path_label.setWordWrap(True)
        grid.addWidget(self.path_label, 3, 1)

        # Resolution
        grid.addWidget(QLabel("Video quality:"), 4, 0)
        res_row = QHBoxLayout()
        self.res_720 = QRadioButton("720p")
        self.res_540 = QRadioButton("540p")
        self.res_360 = QRadioButton("360p")
        for w in (self.res_720, self.res_540, self.res_360):
            res_row.addWidget(w)
        res_row.addStretch(1)
        grid.addLayout(res_row, 4, 1)
        current_res = self.localdb.read('argdict').get('video_resolution', '720p')
        {'540p': self.res_540, '360p': self.res_360}.get(current_res, self.res_720).setChecked(True)

        # Subtitle language
        grid.addWidget(QLabel("Subtitles in:"), 5, 0)
        self.sl_combo = QComboBox()
        self.sl_combo.addItems(sorted(self.sllangschoices.keys()))
        saved_sl = self.localdb.read('argdict').get('sl', 'en')
        key = next((k for k, v in self.sllangschoices.items() if v == saved_sl), 'English')
        self.sl_combo.setCurrentText(key)
        grid.addWidget(self.sl_combo, 5, 1)

        # keep the live summary in sync with these inputs
        self.classname_edit.textChanged.connect(self._update_summary)
        self.sl_combo.currentTextChanged.connect(self._update_summary)
        for r in (self.res_720, self.res_540, self.res_360):
            r.toggled.connect(self._update_summary)

        # ----- Content to include
        content_title = QLabel("CONTENT TO INCLUDE")
        content_title.setObjectName("sectionTitle")
        layout.addWidget(content_title)

        content_row = QHBoxLayout()
        self.opt_subtitles = QCheckBox("Subtitles")
        self.opt_quizzes = QCheckBox("Quizzes")
        self.opt_notebooks = QCheckBox("Jupyter notebooks")
        self.opt_subtitles.setChecked(bool(self.options.get('subtitles', True)))
        self.opt_quizzes.setChecked(bool(self.options.get('quizzes', True)))
        self.opt_notebooks.setChecked(bool(self.options.get('notebooks', True)))
        self.opt_subtitles.setToolTip("Download .srt subtitles in the chosen language")
        self.opt_quizzes.setToolTip("Download quizzes and exams as HTML")
        self.opt_notebooks.setToolTip("Download Jupyter notebooks where available")
        for cb in (self.opt_subtitles, self.opt_quizzes, self.opt_notebooks):
            cb.toggled.connect(self._on_option_changed)
            content_row.addWidget(cb)
        content_row.addStretch(1)
        layout.addLayout(content_row)

        # ----- Live download summary (fills the panel nicely + confirms settings)
        self.summary_group = QGroupBox("🧾  Download summary")
        sg = QVBoxLayout()
        self.summary_group.setLayout(sg)
        self.summary_label = QLabel()
        self.summary_label.setObjectName("summary")
        self.summary_label.setWordWrap(True)
        self.summary_label.setTextFormat(Qt.RichText)
        self.summary_label.setAlignment(Qt.AlignTop)
        sg.addWidget(self.summary_label)
        layout.addWidget(self.summary_group, 1)

        self._update_summary()

        # Action buttons
        btn_row = QHBoxLayout()
        self.download_btn = QPushButton("⬇  Download")
        self.download_btn.setObjectName("primary")
        self.download_btn.clicked.connect(self.downloadBtnHandler)
        self.resume_btn = QPushButton("⏵  Resume")
        self.resume_btn.clicked.connect(self.resumeBtnHandler)
        self.stop_btn = QPushButton("⏹  Stop")
        self.stop_btn.setObjectName("danger")
        self.stop_btn.clicked.connect(self.stop_download)
        self.stop_btn.setEnabled(False)
        btn_row.addWidget(self.resume_btn)
        btn_row.addWidget(self.stop_btn)
        btn_row.addStretch(1)
        btn_row.addWidget(self.download_btn)
        layout.addLayout(btn_row)

        return group

    def _build_library_panel(self):
        group = QGroupBox("📚  My courses")
        layout = QVBoxLayout()
        layout.setSpacing(8)
        group.setLayout(layout)

        top = QHBoxLayout()
        self.load_courses_btn = QPushButton("⟳  Load my courses")
        self.load_courses_btn.setObjectName("ghost")
        self.load_courses_btn.clicked.connect(self.load_courses)
        top.addWidget(self.load_courses_btn)
        top.addStretch(1)
        # List/Grid view toggle
        self.view_toggle_btn = self._make_topbar_button(
            QStyle.SP_FileDialogListView, "Grid view",
            "Switch between list and grid view", self.toggle_course_view)
        top.addWidget(self.view_toggle_btn)
        layout.addLayout(top)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search your courses...")
        self.search_edit.textChanged.connect(self.filter_courses)
        layout.addWidget(self.search_edit)

        self.course_list = QListWidget()
        self.course_list.itemClicked.connect(self.on_course_clicked)
        self.course_list.itemDoubleClicked.connect(self.on_course_double_clicked)
        layout.addWidget(self.course_list, 1)
        self._apply_course_view()

        self.library_status = QLabel("Click \"Load my courses\" to see what you're enrolled in.")
        self.library_status.setObjectName("muted")
        self.library_status.setWordWrap(True)
        layout.addWidget(self.library_status)

        return group

    def _build_console_panel(self):
        group = QGroupBox("📥  Progress")
        layout = QVBoxLayout()
        layout.setSpacing(8)
        group.setLayout(layout)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)         # indeterminate "busy" style
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.console = QPlainTextEdit()
        self.console.setObjectName("console")
        self.console.setReadOnly(True)
        self.console.setMinimumHeight(150)
        self.console.setPlaceholderText("Download progress will appear here...")
        layout.addWidget(self.console)

        bottom = QHBoxLayout()
        self.status_label = QLabel("Ready.")
        self.status_label.setObjectName("muted")
        bottom.addWidget(self.status_label)
        bottom.addStretch(1)
        self.console_toggle_btn = QToolButton()
        self.console_toggle_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.console_toggle_btn.setAutoRaise(True)
        self.console_toggle_btn.setCursor(Qt.PointingHandCursor)
        self.console_toggle_btn.setToolTip("Show or hide the progress log")
        self.console_toggle_btn.clicked.connect(self.toggle_console)
        bottom.addWidget(self.console_toggle_btn)
        self.clear_log_btn = QPushButton("Clear log")
        self.clear_log_btn.setObjectName("ghost")
        self.clear_log_btn.clicked.connect(lambda: self.console.clear())
        bottom.addWidget(self.clear_log_btn)
        layout.addLayout(bottom)

        return group

    # -------------------------------------------------- Collapsible log
    def _set_console_collapsed(self, collapsed):
        """Show/hide the progress log and resize the panel accordingly."""
        self._console_collapsed = collapsed
        if hasattr(self, 'console'):
            self.console.setVisible(not collapsed)
        if collapsed and not (self.process is not None):
            self.progress.setVisible(False)
        # Give the top content all the room when the log is hidden; share it
        # when the log is open.
        if hasattr(self, '_root_layout'):
            self._root_layout.setStretchFactor(self._content_layout, 1)
            self._root_layout.setStretchFactor(
                self.console_group, 0 if collapsed else 3)
        self._update_console_toggle()

    def _update_console_toggle(self):
        collapsed = getattr(self, '_console_collapsed', False)
        if not hasattr(self, 'console_toggle_btn'):
            return
        self.console_toggle_btn.setText("Show log" if collapsed else "Hide log")
        self.console_toggle_btn.setIcon(self.style().standardIcon(
            QStyle.SP_TitleBarUnshadeButton if collapsed
            else QStyle.SP_TitleBarShadeButton))

    def toggle_console(self):
        self._set_console_collapsed(not getattr(self, '_console_collapsed', False))

    def changeEvent(self, event):
        """Auto-collapse the log when the window isn't maximised/fullscreen."""
        if event.type() == QEvent.WindowStateChange:
            self._sync_console_to_window_state()
        super().changeEvent(event)

    def _sync_console_to_window_state(self):
        # Keep the log open while a download is running so output stays visible.
        if self.process is not None:
            return
        maximized = bool(self.windowState() &
                         (Qt.WindowMaximized | Qt.WindowFullScreen))
        self._set_console_collapsed(not maximized)

    # --------------------------------------------------------------- Theme
    def apply_theme(self, name):
        self.theme = name
        QApplication.instance().setStyleSheet(theme.get_stylesheet(name))
        self._refresh_theme_button_text()

    def _refresh_theme_button_text(self):
        if not hasattr(self, 'theme_btn'):
            return
        self.theme_btn.setText("Light mode" if theme.is_dark(self.theme) else "Dark mode")

    def toggle_theme(self):
        new_theme = 'light' if theme.is_dark(self.theme) else 'dark'
        self.apply_theme(new_theme)
        self.localdb.set('theme', new_theme)

    # ------------------------------------------------------ Course library
    def load_courses(self):
        browser = self.browser_combo.currentText()
        self.localdb.update('browser', browser)
        self.library_status.setText("Reading authentication from your browser...")
        self.load_courses_btn.setEnabled(False)

        def worker():
            cauth = general.loadcauth('coursera.org', browser)
            if not cauth:
                self.courses_loaded.emit(
                    [],
                    "Could not read your Coursera login from this browser. "
                    "Log in on coursera.org first (and on Edge/Brave, run as administrator)."
                )
                return
            courses, err = fetch_enrolled_courses(cauth)
            self.courses_loaded.emit(courses, err or "")
            # fetch thumbnails after the list is shown
            if not err and courses:
                self._load_thumbnails(cauth, courses)

        Thread(target=worker, daemon=True).start()

    def _load_thumbnails(self, cauth, courses):
        try:
            session = build_session(cauth)
        except Exception:
            return
        for c in courses:
            url = c.get('photo_url')
            if not url:
                continue
            try:
                resp = session.get(url, timeout=10)
                if resp.ok and resp.content:
                    self.thumb_loaded.emit(c['slug'], resp.content)
            except Exception:
                continue

    def on_courses_loaded(self, courses, error_message):
        self.load_courses_btn.setEnabled(True)
        if error_message:
            self.library_status.setText(error_message)
            return
        self._courses = courses
        self.course_list.clear()
        for c in courses:
            item = QListWidgetItem(c['name'])
            item.setData(Qt.UserRole, c['slug'])
            item.setToolTip(f"{c['name']}\n{c['slug']}")
            self.course_list.addItem(item)
        if courses:
            self.library_status.setText(
                f"{len(courses)} course(s) found. Click one to use it, or double-click to start."
            )
        else:
            self.library_status.setText("No enrolled courses found for this account.")
        self._update_summary()  # may now resolve a friendly course name

    def on_thumb_loaded(self, slug, data):
        pixmap = QPixmap()
        if not pixmap.loadFromData(data):
            return
        icon = QIcon(pixmap)
        for i in range(self.course_list.count()):
            item = self.course_list.item(i)
            if item.data(Qt.UserRole) == slug:
                item.setIcon(icon)
                break

    def _apply_course_view(self):
        """Configure the course list for the current view mode (list/grid)."""
        grid = (self.course_view == 'grid')
        if grid:
            self.course_list.setViewMode(QListWidget.IconMode)
            self.course_list.setIconSize(QSize(128, 72))
            self.course_list.setGridSize(QSize(168, 138))
            self.course_list.setWordWrap(True)
            self.course_list.setSpacing(10)
        else:
            self.course_list.setViewMode(QListWidget.ListMode)
            self.course_list.setIconSize(QSize(56, 32))
            self.course_list.setGridSize(QSize())   # restore default sizing
            self.course_list.setWordWrap(False)
            self.course_list.setSpacing(2)
        self.course_list.setMovement(QListWidget.Static)
        self.course_list.setResizeMode(QListWidget.Adjust)
        if hasattr(self, 'view_toggle_btn'):
            # button label/icon describes the view it switches TO
            self.view_toggle_btn.setText("List view" if grid else "Grid view")
            self.view_toggle_btn.setIcon(self.style().standardIcon(
                QStyle.SP_FileDialogDetailedView if grid else QStyle.SP_FileDialogListView))

    def toggle_course_view(self):
        self.course_view = 'list' if self.course_view == 'grid' else 'grid'
        self.localdb.set('course_view', self.course_view)
        self._apply_course_view()

    def filter_courses(self, text):
        text = text.lower().strip()
        for i in range(self.course_list.count()):
            item = self.course_list.item(i)
            item.setHidden(text not in item.text().lower())

    def on_course_clicked(self, item):
        slug = item.data(Qt.UserRole)
        if slug:
            self.classname_edit.setText(f"https://www.coursera.org/learn/{slug}")

    def on_course_double_clicked(self, item):
        self.on_course_clicked(item)
        self.downloadBtnHandler()

    # ----------------------------------------------------------- Download
    def _collect_argdict(self):
        """Validate inputs and build the argument dict. Returns (argdict, error)."""
        browser = self.browser_combo.currentText()
        self.localdb.update('browser', browser)

        cauth = general.loadcauth('coursera.org', browser)
        if not cauth:
            return None, ("Could not read your Coursera login from this browser.\n"
                          "Make sure you're logged in on coursera.org in the selected "
                          "browser (on Edge/Brave you may need to run as administrator).")

        courseurl = self.classname_edit.text().strip()
        cname = general.urltoclassname(courseurl)
        if not cname:
            return None, "That doesn't look like a valid Coursera course URL or slug."

        path = self.path_label.text().strip()
        if not path or path == "No folder selected":
            return None, "Please choose a download folder first."

        if self.res_540.isChecked():
            res = '540p'
        elif self.res_360.isChecked():
            res = '360p'
        else:
            res = '720p'

        sl_name = self.sl_combo.currentText()
        langcode = self.sllangschoices.get(sl_name, 'en')

        # persist user choices
        self.localdb.update('argdict.ca', cauth)
        self.localdb.update('argdict.classname', courseurl)
        self.localdb.update('argdict.path', path)
        self.localdb.update('argdict.video_resolution', res)
        self.localdb.update('argdict.sl', sl_name)

        argdict = {
            'ca': cauth,
            'classname': cname,
            'path': path,
            'video_resolution': res,
            'sl': langcode if langcode else 'en',
        }
        ignore_srt = (langcode == '')
        return (argdict, ignore_srt), None

    def _build_command(self, argdict, ignore_srt, resume):
        """Translate the argument dict into a coursera-dl style command list."""
        cmd = []
        # auth first
        cmd += ['-ca', argdict['ca']]
        cmd += ['-sl', argdict['sl']]
        cmd += ['--video-resolution', argdict['video_resolution']]
        cmd += ['--path', argdict['path']]

        cmd += [
            '--disable-url-skipping',
            '--unrestricted-filenames',
            '--combined-section-lectures-nums',
            '--jobs', '1',
        ]
        # content-to-include toggles
        if self.options.get('quizzes', True):
            cmd.append('--download-quizzes')
        if self.options.get('notebooks', True):
            cmd.append('--download-notebooks')
        if ignore_srt or not self.options.get('subtitles', True):
            cmd += ['--ignore-formats', 'srt']
        if resume:
            cmd += ['--resume', '--cache-syllabus']

        # positional course name last
        cmd.append(argdict['classname'])
        return cmd

    def downloadBtnHandler(self):
        if self.process is not None:
            QMessageBox.information(self, "Busy", "A download is already running.")
            return

        result, error = self._collect_argdict()
        if error:
            QMessageBox.warning(self, "Check your inputs", error)
            return
        argdict, ignore_srt = result
        cmd = self._build_command(argdict, ignore_srt, self.shouldResume)

        self._current_dl_meta = {
            'slug': argdict['classname'],
            'path': argdict['path'],
        }
        self._start_process(cmd, resume=self.shouldResume)

    def resumeBtnHandler(self):
        self.shouldResume = True
        self.downloadBtnHandler()
        self.shouldResume = False

    def _start_process(self, cmd, resume=False):
        # In a frozen .exe we relaunch this same executable in worker mode;
        # during development we run the download_worker.py script with Python.
        if IS_FROZEN:
            program = sys.executable
            args = [WORKER_FLAG] + cmd
        else:
            program = sys.executable
            args = [os.path.join(APP_DIR, 'download_worker.py')] + cmd

        self.process = QProcess(self)
        self.process.setWorkingDirectory(WORK_DIR)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self._on_process_output)
        self.process.finished.connect(self._on_process_finished)
        self.process.errorOccurred.connect(self._on_process_error)

        self._set_running_state(True)
        self._set_console_collapsed(False)   # always show the log while running
        action = "Resuming" if resume else "Starting"
        self._append_console(f"\n=== {action} download: {self._current_dl_meta['slug']} ===\n")
        self.status_label.setText(f"{action} download...")

        self.process.start(program, args)

    def _on_process_output(self):
        if not self.process:
            return
        data = bytes(self.process.readAllStandardOutput()).decode('utf-8', errors='replace')
        if data:
            self._append_console(data)

    def _on_process_error(self, _err):
        self._append_console("\n[ERROR] Failed to launch the download engine. "
                             "Make sure Python and the app files are intact.\n")

    def _on_process_finished(self, exit_code, _status):
        self._append_console(f"\n=== Download process ended (exit code {exit_code}) ===\n")
        if exit_code == 0:
            self.status_label.setText("Done.")
            self._record_history()
        elif exit_code == 130:
            self.status_label.setText("Stopped. You can resume later.")
        else:
            self.status_label.setText("Finished with errors - check the log above.")
        self.process = None
        self._set_running_state(False)

    def stop_download(self):
        if self.process is None:
            return
        self._append_console("\n=== Stopping download... ===\n")
        self.status_label.setText("Stopping...")
        self.process.kill()

    def _set_running_state(self, running):
        self.download_btn.setEnabled(not running)
        self.resume_btn.setEnabled(not running)
        self.stop_btn.setEnabled(running)
        self.progress.setVisible(running)

    def _append_console(self, text):
        self.console.moveCursor(self.console.textCursor().End)
        self.console.insertPlainText(text)
        self.console.moveCursor(self.console.textCursor().End)

    # ------------------------------------------------------------ History
    def _record_history(self):
        if not self._current_dl_meta:
            return
        history = self.localdb.read('history') or []
        entry = {
            'slug': self._current_dl_meta['slug'],
            'path': self._current_dl_meta['path'],
            'time': datetime.now().strftime('%Y-%m-%d %H:%M'),
        }
        # de-duplicate by slug+path, keep most recent first
        history = [h for h in history if not (h.get('slug') == entry['slug']
                                              and h.get('path') == entry['path'])]
        history.insert(0, entry)
        history = history[:50]
        self.localdb.set('history', history)

    def show_history(self):
        history = self.localdb.read('history') or []
        dlg = QDialog(self)
        dlg.setWindowTitle("Download History")
        dlg.setMinimumSize(460, 360)
        v = QVBoxLayout()
        dlg.setLayout(v)

        title = QLabel("Recently downloaded courses")
        title.setObjectName("heading")
        v.addWidget(title)

        if not history:
            v.addWidget(QLabel("No downloads yet."))
        else:
            lst = QListWidget()
            for h in history:
                item = QListWidgetItem(f"{h.get('slug','?')}   -   {h.get('time','')}")
                item.setData(Qt.UserRole, h.get('path', ''))
                item.setToolTip(h.get('path', ''))
                lst.addItem(item)
            v.addWidget(lst, 1)

            open_btn = QPushButton("Open selected folder")
            open_btn.setObjectName("primary")

            def open_selected():
                item = lst.currentItem()
                if item:
                    self._open_path(item.data(Qt.UserRole))
            open_btn.clicked.connect(open_selected)
            v.addWidget(open_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        v.addWidget(close_btn)
        dlg.exec_()

    # -------------------------------------------------------------- Misc
    def _on_option_changed(self, _checked=False):
        self.options = {
            'subtitles': self.opt_subtitles.isChecked(),
            'quizzes': self.opt_quizzes.isChecked(),
            'notebooks': self.opt_notebooks.isChecked(),
        }
        self.localdb.set('options', self.options)
        self._update_summary()

    def _update_summary(self):
        """Refresh the live 'Download summary' card from the current inputs."""
        if not hasattr(self, 'summary_label'):
            return
        url = self.classname_edit.text().strip()
        slug = general.urltoclassname(url)

        # resolve a friendly course name if it's in the loaded library
        name = None
        for c in self._courses:
            if c.get('slug') == slug:
                name = c.get('name')
                break
        course = name or slug or '<i>not set</i>'

        if self.res_540.isChecked():
            res = '540p'
        elif self.res_360.isChecked():
            res = '360p'
        else:
            res = '720p'

        subs_on = self.opt_subtitles.isChecked()
        lang = self.sl_combo.currentText() if subs_on else 'Off'

        includes = ['Videos', 'Course resources']
        if subs_on:
            includes.append('Subtitles')
        if self.opt_quizzes.isChecked():
            includes.append('Quizzes')
        if self.opt_notebooks.isChecked():
            includes.append('Notebooks')

        folder = self.path_label.text().strip()
        if not folder or folder == 'No folder selected':
            folder = '<i>not set</i>'

        self.summary_label.setText(
            "<div style='line-height:1.7;'>"
            f"<b>Course:</b> {course}<br>"
            f"<b>Quality:</b> {res} &nbsp;&bull;&nbsp; <b>Subtitles:</b> {lang}<br>"
            f"<b>Includes:</b> {', '.join(includes)}<br>"
            f"<b>Saving to:</b> {folder}"
            "</div>"
        )

    def getPath(self):
        start = self.path_label.text()
        if start == "No folder selected":
            start = ""
        directory = QFileDialog.getExistingDirectory(self, "Select download folder", start)
        if directory:
            self.path_label.setText(directory)
            self.localdb.update('argdict.path', directory)
            self._update_summary()

    def open_download_folder(self):
        path = self.path_label.text().strip()
        if not path or path == "No folder selected":
            QMessageBox.information(self, "No folder", "Choose a download folder first.")
            return
        self._open_path(path)

    def _open_path(self, path):
        if path and os.path.isdir(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        else:
            QMessageBox.information(self, "Not found", "That folder no longer exists.")

    def show_about(self):
        from gui_components.about_text import get_about_text
        dlg = QDialog(self)
        dlg.setWindowTitle(f"About - {APP_NAME}")
        dlg.setMinimumWidth(460)
        v = QVBoxLayout()
        dlg.setLayout(v)

        logo = QLabel()
        pm = self._load_logo_pixmap(84)
        if pm is not None:
            logo.setPixmap(pm)
        logo.setAlignment(Qt.AlignCenter)
        v.addWidget(logo)

        body = QLabel(get_about_text(__version__))
        body.setTextFormat(Qt.RichText)
        body.setWordWrap(True)
        body.setOpenExternalLinks(True)
        body.setTextInteractionFlags(Qt.TextBrowserInteraction)
        v.addWidget(body)

        row = QHBoxLayout()
        row.addStretch(1)
        ok = QPushButton("OK")
        ok.setObjectName("primary")
        ok.clicked.connect(dlg.accept)
        row.addWidget(ok)
        v.addLayout(row)
        dlg.exec_()

    def show_help(self):
        from gui_components.help_text import get_help_text
        dlg = QMessageBox(self)
        dlg.setWindowTitle(f"Help - {APP_NAME}")
        dlg.setTextFormat(Qt.RichText)
        dlg.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        dlg.setText(get_help_text())
        dlg.setStandardButtons(QMessageBox.Ok)
        dlg.exec_()

    def closeEvent(self, event):
        # don't leave a download orphaned if the window is closed
        if self.process is not None:
            self.process.kill()
            self.process.waitForFinished(2000)
        event.accept()


if __name__ == "__main__":
    # Frozen .exe worker mode: if launched with the worker flag, run the
    # download engine instead of opening the GUI. (No window is created.)
    if len(sys.argv) > 1 and sys.argv[1] == WORKER_FLAG:
        import download_worker
        # Hand the remaining args to the worker as if it were called directly.
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        sys.exit(download_worker.run())

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

# CourseraGrab
