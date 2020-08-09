import unittest
import unittest.mock

import klotio.unittest

class TestMockLogger(unittest.TestCase):

    def test___init__(self):

        logger = klotio.unittest.MockLogger()

        self.assertEqual(logger.events, [])

    def test_log(self):

        logger = klotio.unittest.MockLogger()

        logger.log("unit", "test", extra={"a": 1})

        self.assertEqual(logger.events, [{
            "level": "unit",
            "message": "test",
            "a": 1
        }])

    def test_exception(self):

        logger = klotio.unittest.MockLogger()

        logger.exception("test", extra={"a": 1})

        self.assertEqual(logger.events, [{
            "level": "exception",
            "message": "test",
            "a": 1
        }])

    def test_critical(self):

        logger = klotio.unittest.MockLogger()

        logger.critical("test", extra={"a": 1})

        self.assertEqual(logger.events, [{
            "level": "critical",
            "message": "test",
            "a": 1
        }])

    def test_error(self):

        logger = klotio.unittest.MockLogger()

        logger.error("test", extra={"a": 1})

        self.assertEqual(logger.events, [{
            "level": "error",
            "message": "test",
            "a": 1
        }])

    def test_warning(self):

        logger = klotio.unittest.MockLogger()

        logger.warning("test", extra={"a": 1})

        self.assertEqual(logger.events, [{
            "level": "warning",
            "message": "test",
            "a": 1
        }])

    def test_info(self):

        logger = klotio.unittest.MockLogger()

        logger.info("test", extra={"a": 1})

        self.assertEqual(logger.events, [{
            "level": "info",
            "message": "test",
            "a": 1
        }])

    def test_debug(self):

        logger = klotio.unittest.MockLogger()

        logger.debug("test", extra={"a": 1})

        self.assertEqual(logger.events, [{
            "level": "debug",
            "message": "test",
            "a": 1
        }])


class TestMockRedis(unittest.TestCase):

    def test___init__(self):

        redis = klotio.unittest.MockRedis("redis.com", 123)

        self.assertEqual(redis.host, "redis.com")
        self.assertEqual(redis.port, 123)
        self.assertIsNone(redis.channel)
        self.assertEqual(redis.messages, [])

    def test_publish(self):

        redis = klotio.unittest.MockRedis("redis.com", 123)

        redis.publish("unit", "test")

        self.assertEqual(redis.channel, "unit")
        self.assertEqual(redis.messages, ["test"])


class TestUnitTest(klotio.unittest.TestCase):

    def test_assertFields(self):

        fields = unittest.mock.MagicMock()

        fields.to_list.return_value = [1, 2, 3]

        self.assertFields(fields, [1, 2, 3])

    def test_assertassertStatusValue(self):

        response = unittest.mock.MagicMock()

        response.status_code = 200
        response.json = {"a": 1}

        self.assertStatusValue(response, 200, "a", 1)

    def test_assertStatusFields(self):

        response = unittest.mock.MagicMock()

        response.status_code = 200
        response.json = {
            "fields": [1, 2, 3],
            "errors": True
        }

        self.assertStatusFields(response, 200, [1, 2, 3], errors=True)

    def test_assertStatusModel(self):

        response = unittest.mock.MagicMock()

        response.status_code = 200
        response.json = {
            "model": {"a": 1}
        }

        self.assertStatusModel(response, 200, "model", {"a": 1})

    def test_assertStatusModels(self):

        response = unittest.mock.MagicMock()

        response.status_code = 200
        response.json = {
            "models": [
                {"a": 1}
            ]
        }

        self.assertStatusModels(response, 200, "models", [{"a": 1}])
