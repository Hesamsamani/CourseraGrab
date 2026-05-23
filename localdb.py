"""
A very simple key-value database using Python's pickle module.
It supports basic operations like create, read, update, delete.
It also supports nested key paths for updates.
"""

import os
import sys
import pickle
from os import path


def _writable_base_dir():
    """Directory where the config file should live.

    When running normally this is the project folder. When frozen into a single
    .exe by PyInstaller, __file__ points inside a temporary extraction folder
    that is read-only and wiped on exit, so we store config next to the .exe
    instead (which keeps the app fully portable).
    """
    if getattr(sys, 'frozen', False):
        return path.dirname(sys.executable)
    return path.dirname(path.abspath(__file__))


class SimpleDB:
    def __init__(self, filename='data.bin'):
        self.filename = path.join(_writable_base_dir(), filename)
        self._data = self._load()

    def _load(self):
        """Load data from the file, or initialize an empty dict if file doesn't exist."""
        if not os.path.exists(self.filename):
            # create a database with default values
            self._save({
                'browser': 'edge',
                'theme': 'dark',
                'history': [],
                'argdict': {
                    'ca': '',
                    'classname': '',
                    'path': '',
                    'video_resolution': '720p',
                    'sl': 'en'
                }
            })
        with open(self.filename, 'rb') as f:
            data = pickle.load(f)

        # Forward-compatible migration: make sure newer keys exist even if the
        # database file was created by an older version.
        changed = False
        for key, default in (('browser', 'edge'), ('theme', 'dark'), ('history', [])):
            if key not in data:
                data[key] = default
                changed = True
        if changed:
            self._save(data)
        return data

    def _save(self, data):
        """Save current data to file."""
        with open(self.filename, 'wb') as f:
            pickle.dump(data, f)

    def create(self, key, value):
        """Create a new key-value pair. Raises error if key exists."""
        if key in self._data:
            raise KeyError(f"Key '{key}' already exists.")
        self._data[key] = value
        self._save(self._data)

    def read(self, key):
        """Read the value for a given key. Returns None if not found."""
        return self._data.get(key, None)

    def update(self, key_path, value):
        """Update value at top-level key or nested key path.
        example key_path: 'argdict.ca' or ['argdict', 'ca'].
        Raises KeyError if the key path is invalid.
        """
        if isinstance(key_path, str):
            key_path = key_path.split('.')  # support dot notation

        data_ref = self._data
        for key in key_path[:-1]:
            if key not in data_ref or not isinstance(data_ref[key], dict):
                raise KeyError(f"Path '{'.'.join(key_path)}' is invalid.")
            data_ref = data_ref[key]

        final_key = key_path[-1]
        if final_key not in data_ref:
            raise KeyError(f"Key '{final_key}' not found in path '{'.'.join(key_path)}'.")
        data_ref[final_key] = value
        self._save(self._data)

    def set(self, key, value):
        """Create the key if missing, otherwise update it (upsert)."""
        self._data[key] = value
        self._save(self._data)

    def delete(self, key):
        """Delete a key-value pair."""
        if key in self._data:
            del self._data[key]
            self._save(self._data)
        else:
            raise KeyError(f"Key '{key}' not found.")

    def get_full_db(self):
        """Return the full dictionary."""
        return dict(self._data)


if __name__ == '__main__':
    db = SimpleDB()
    print(db.get_full_db())
