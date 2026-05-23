"""
courses_api.py
==============

Lightweight helper for the CourseraGrab GUI that fetches the list of courses
the logged-in user is enrolled in, together with each course's display name and
thumbnail URL.

It reuses the same authentication mechanism as the downloader: a single CAUTH
cookie value (read from the user's browser) is enough to talk to Coursera's
public membership API.

This module is intentionally self-contained and side-effect free so it can be
unit tested and called from a background thread without touching the GUI.
"""

import logging

import requests

from auth import TLSAdapter

# Build a membership query that explicitly asks for the fields we render.
# Using an explicit `fields` clause guarantees `name`, `slug` and `photoUrl`
# come back regardless of Coursera's default field set.
MEMBERSHIPS_URL = (
    "https://api.coursera.org/api/memberships.v1"
    "?q=me&showHidden=true&filter=current,preEnrolled"
    "&includes=courseId,courses.v1"
    "&fields=courseId,"
    "courses.v1(name,slug,photoUrl,courseStatus,description)"
)

DEFAULT_TIMEOUT = 15


def build_session(cauth):
    """
    Create a requests session authenticated with the given CAUTH cookie.

    @param cauth: The value of the CAUTH cookie from a logged-in browser.
    @type cauth: str
    @return: A ready-to-use requests session.
    @rtype: requests.Session
    """
    session = requests.Session()
    session.mount("https://", TLSAdapter())
    session.cookies.set("CAUTH", cauth, domain=".coursera.org")
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            )
        }
    )
    return session


def fetch_enrolled_courses(cauth):
    """
    Fetch the list of courses the user is enrolled in.

    @param cauth: CAUTH cookie value from a logged-in browser.
    @type cauth: str

    @return: Tuple of (courses, error_message).
        `courses` is a list of dicts with keys: slug, name, photo_url.
        On success `error_message` is None; on failure `courses` is an empty
        list and `error_message` is a short human-readable string.
    @rtype: (list[dict], str | None)
    """
    if not cauth:
        return [], "No authentication found. Select the browser you're logged in with."

    try:
        session = build_session(cauth)
        reply = session.get(MEMBERSHIPS_URL, timeout=DEFAULT_TIMEOUT)
        reply.raise_for_status()
        data = reply.json()
    except requests.exceptions.Timeout:
        return [], "Timed out talking to Coursera. Check your internet connection."
    except requests.exceptions.ConnectionError:
        return [], "Could not connect to Coursera. Check your internet connection."
    except requests.exceptions.HTTPError as exc:
        status = getattr(exc.response, "status_code", "?")
        if status in (401, 403):
            return [], ("Authentication rejected. Make sure you're logged in on "
                        "coursera.org in the selected browser.")
        return [], f"Coursera returned an error (HTTP {status})."
    except ValueError:
        return [], "Got an unexpected response from Coursera."
    except Exception as exc:  # pragma: no cover - defensive catch-all
        logging.exception("Unexpected error fetching courses")
        return [], f"Unexpected error: {exc}"

    return _parse_courses(data), None


def _parse_courses(data):
    """
    Turn a raw memberships.v1 reply into a clean, de-duplicated, sorted list.

    @param data: Parsed JSON reply.
    @type data: dict
    @return: List of {slug, name, photo_url} dicts.
    @rtype: list[dict]
    """
    linked = (data or {}).get("linked", {})
    raw_courses = linked.get("courses.v1", []) or []

    courses = []
    seen = set()
    for course in raw_courses:
        slug = course.get("slug")
        if not slug or slug in seen:
            continue
        seen.add(slug)
        courses.append(
            {
                "slug": slug,
                "name": course.get("name") or slug,
                "photo_url": course.get("photoUrl") or "",
            }
        )

    courses.sort(key=lambda c: c["name"].lower())
    return courses


if __name__ == "__main__":
    # Manual smoke test:  python courses_api.py <CAUTH>
    import sys

    logging.basicConfig(level=logging.INFO)
    token = sys.argv[1] if len(sys.argv) > 1 else ""
    found, err = fetch_enrolled_courses(token)
    if err:
        print("ERROR:", err)
    else:
        print(f"Found {len(found)} courses:")
        for c in found:
            print(f"  - {c['name']}  ({c['slug']})")
