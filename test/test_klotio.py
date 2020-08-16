import unittest
import unittest.mock

import yaml

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

    @unittest.mock.patch("requests.options")
    def test_derive(self, mock_options):

        mock_options.return_value.json.return_value = "yep"

        self.assertEqual(klotio.derive({"url": "sure"}), "yep")
        mock_options.assert_has_calls([
            unittest.mock.call("sure"),
            unittest.mock.call().raise_for_status(),
            unittest.mock.call().json()
        ])

        self.assertEqual(klotio.derive({"node": "sure"}), "yep")
        mock_options.assert_has_calls([
            unittest.mock.call("http://api.klot-io/node", params="sure"),
            unittest.mock.call().raise_for_status(),
            unittest.mock.call().json()
        ])

    @unittest.mock.patch("requests.options")
    def test_integrate(self, mock_options):

        def options(url, params=None):

            response = unittest.mock.MagicMock()

            if url == "sure":

                response.json.return_value = {
                    "fields": [
                        {
                            "integrate": {
                                "node": "yep"
                            }
                        },
                        {
                            "integrate": {
                                "url": "nope"
                            }
                        }
                    ]
                }

            elif url == "http://api.klot-io/node" and params == "yep":

                response.json.return_value = {
                    "name": "master"
                }

            elif url == "nope":

                response.raise_for_status.side_effect = Exception("whoops")

            return response

        mock_options.side_effect = options

        self.assertEqual(klotio.integrate({
            "integrate": {
                "url": "sure"
            }
        }), {
            "integrate": {
                "url": "sure"
            },
            "fields": [
                {
                    "integrate": {
                        "node": "yep"
                    },
                    "name": "master"
                },
                {
                    "integrate": {
                        "url": "nope"
                    },
                    "errors": ["failed to integrate: whoops"]
                }
            ]
        })

    @unittest.mock.patch("glob.glob")
    @unittest.mock.patch("klotio.open", create=True)
    @unittest.mock.patch("requests.options")
    def test_integrations(self, mock_options, mock_open, mock_glob):

        mock_glob.return_value = ["/opt/service/config/integration_unit.test_unittest.fields.yaml"]

        mock_open.side_effect = [
            unittest.mock.mock_open(read_data=yaml.safe_dump({
                "integrate": {
                    "url": "sure"
                }
            })).return_value
        ]

        def options(url, params=None):

            response = unittest.mock.MagicMock()

            if url == "sure":

                response.json.return_value = {
                    "fields": [
                        {
                            "integrate": {
                                "node": "yep"
                            }
                        },
                        {
                            "integrate": {
                                "url": "nope"
                            }
                        }
                    ]
                }

            elif url == "http://api.klot-io/node" and params == "yep":

                response.json.return_value = {
                    "name": "master"
                }

            elif url == "nope":

                response.raise_for_status.side_effect = Exception("whoops")

            return response

        mock_options.side_effect = options

        self.assertEqual(klotio.integrations("unittest"), [
            {
                "name": "unit.test",
                "integrate": {
                    "url": "sure"
                },
                "fields": [
                    {
                        "integrate": {
                            "node": "yep"
                        },
                        "name": "master"
                    },
                    {
                        "integrate": {
                            "url": "nope"
                        },
                        "errors": ["failed to integrate: whoops"]
                    }
                ]
            }
        ])

        mock_glob.assert_called_once_with("/opt/service/config/integration_*_unittest.fields.yaml")

        mock_open.assert_called_once_with("/opt/service/config/integration_unit.test_unittest.fields.yaml", "r")
