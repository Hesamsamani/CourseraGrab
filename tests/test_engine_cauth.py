"""Tests for CAUTH resolution in create_session."""

import os
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch


class TestCreateSessionCauth(unittest.TestCase):
    @patch('engine.get_session')
    def test_prefers_env_over_cli_flag(self, mock_get_session):
        session = MagicMock()
        mock_get_session.return_value = session
        args = SimpleNamespace(
            cookies_cauth='cli-token',
            browser=None,
            username=None,
            password=None,
        )

        with patch.dict(os.environ, {'COURSERA_CAUTH': 'env-token'}, clear=False):
            from engine import create_session
            create_session(args)

        session.cookies.set.assert_called_once_with('CAUTH', 'env-token')

    @patch('engine.get_session')
    def test_falls_back_to_cli_flag_without_env(self, mock_get_session):
        session = MagicMock()
        mock_get_session.return_value = session
        args = SimpleNamespace(
            cookies_cauth='cli-token',
            browser=None,
            username=None,
            password=None,
        )

        env = os.environ.copy()
        env.pop('COURSERA_CAUTH', None)
        with patch.dict(os.environ, env, clear=True):
            from engine import create_session
            create_session(args)

        session.cookies.set.assert_called_once_with('CAUTH', 'cli-token')


if __name__ == '__main__':
    unittest.main()