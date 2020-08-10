import os
import yaml
import logging
import pythonjsonlogger.jsonlogger


def logger(name):

    level = getattr(logging, os.environ.get("LOG_LEVEL", "WARNING"))

    logHandler = logging.StreamHandler()
    logHandler.setFormatter(pythonjsonlogger.jsonlogger.JsonFormatter(
        fmt="%(created)f %(asctime)s %(name)s %(levelname)s %(pathname)s %(funcName)s %(lineno)d %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S %Z"
    ))

    root = logging.getLogger()
    root.handlers = []
    root.addHandler(logHandler)
    root.setLevel(level)

    custom = logging.getLogger(name)
    custom.setLevel(level)

    return custom


def settings():

    with open("/opt/service/config/settings.yaml", "r") as settings_file:
        return yaml.safe_load(settings_file)
