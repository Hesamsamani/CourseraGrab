"""Tests for localdb JSON storage and CAUTH handling."""

import json
import os
import pickle
import shutil
import tempfile
import unittest
from unittest.mock import patch

from localdb import SimpleDB


class TestLocalDB(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, 'data.bin')

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _db(self):
        with patch('localdb._writable_base_dir', return_value=self.tmpdir):
            return SimpleDB()

    def test_defaults_use_json_without_cauth(self):
        db = self._db()
        argdict = db.read('argdict')
        self.assertNotIn('ca', argdict)
        with open(self.db_path, 'r', encoding='utf-8') as handle:
            stored = json.load(handle)
        self.assertNotIn('ca', stored['argdict'])

    def test_json_roundtrip(self):
        db = self._db()
        db.set('theme', 'light')
        self.assertEqual(db.read('theme'), 'light')
        with open(self.db_path, 'r', encoding='utf-8') as handle:
            stored = json.load(handle)
        self.assertEqual(stored['theme'], 'light')

    def test_pickle_migration_strips_cauth_and_rewrites_json(self):
        legacy = {
            'browser': 'chrome',
            'theme': 'dark',
            'history': [],
            'argdict': {
                'ca': 'secret-token',
                'classname': 'ml',
                'path': '/tmp',
                'video_resolution': '720p',
                'sl': 'en',
            },
        }
        with open(self.db_path, 'wb') as handle:
            pickle.dump(legacy, handle)

        db = self._db()
        self.assertNotIn('ca', db.read('argdict'))

        with open(self.db_path, 'r', encoding='utf-8') as handle:
            stored = json.load(handle)
        self.assertNotIn('ca', stored['argdict'])
        self.assertEqual(stored['argdict']['classname'], 'ml')

    def test_update_rejects_cauth_persistence(self):
        db = self._db()
        with self.assertRaises(KeyError):
            db.update('argdict.ca', 'secret-token')


if __name__ == '__main__':
    unittest.main()