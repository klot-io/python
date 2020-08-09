import unittest
import unittest.mock

import logging
import klotio.logger

class TestLogger(unittest.TestCase):

    def test_setup(self):

        custom = klotio.logger.setup("unit-test")
        self.assertEqual(custom.name, "unit-test")

        root = logging.getLogger()
        self.assertEqual(root.name, "root")
        self.assertEqual(root.level, logging.WARNING)
        self.assertEqual(len(root.handlers), 1)
        self.assertEqual(root.handlers[0].__class__.__name__, "StreamHandler")
        self.assertEqual(root.handlers[0].formatter.__class__.__name__, "JsonFormatter")
        self.assertEqual(root.handlers[0].formatter._fmt, "%(created)f %(asctime)s %(name)s %(levelname)s %(message)s")
        self.assertEqual(root.handlers[0].formatter.datefmt, "%Y-%m-%d %H:%M:%S %Z")