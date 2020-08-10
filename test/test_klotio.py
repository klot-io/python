import unittest
import unittest.mock

import logging
import klotio

class TestKlotIO(unittest.TestCase):

    def test_logger(self):

        custom = klotio.logger("unit-test")
        self.assertEqual(custom.name, "unit-test")

        root = logging.getLogger()
        self.assertEqual(root.name, "root")
        self.assertEqual(root.level, logging.WARNING)
        self.assertEqual(len(root.handlers), 1)
        self.assertEqual(root.handlers[0].__class__.__name__, "StreamHandler")
        self.assertEqual(root.handlers[0].formatter.__class__.__name__, "JsonFormatter")
        self.assertEqual(root.handlers[0].formatter._fmt, "%(created)f %(asctime)s %(name)s %(levelname)s %(pathname)s %(funcName)s %(lineno)d %(message)s")
        self.assertEqual(root.handlers[0].formatter.datefmt, "%Y-%m-%d %H:%M:%S %Z")

    @unittest.mock.patch("builtins.open", create=True)
    def test_settings(self, mock_open):

        mock_open.side_effect = [
            unittest.mock.mock_open(read_data='unit: test').return_value
        ]

        self.assertEqual(klotio.settings(), {"unit": "test"})

        mock_open.assert_called_once_with("/opt/service/config/settings.yaml", "r")
