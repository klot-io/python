import unittest
import unittest.mock
import klotio_unittest

import redis
import klotio


class TestMockRedis(unittest.TestCase):

    @unittest.mock.patch("redis.Redis", klotio_unittest.MockRedis)
    def setUp(self):

        self.redis = redis.Redis(host="unit", port=123)

    @unittest.mock.patch("redis.Redis", klotio_unittest.MockRedis)
    def test___init__(self):

        db = redis.Redis(host="test", port=456)

        self.assertEqual(db.host, "test")
        self.assertEqual(db.port, 456)
        self.assertIsNone(db.channel)
        self.assertEqual(db.messages, [])

    @unittest.mock.patch("redis.Redis", klotio_unittest.MockRedis)
    def test___str__(self):

        db = redis.Redis(host="cheese", port=789)

        self.assertEqual(str(db), "MockRedis<host=cheese,port=789>")

    def test_publish(self):

        self.redis.publish("unit-test", "test-unit")

        self.assertEqual(self.redis.channel, "unit-test")
        self.assertEqual(self.redis.messages, ["test-unit"])

    def test_pubsub(self):

        self.assertEqual(self.redis.pubsub(), self.redis)

    def test_subscribe(self):

        self.redis.subscribe("stuff")

        self.assertEqual(self.redis.channel, "stuff")

    def test_get_message(self):

        self.redis.messages = ["things"]

        self.assertEqual(self.redis.get_message(), "things")


class TestMockLogger(unittest.TestCase):

    @unittest.mock.patch("klotio.logger", klotio_unittest.MockLogger)
    def setUp(self):

        self.logger = klotio.logger("unit")

    @unittest.mock.patch("klotio.logger", klotio_unittest.MockLogger)
    def test___init__(self):

        logger = klotio.logger("test")

        self.assertEqual(logger.name, "test")
        self.assertEqual(logger.events, [])

    def test_event(self):

        self.assertEqual(klotio_unittest.MockLogger.event("unit", "test", extra={"a": 1}), {
            "level": "unit",
            "message": "test",
            "a": 1
        })

    def test_log(self):

        self.logger.log("unit", "test", extra={"a": 1})

        self.assertEqual(self.logger.events, [{
            "level": "unit",
            "message": "test",
            "a": 1
        }])

    def test_exception(self):

        self.logger.exception("test", extra={"a": 1})

        self.assertEqual(self.logger.events, [{
            "level": "exception",
            "message": "test",
            "a": 1
        }])

    def test_critical(self):

        self.logger.critical("test", extra={"a": 1})

        self.assertEqual(self.logger.events, [{
            "level": "critical",
            "message": "test",
            "a": 1
        }])

    def test_error(self):

        self.logger.error("test", extra={"a": 1})

        self.assertEqual(self.logger.events, [{
            "level": "error",
            "message": "test",
            "a": 1
        }])

    def test_warning(self):

        self.logger.warning("test", extra={"a": 1})

        self.assertEqual(self.logger.events, [{
            "level": "warning",
            "message": "test",
            "a": 1
        }])

    def test_info(self):

        self.logger.info("test", extra={"a": 1})

        self.assertEqual(self.logger.events, [{
            "level": "info",
            "message": "test",
            "a": 1
        }])

    def test_debug(self):

        self.logger.debug("test", extra={"a": 1})

        self.assertEqual(self.logger.events, [{
            "level": "debug",
            "message": "test",
            "a": 1
        }])


class TestMockIntegrations(unittest.TestCase):

    @unittest.mock.patch("klotio.integrations", klotio_unittest.MockIntegrations())
    def test_integrations(self):

        self.assertEqual(klotio.integrations.forms, {})

        klotio.integrations.add("unit", "test")

        self.assertEqual(klotio.integrations("unit"), ["test"])

        self.assertEqual(klotio.integrations("nope"), [])

class TestUnitTest(klotio_unittest.TestCase):

    @unittest.mock.patch("klotio.logger", klotio_unittest.MockLogger)
    def setUp(self):

        self.logger = klotio.logger("unit")

    def test_consistent(self):

        # dict

        self.assertTrue(self.consistent({"a": 1}, {"a": 1, "b": 2}))
        self.assertFalse(self.consistent({"a": 2}, {"a": 1, "b": 2}))

        # list

        self.assertTrue(self.consistent([1, 2], [1, 2, 3]))
        self.assertFalse(self.consistent([1, 2, 4], [2, 1]))
        self.assertFalse(self.consistent([1, 2], [2, 1]))

        # else

        self.assertTrue(self.consistent("a", "a"))
        self.assertFalse(self.consistent("a", "b"))

    def test_contains(self):

        self.assertTrue(self.contains({"a": 1}, [{"a": 1, "b": 2}]))
        self.assertFalse(self.contains({"a": 2}, [{"a": 1, "b": 2}]))

    def test_assertConsistent(self):

        self.assertConsistent({"a": 1}, {"a": 1, "b": 2})

        with unittest.mock.patch('klotio_unittest.TestCase.assertEqual') as mock_equal:

            self.assertConsistent({"a": 2}, {"a": 1, "b": 2}, "nope")
            mock_equal.assert_called_once_with({"a": 2}, {"a": 1, "b": 2}, "nope")

    def test_assertContains(self):

        self.assertContains({"a": 1}, [{"a": 1, "b": 2}])

        with unittest.mock.patch('klotio_unittest.TestCase.assertIn') as mock_in:

            self.assertContains({"a": 2}, [{"a": 1, "b": 2}], "nope")
            mock_in.assert_called_once_with({"a": 2}, [{"a": 1, "b": 2}], "nope")

    def test_assertLogged(self):

        self.logger.info("sure", extra={"a": 1})

        self.assertLogged(self.logger, "info", "sure", extra={"a": 1})

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
