"""
Module for general klot-io functionality
"""

# pylint: disable: invalid-name

import os
import glob
import yaml
import logging
import requests
import pythonjsonlogger.jsonlogger


def logger(name):
    """
    Creates a logget by name and sets the default logging to be structured
    """

    level = os.environ.get("LOG_LEVEL", "WARNING")

    handler = logging.StreamHandler()
    handler.setFormatter(pythonjsonlogger.jsonlogger.JsonFormatter(
        fmt="%(created)f %(asctime)s %(name)s %(levelname)s %(pathname)s %(funcName)s %(lineno)d %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S %Z"
    ))

    root = logging.getLogger()
    root.handlers = []
    root.addHandler(handler)
    root.setLevel(level)

    custom = logging.getLogger(name)
    custom.setLevel(level)

    return custom


def settings():
    """
    Loads and returns settings from the default config area
    """

    with open("/opt/service/config/settings.yaml", "r") as settings_file:
        return yaml.safe_load(settings_file)


def derive(derivation):
    """
    Derives the integrations to grab with wordplay
    """

    if "url" in derivation:
        response = requests.options(derivation["url"])
    elif "node" in derivation:
        response = requests.options("http://api.klot-io/node", params=derivation["node"])

    response.raise_for_status()

    return response.json()

def integrate(integration):
    """
    Integrates the values for a field including sub fields
    """

    if "integrate" in integration:
        try:
            integration.update(derive(integration["integrate"]))
        except Exception as exception:
            integration.setdefault("errors", [])
            integration["errors"].append(f"failed to integrate: {exception}")

    for field in integration.get("fields", []):
        integrate(field)

    return integration

def integrations(form):
    """
    Loads the integrations for a form, including looking up the values
    """

    integrated = []

    for integration_path in sorted(glob.glob(f"/opt/service/config/integration_*_{form}.fields.yaml")):
        with open(integration_path, "r") as integration_file:
            integrated.append(integrate({**{"name": integration_path.split("_")[1], **yaml.safe_load(integration_file)}}))

    return integrated
