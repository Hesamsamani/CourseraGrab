"""
theme.py
========

Qt style sheets (QSS) for CourseraGrab's two themes: a modern dark theme and a
clean light theme. Keeping the styling here keeps maingui.py focused on
behaviour, and makes it trivial to tweak the look in one place.

Call `get_stylesheet("dark")` or `get_stylesheet("light")` and apply the result
with `app.setStyleSheet(...)` or `widget.setStyleSheet(...)`.
"""

# Coursera-style blue accent.
_ACCENT = "#0056D2"
_ACCENT_HOVER = "#0A66E0"
_ACCENT_PRESSED = "#00429E"

_DARK = {
    "bg": "#1E2128",
    "surface": "#272B33",
    "surface_alt": "#2E333C",
    "border": "#3A404B",
    "text": "#E6E9EF",
    "text_muted": "#9AA3B2",
    "accent": _ACCENT,
    "accent_hover": _ACCENT_HOVER,
    "accent_pressed": _ACCENT_PRESSED,
    "danger": "#E05260",
    "danger_hover": "#EC6975",
    "selection": "#34527A",
    "console_bg": "#15171C",
    "console_text": "#C8E1FF",
}

_LIGHT = {
    "bg": "#F4F6FA",
    "surface": "#FFFFFF",
    "surface_alt": "#EEF1F6",
    "border": "#D4DAE3",
    "text": "#1B2330",
    "text_muted": "#5B6675",
    "accent": _ACCENT,
    "accent_hover": _ACCENT_HOVER,
    "accent_pressed": _ACCENT_PRESSED,
    "danger": "#D7263D",
    "danger_hover": "#E23B51",
    "selection": "#CFE0FB",
    "console_bg": "#0F1115",
    "console_text": "#C8E1FF",
}


def _build(c):
    return f"""
    QMainWindow, QDialog {{
        background-color: {c['bg']};
    }}
    QWidget {{
        color: {c['text']};
        font-size: 13px;
    }}
    QLabel {{
        color: {c['text']};
        background: transparent;
    }}
    QLabel#muted {{
        color: {c['text_muted']};
    }}
    QLabel#heading {{
        font-size: 20px;
        font-weight: 700;
        color: {c['text']};
    }}
    QLabel#appTitle {{
        font-size: 24px;
        font-weight: 800;
        color: {c['accent']};
    }}
    QLabel#subheading {{
        font-size: 12px;
        color: {c['text_muted']};
    }}
    QLabel#sectionTitle {{
        font-size: 12px;
        font-weight: 700;
        color: {c['text_muted']};
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    /* Cards / group boxes */
    QGroupBox {{
        background-color: {c['surface']};
        border: 1px solid {c['border']};
        border-radius: 10px;
        margin-top: 8px;
        padding: 12px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 12px;
        padding: 0 4px;
        color: {c['text_muted']};
    }}

    /* Inputs */
    QLineEdit, QComboBox {{
        background-color: {c['surface_alt']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 7px 10px;
        selection-background-color: {c['selection']};
        color: {c['text']};
    }}
    QLineEdit:focus, QComboBox:focus {{
        border: 1px solid {c['accent']};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 22px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {c['surface']};
        border: 1px solid {c['border']};
        selection-background-color: {c['accent']};
        selection-color: #FFFFFF;
        outline: none;
    }}

    /* Buttons */
    QPushButton {{
        background-color: {c['surface_alt']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 8px 16px;
        color: {c['text']};
    }}
    QPushButton:hover {{
        border: 1px solid {c['accent']};
    }}
    QPushButton:disabled {{
        color: {c['text_muted']};
        background-color: {c['surface']};
    }}
    QPushButton#primary {{
        background-color: {c['accent']};
        border: 1px solid {c['accent']};
        color: #FFFFFF;
        font-weight: 600;
    }}
    QPushButton#primary:hover {{
        background-color: {c['accent_hover']};
        border: 1px solid {c['accent_hover']};
    }}
    QPushButton#primary:pressed {{
        background-color: {c['accent_pressed']};
    }}
    QPushButton#primary:disabled {{
        background-color: {c['surface_alt']};
        border: 1px solid {c['border']};
        color: {c['text_muted']};
    }}
    QPushButton#danger {{
        background-color: {c['danger']};
        border: 1px solid {c['danger']};
        color: #FFFFFF;
        font-weight: 600;
    }}
    QPushButton#danger:hover {{
        background-color: {c['danger_hover']};
        border: 1px solid {c['danger_hover']};
    }}
    QPushButton#ghost {{
        background-color: transparent;
        border: 1px solid {c['border']};
    }}
    QPushButton#ghost:hover {{
        border: 1px solid {c['accent']};
        color: {c['accent']};
    }}

    /* Tool buttons (top-bar actions, view toggle) */
    QToolButton {{
        background: transparent;
        border: 1px solid transparent;
        border-radius: 8px;
        padding: 6px 10px;
        color: {c['text']};
    }}
    QToolButton:hover {{
        background-color: {c['surface_alt']};
        border: 1px solid {c['accent']};
    }}
    QToolButton:pressed {{
        background-color: {c['surface']};
    }}

    /* Radio buttons */
    QRadioButton {{
        spacing: 6px;
        background: transparent;
    }}
    QRadioButton::indicator {{
        width: 15px;
        height: 15px;
        border-radius: 8px;
        border: 1px solid {c['border']};
        background: {c['surface_alt']};
    }}
    QRadioButton::indicator:checked {{
        border: 4px solid {c['accent']};
        background: #FFFFFF;
    }}

    /* Check boxes (content-to-include) */
    QCheckBox {{
        spacing: 6px;
        background: transparent;
    }}
    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border-radius: 4px;
        border: 1px solid {c['border']};
        background: {c['surface_alt']};
    }}
    QCheckBox::indicator:hover {{
        border: 1px solid {c['accent']};
    }}
    QCheckBox::indicator:checked {{
        border: 1px solid {c['accent']};
        background: {c['accent']};
    }}

    /* Live download summary card */
    QLabel#summary {{
        color: {c['text_muted']};
        font-size: 13px;
    }}

    /* Course list */
    QListWidget {{
        background-color: {c['surface']};
        border: 1px solid {c['border']};
        border-radius: 10px;
        padding: 4px;
        outline: none;
    }}
    QListWidget::item {{
        border-radius: 8px;
        padding: 6px;
        margin: 2px;
    }}
    QListWidget::item:hover {{
        background-color: {c['surface_alt']};
    }}
    QListWidget::item:selected {{
        background-color: {c['accent']};
        color: #FFFFFF;
    }}

    /* Console / progress log */
    QPlainTextEdit#console, QTextBrowser#console {{
        background-color: {c['console_bg']};
        color: {c['console_text']};
        border: 1px solid {c['border']};
        border-radius: 10px;
        padding: 8px;
        font-family: "Consolas", "Menlo", "DejaVu Sans Mono", monospace;
        font-size: 12px;
    }}

    QTextBrowser {{
        background-color: {c['surface']};
        border: 1px solid {c['border']};
        border-radius: 10px;
    }}

    /* Menu bar */
    QMenuBar {{
        background-color: {c['bg']};
        color: {c['text']};
    }}
    QMenuBar::item:selected {{
        background: {c['surface_alt']};
        border-radius: 6px;
    }}
    QMenu {{
        background-color: {c['surface']};
        border: 1px solid {c['border']};
    }}
    QMenu::item:selected {{
        background-color: {c['accent']};
        color: #FFFFFF;
    }}

    /* Progress bar */
    QProgressBar {{
        background-color: {c['surface_alt']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        text-align: center;
        height: 16px;
        color: {c['text']};
    }}
    QProgressBar::chunk {{
        background-color: {c['accent']};
        border-radius: 7px;
    }}

    /* Scrollbars */
    QScrollBar:vertical {{
        background: transparent;
        width: 10px;
        margin: 2px;
    }}
    QScrollBar::handle:vertical {{
        background: {c['border']};
        border-radius: 5px;
        min-height: 24px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {c['text_muted']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar:horizontal {{
        background: transparent;
        height: 10px;
        margin: 2px;
    }}
    QScrollBar::handle:horizontal {{
        background: {c['border']};
        border-radius: 5px;
        min-width: 24px;
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0;
    }}

    /* Footer version label */
    QLabel#version {{
        color: {c['text_muted']};
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }}

    /* GitHub-style footer badges (brand-dark in both themes) */
    QPushButton#githubBadge {{
        background-color: #24292F;
        border: 1px solid #444C56;
        border-radius: 8px;
        padding: 7px 16px 7px 12px;
        color: #FFFFFF;
        font-weight: 600;
    }}
    QPushButton#githubBadge:hover {{
        background-color: #30363D;
        border: 1px solid #6E7681;
    }}
    QPushButton#githubBadge:pressed {{
        background-color: #1C2128;
    }}
    QPushButton#starBadge {{
        background-color: #24292F;
        border: 1px solid #444C56;
        border-radius: 8px;
        padding: 7px 16px;
        color: #E3B341;
        font-weight: 700;
    }}
    QPushButton#starBadge:hover {{
        background-color: #30363D;
        border: 1px solid #E3B341;
        color: #F2CC60;
    }}
    QPushButton#starBadge:pressed {{
        background-color: #1C2128;
    }}
    """


def get_stylesheet(theme="dark"):
    """Return the QSS string for the requested theme ('dark' or 'light')."""
    return _build(_LIGHT if str(theme).lower() == "light" else _DARK)


def is_dark(theme):
    return str(theme).lower() != "light"
