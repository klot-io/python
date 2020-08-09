import unittest

class MockRedis(object):

    def __init__(self, host, port):

        self.host = host
        self.port = port
        self.channel = None

        self.messages = []

    def __str__(self):

        return f"MockRedis<host={self.host},port={self.port}>"

    def publish(self, channel, message):

        self.channel = channel
        self.messages.append(message)


class MockLogger(object):

    def __init__(self, name):

        self.name = name
        self.events = []

    @staticmethod
    def event(level, message, extra=None):

        event = {
            "level": level,
            "message": message
        }

        if extra:
            event.update(extra)

        return event

    def log(self, level, message, extra=None):

        self.events.append(self.event(level, message, extra))

    def exception(self, message, extra=None):
        self.log("exception", message, extra)

    def critical(self, message, extra=None):
        self.log("critical", message, extra)

    def error(self, message, extra=None):
        self.log("error", message, extra)

    def warning(self, message, extra=None):
        self.log("warning", message, extra)

    def info(self, message, extra=None):
        self.log("info", message, extra)

    def debug(self, message, extra=None):
        self.log("debug", message, extra)


class TestCase(unittest.TestCase):

    maxDiff = None

    def assertLogged(self, logger, level, message, extra=None):

        self.assertIn(MockLogger.event(level, message, extra), logger.events)

    def assertNotLogged(self, logger, level, message, extra=None):

        self.assertNotIn(MockLogger.event(level, message, extra), logger.events)

    def assertFields(self, fields, data):

        items = fields.to_list()

        self.assertEqual(len(items), len(data), "fields")

        for index, field in enumerate(items):
            self.assertEqual(field, data[index], index)

    def assertStatusValue(self, response, code, key, value):

        self.assertEqual(response.status_code, code, response.json)
        self.assertEqual(response.json[key], value)

    def assertStatusFields(self, response, code, fields, errors=None):

        self.assertEqual(response.status_code, code, response.json)

        self.assertEqual(len(fields), len(response.json['fields']), "fields")

        for index, field in enumerate(fields):
            self.assertEqual(field, response.json['fields'][index], index)

        if errors or "errors" in response.json:

            self.assertIsNotNone(errors, response.json)
            self.assertIn("errors", response.json, response.json)

            self.assertEqual(errors, response.json['errors'], "errors")

    def assertStatusModel(self, response, code, key, model):

        self.assertEqual(response.status_code, code, response.json)

        for field in model:
            self.assertEqual(response.json[key][field], model[field], field)

    def assertStatusModels(self, response, code, key, models):

        self.assertEqual(response.status_code, code, response.json)

        for index, model in enumerate(models):
            for field in model:
                self.assertEqual(response.json[key][index][field], model[field], f"{index} {field}")