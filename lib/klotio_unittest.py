"""
Module for unittesting and mocking general klot-io functionality
"""

#pylint: disable=unused-argument,invalid-name

import unittest

class MockRedis:
    """
    Object for mocking Redis
    """

    def __init__(self, host, port):
        """
        Keep track of the host/post, data with expirations, and
        any messages sent or received.
        """

        self.host = host
        self.port = port
        self.channel = None

        self.data = {}
        self.expires = {}
        self.messages = []

    def __str__(self):
        """
        String representation for testing logging
        """

        return f"MockRedis<host={self.host},port={self.port}>"

    def get(self, key):
        """
        Gets a value
        """

        return self.data.get(key)

    def set(self, key, value, ex=None):
        """
        Sets a values with optional expiration
        """

        self.data[key] = value
        self.expires[key] = ex

    def publish(self, channel, message):
        """
        Publish a message on a channel
        """

        self.channel = channel
        self.messages.append(message)

    def pubsub(self):
        """
        Mock creates a pubsub by returning itself
        """

        return self

    def subscribe(self, channel):
        """
        Subscirbes to a channel as a pubsub
        """

        self.channel = channel

    def get_message(self):
        """
        Gets a message as a pubsub
        """

        return self.messages.pop(0)


class MockLogger:
    """
    Class for mock and checking logging. Use as a patch.
    """

    def __init__(self, name):
        """
        Keep track of the name and clear the events
        """

        self.name = name
        self.clear()

    def clear(self):
        """
        Clears the events. Good between tests
        """

        self.events = []

    @staticmethod
    def event(level, message, extra=None):
        """
        Create and event structure
        """

        event = {
            "level": level,
            "message": message
        }

        if extra:
            event.update(extra)

        return event

    def log(self, level, message, extra=None, **kwargs):
        """
        Log something at a level with extra
        """

        self.events.append(self.event(level, message, extra))

    def exception(self, message, extra=None, **kwargs):
        """
        Log an exception
        """

        self.log("exception", message, extra)

    def critical(self, message, extra=None, **kwargs):
        """
        Log a critical
        """

        self.log("critical", message, extra)

    def error(self, message, extra=None, **kwargs):
        """
        Log an error
        """

        self.log("error", message, extra)

    def warning(self, message, extra=None, **kwargs):
        """
        Log a warning
        """

        self.log("warning", message, extra)

    def info(self, message, extra=None, **kwargs):
        """
        Log an info
        """

        self.log("info", message, extra)

    def debug(self, message, extra=None, **kwargs):
        """
        Log a debug
        """

        self.log("debug", message, extra)


class MockIntegrations:
    """
    Mocks integrations. Use in a patch.
    """

    def __init__(self):
        """
        Just keep track of what integrations for what forms
        """

        self.forms = {}

    def add(self, form, integrations):
        """
        Add integreations to a form. Can be a single or list.
        """

        if not isinstance(integrations, list):
            integrations = [integrations]

        self.forms.setdefault(form, [])

        self.forms[form].extend(integrations)

    def __call__(self, form):
        """
        Allows an instance to be called as a function, like the library it's patching.
        """

        return self.forms.get(form, [])


class TestCase(unittest.TestCase):
    """
    Extended unittest.TestCase with asserts used with klot-io
    """

    maxDiff = None

    def consistent(self, first, second):
        """
        A loose equals for checking only the parts of dictionares and lists you care about
        {"a": 1} is consistent with {"a": 1, "b": 2} while {"a": 2} is not
        [1,2] is consistent with [1,2,3] but [1,2,4] is not. Neither is [2,1]
        """

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
        """
        Checks to see if members is conistent with an item within container
        """

        for item in container:
            if self.consistent(member, item):
                return True

        return False

    def assertConsistent(self, first, second, message=None):
        """
        Asserts first is consistent with second
        """

        if not self.consistent(first, second):
            self.assertEqual(first, second, message)

    def assertContains(self, member, container, message=None):
        """
        Asserts member is contained within second
        """

        if not self.contains(member, container):
            self.assertIn(member, container, message)

    def assertLogged(self, logger, level, message, extra=None):
        """
        Assert event is contained within the logger's events
        """

        self.assertContains(MockLogger.event(level, message, extra), logger.events)

    def assertFields(self, fields, data):
        """
        Asserts fields object in list form equals data
        """

        items = fields.to_list()

        self.assertEqual(len(items), len(data), "fields")

        for index, field in enumerate(items):
            self.assertEqual(field, data[index], index)

    def assertStatusValue(self, response, code, key, value):
        """
        Assert a response's code and keyed json value are equal.
        Good with checking API responses in full with an outout
        of the json if unequal
        """

        self.assertEqual(response.status_code, code, response.json)
        self.assertEqual(response.json[key], value)

    def assertStatusFields(self, response, code, fields, errors=None):
        """
        Assert a response's code and keyed json fields are equal.
        Good with checking API responses  of options with an outout
        of the json if unequal
        """

        self.assertEqual(response.status_code, code, response.json)

        self.assertEqual(len(fields), len(response.json['fields']), "fields")

        for index, field in enumerate(fields):
            self.assertEqual(field, response.json['fields'][index], index)

        if errors or "errors" in response.json:

            self.assertIsNotNone(errors, response.json)
            self.assertIn("errors", response.json, response.json)

            self.assertEqual(errors, response.json['errors'], "errors")

    def assertStatusModel(self, response, code, key, model):
        """
        Assert a response's code and keyed json model are consitent.
        Good with checking API responses of creates, gets with an outout
        of the json if inconsistent
        """

        self.assertEqual(response.status_code, code, response.json)
        self.assertConsistent(model, response.json[key])

    def assertStatusModels(self, response, code, key, models):
        """
        Assert a response's code and keyed json models are consitent.
        Good with checking API responses of lists with an outout
        of the json if inconsistent
        """

        self.assertEqual(response.status_code, code, response.json)

        for index, model in enumerate(models):
            self.assertConsistent(model, response.json[key][index])
