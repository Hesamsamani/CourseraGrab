"""
download_worker.py
==================

Subprocess entry point used by the CourseraGrab GUI.

The GUI launches this script with a QProcess and the usual coursera-dl style
command-line arguments. Running the download in a separate process gives us two
things the old in-thread approach could not:

  * a live progress feed - everything the downloader logs is streamed straight
    back to the GUI's in-app console, so the user never needs a terminal window;
  * a real Stop button - the GUI can simply terminate this process, which is far
    more reliable than trying to interrupt a worker thread.

Usage (handled automatically by the GUI):
    python download_worker.py <coursera-dl args...>
"""

import os
import sys

# Make sure output reaches the GUI immediately rather than sitting in a buffer.
os.environ.setdefault("PYTHONUNBUFFERED", "1")

# When this runs inside a PyInstaller "windowed" .exe, Python may set
# sys.stdout / sys.stderr to None. The GUI launches us with pipes attached to
# OS file descriptors 1 and 2, so we re-open those so our progress text still
# reaches the in-app console. Falls back to a null sink if that isn't possible.
for _name, _fd in (("stdout", 1), ("stderr", 2)):
    if getattr(sys, _name, None) is None:
        try:
            setattr(sys, _name,
                    os.fdopen(_fd, "w", buffering=1, encoding="utf-8", errors="replace"))
        except Exception:
            setattr(sys, _name, open(os.devnull, "w"))

try:
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
except Exception:
    pass

import requests

from engine import main_f
from auth import AuthenticationFailed, ClassNotFound


def run():
    cmd = sys.argv[1:]
    try:
        main_f(cmd)
        print("\n[DONE] Finished. You can close this download or start another.")
        return 0
    except KeyboardInterrupt:
        print("\n[STOPPED] Download stopped. Use Resume later to continue.")
        return 130
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Could not connect to Coursera. Check your internet connection.")
        return 2
    except requests.exceptions.SSLError as exc:
        print(f"\n[ERROR] SSL error: {exc}")
        return 3
    except requests.exceptions.HTTPError as exc:
        print(f"\n[ERROR] HTTP error: {exc}")
        print("Make sure you are logged in on coursera.org and enrolled in this course.")
        return 4
    except ClassNotFound as exc:
        print(f"\n[ERROR] Course not found: {exc}")
        return 5
    except AuthenticationFailed as exc:
        print(f"\n[ERROR] Authentication failed: {exc}")
        return 6
    except Exception as exc:  # pragma: no cover - surface anything else cleanly
        print(f"\n[ERROR] Something went wrong: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(run())
