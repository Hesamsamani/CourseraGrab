<div align="center">

<img src="icon/icon.png" width="120" alt="CourseraGrab icon">

# CourseraGrab

**Download your enrolled Coursera courses, week by week.**

Videos, subtitles, quizzes, notebooks and resources, organised just like on the site.

A privacy-first Windows desktop app — no telemetry, no cloud uploads.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-41cd52?logo=qt&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)
[![Release](https://img.shields.io/github/v/release/Hesamsamani/CourseraGrab?label=release)](https://github.com/Hesamsamani/CourseraGrab/releases/latest)
[![Star](https://img.shields.io/github/stars/Hesamsamani/CourseraGrab?style=social)](https://github.com/Hesamsamani/CourseraGrab)

<img src="App_Interface.png" width="720" alt="CourseraGrab App Interface">

</div>

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