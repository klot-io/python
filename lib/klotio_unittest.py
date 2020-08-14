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

    def pubsub(self):

        return self

    def subscribe(self, channel):

        self.channel = channel

    def get_message(self):

        return self.messages.pop(0)


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

    def log(self, level, message, extra=None, **kwargs):

        self.events.append(self.event(level, message, extra))

    def exception(self, message, extra=None, **kwargs):
        self.log("exception", message, extra)

    def critical(self, message, extra=None, **kwargs):
        self.log("critical", message, extra)

    def error(self, message, extra=None, **kwargs):
        self.log("error", message, extra)

    def warning(self, message, extra=None, **kwargs):
        self.log("warning", message, extra)

    def info(self, message, extra=None, **kwargs):
        self.log("info", message, extra)

    def debug(self, message, extra=None, **kwargs):
        self.log("debug", message, extra)


class MockIntegrations(object):

    def __init__(self):

        self.forms = {}

    def add(self, form, integrations):

        if not isinstance(integrations, list):
            integrations = [integrations]

        self.forms.setdefault(form, [])

        self.forms[form].extend(integrations)

    def __call__(self, form):

        return self.forms.get(form, [])


class TestCase(unittest.TestCase):

    maxDiff = None

    def consistent(self, first, second):

        if isinstance(first, dict) and isinstance(second, dict):

            for first_key, first_item in first.items():
                if first_key not in second or not self.consistent(first_item, second[first_key]):
                    return False

        elif isinstance(first, list) and isinstance(second, list):

            second_index = 0

            for first_item in first:

                found = False

                for second_index, second_item in enumerate(second[second_index:]):
                    if self.consistent(first_item, second_item):
                        found = True
                        break

                if not found:
                    return False

        else:

            return first == second

        return True

    def contains(self, member, container):

        for item in container:
            if self.consistent(member, item):
                return True

        return False

    def assertConsistent(self, first, second, message=None):

        if not self.consistent(first, second):
            self.assertEqual(first, second, message)

    def assertContains(self, member, container, message=None):

        if not self.contains(member, container):
            self.assertIn(member, container, message)

    def assertLogged(self, logger, level, message, extra=None):

        self.assertContains(MockLogger.event(level, message, extra), logger.events)

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
        self.assertConsistent(model, response.json[key])

    def assertStatusModels(self, response, code, key, models):

        self.assertEqual(response.status_code, code, response.json)

        for index, model in enumerate(models):
            self.assertConsistent(model, response.json[key][index])
