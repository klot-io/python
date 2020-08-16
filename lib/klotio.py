import os
import glob
import yaml
import logging
import requests
import pythonjsonlogger.jsonlogger


def logger(name):

    level = os.environ.get("LOG_LEVEL", "WARNING")

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


def derive(integrate):

    if "url" in integrate:
        response = requests.options(integrate["url"])
    elif "node" in integrate:
        response = requests.options(f"http://api.klot-io/node", params=integrate["node"])

    response.raise_for_status()

    return response.json()

def integrate(integration):

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

    integrations = []

    for integration_path in sorted(glob.glob(f"/opt/service/config/integration_*_{form}.fields.yaml")):
        with open(integration_path, "r") as integration_file:
            integrations.append(integrate({**{"name": integration_path.split("_")[1], **yaml.safe_load(integration_file)}}))

    return integrations
