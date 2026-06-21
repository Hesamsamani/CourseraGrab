<div align="center">

<img src="icon/icon.png" width="120" alt="CourseraGrab icon">

# CourseraGrab

**Windows GUI to download enrolled Coursera courses — videos, subtitles, and resources offline.**

Videos, subtitles, quizzes, notebooks and resources, organised week by week just like on the site.

A privacy-first Windows desktop app — no telemetry, no cloud uploads.

<p>
  <a href="https://github.com/Hesamsamani/CourseraGrab/releases/latest"><img src="https://img.shields.io/github/v/release/Hesamsamani/CourseraGrab?style=for-the-badge&label=%E2%AC%87%EF%B8%8F%20Download" alt="Latest release"></a>
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PyQt5-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PyQt5">
  <img src="https://img.shields.io/badge/platform-Windows%2010%2F11-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows">
  <img src="https://img.shields.io/badge/license-MIT-22c55e?style=for-the-badge" alt="MIT">
</p>

<p>
  <img src="https://img.shields.io/badge/video-FFmpeg-007808?style=for-the-badge&logo=ffmpeg&logoColor=white" alt="FFmpeg">
  <img src="https://img.shields.io/badge/auth-Selenium-43B02A?style=for-the-badge&logo=selenium&logoColor=white" alt="Selenium">
  <img src="https://img.shields.io/badge/courses-Coursera-0056D2?style=for-the-badge&logo=coursera&logoColor=white" alt="Coursera">
</p>

<img src="App_Interface.png" width="720" alt="CourseraGrab App Interface">

</div>

## ⚙️ How it works

```mermaid
flowchart LR
  subgraph auth["Browser session"]
    CK["rookiepy cookie import"]
  end

  subgraph api["Coursera API"]
    EC["Enrolled courses"]
    SY["Syllabus parse"]
  end

  subgraph worker["Download worker"]
    QP["QProcess subprocess"]
    EN["engine.py"]
    PO["Download pool"]
  end

  subgraph files["Local files"]
    VD["Videos"]
    ST["Subtitles"]
    RS["Quizzes · notebooks · resources"]
  end

  CK --> EC
  EC --> SY
  SY --> QP
  QP --> EN
  EN --> PO
  PO --> VD & ST & RS
```

1. **Import session** — CourseraGrab reads your browser login cookies via `rookiepy` (no password storage).
2. **List courses** — the GUI fetches enrolled courses and builds a week-by-week syllabus tree.
3. **Download in worker** — a `QProcess` subprocess runs `engine.py` so you can stop/resume without freezing the UI.
4. **Save locally** — videos, subtitles, quizzes, notebooks, and reading resources land in your chosen folder.

---

## ✨ Features

- **One-Click Offline Downloading:** Browse your enrolled Coursera courses and start downloading entire weeks with a single click.
- **Complete Course Materials:** Automatically grabs high-quality videos, localized subtitles, quizzes, Jupyter notebooks, and reading resources.
- **Live GUI Progress Tracking:** Clean PyQt5 interface featuring a live progress bar, real-time stop button, and download history.
- **Customizable UI:** Switch between list and grid views, and toggle between dark and light themes.
- **Smart Resuming:** Pause and resume downloads without losing progress, with quick access to your downloaded folders.
- **Quality Control:** Pick your preferred video resolution and select specific subtitle languages before downloading.

## 🛠️ Tech Highlights

| Area | Implementation |
|------|------------------|
| **UI** | PyQt5 desktop app with dark/light themes, list/grid course browser |
| **Auth** | Browser cookie extraction via `rookiepy` (no password storage) |
| **Downloads** | Multithreaded pool + isolated worker subprocess for clean stop/resume |
| **Persistence** | Local SQLite history, settings, and download state |
| **Packaging** | PyInstaller single-file `.exe` for Windows distribution |

**Stack:** Python 3.12 · PyQt5 · requests · BeautifulSoup · rookiepy · PyInstaller

The download engine is adapted from the open-source [coursera-dl](https://github.com/coursera-dl/coursera-dl) project.

---

## 🏗 Architecture

```mermaid
flowchart LR
  subgraph gui["PyQt5 · maingui.py"]
    MW["MainWindow"]
    UI["Course browser + progress"]
  end

  subgraph proc["Worker process"]
    QP["QProcess (--coursera-worker)"]
    EN["engine.py"]
    CB["course_builder.py"]
    FD["file_downloader.py"]
  end

  subgraph net["Networking"]
    AU["auth.py"]
    OD["ondemand_api.py"]
    CA["courses_api.py"]
  end

  subgraph data["Local persistence"]
    DB[(SQLite · localdb.py)]
  end

  MW --> AU
  AU --> CA
  CA --> OD
  MW --> QP
  QP --> EN
  EN --> CB & FD
  MW --> DB
  EN --> DB
```

| Layer | Tech |
|-------|------|
| GUI | PyQt5 — course browser, themes, live progress bar |
| Worker | Isolated `QProcess` subprocess for clean stop/resume |
| Engine | `engine.py` + coursera-dl–adapted download pipeline |
| Auth | Browser cookies via `rookiepy` — no credential storage |
| Persistence | SQLite history, settings, and download state |

---

## 🚀 Getting Started

There are two ways to use CourseraGrab: downloading the standalone app (recommended) or running it via the Python terminal.

### Method 1: Download the Windows App (.exe)
You do not need Python installed for this method.

[![Download Latest Release](https://img.shields.io/github/v/release/Hesamsamani/CourseraGrab?style=for-the-badge&label=Download%20.exe&color=success)](https://github.com/Hesamsamani/CourseraGrab/releases/latest)

1. Click the button above to go to the Releases page.
2. Download the `CourseraGrab.exe` file from the **Assets** section.
3. Double-click the `.exe` file to run the app.

### Method 2: Run via Terminal (Python)
If you prefer to run the raw Python code, make sure you have Python 3.12+ installed.

> ⚠️ **CRITICAL:** You MUST open your terminal (Command Prompt, PowerShell, or your IDE's Terminal) as an **Administrator**. If you do not run the terminal as an administrator, the script will not have permission to read your browser's login cookies and will fail to load your courses.

```bash
pip install -r requirements.txt
python maingui.py
```

---

## Credits

Built by **Hesam Samani** · [LinkedIn](https://www.linkedin.com/in/hesam-samani/) · [GitHub](https://github.com/Hesamsamani) · [Portfolio](https://hesamsamani.codes)

<sub>For personal, offline study of courses you are enrolled in. Please respect Coursera's Terms of Service.</sub>