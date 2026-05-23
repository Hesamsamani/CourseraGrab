<div align="center">

<img src="icon/icon.png" width="120" alt="CourseraGrab icon">

# CourseraGrab

**Download your enrolled Coursera courses, week by week.**

Videos, subtitles, quizzes, notebooks and resources, organised just like on the site.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-41cd52?logo=qt&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)
[![Star](https://img.shields.io/github/stars/Hesamsamani/CourseraGrab?style=social)](https://github.com/Hesamsamani/CourseraGrab)


---

<div align="center">
<img src="App_Interfac.png" width="1400" alt="CourseraGrab App Interface">
  
</div>
</div>

---

## Features

- Browse your enrolled courses and start a download with one click
- Live in-app progress with a real Stop button
- List and grid views, plus dark and light themes
- Resume downloads, history, and quick folder access
- Pick video quality and subtitle language

## Quick start

```bash
pip install -r requirements.txt
python maingui.py
```

Log in to coursera.org in your browser (Edge, Firefox or Brave), pick it in the app, click **Load my courses**, choose a folder, and hit **Download**.

> On Edge and Brave, run the app as administrator so it can read your login cookie.

## Build a Windows app

```bash
pip install pyinstaller
pyinstaller --clean CourseraGrab.spec
```

The standalone `CourseraGrab.exe` appears in `dist/`.

## Credits

Built by **Hesam Samani** &middot; [LinkedIn](https://www.linkedin.com/in/hesam-samani/) &middot; [GitHub](https://github.com/Hesamsamani)

Download engine adapted from the open-source [coursera-dl](https://github.com/coursera-dl/coursera-dl) project.

<sub>For personal, offline study of courses you are enrolled in. Please respect Coursera's Terms of Service.</sub>
