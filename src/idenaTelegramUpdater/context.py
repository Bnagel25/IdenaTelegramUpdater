import os
import logging
import json
from datetime import datetime

import attr

logger = logging.getLogger(__name__)

CONFIG_FILE = "idenaTelegramUpdater-config.json"
TIME_FORMAT = "%H:%M:%S"


def validate_address(_, _2, value):
    """ ERC20 Addresses are always 42 characters long """
    if value == "":
        return

    if len(value) != 42:
        raise ValueError("Address not in correct format")


def validate_alert_times(_, _2, values):
    """ Validate all datetime objects are in the correct format """
    for v in values:
        datetime.strptime(v, TIME_FORMAT)


def validate_node_port(_, _2, value):
    """ NodePort must be an integer"""
    if value == "":
        return

    port = int(value)
    if not 0 <= port <= 9999:
        raise ValueError("Port out of bounds")


@attr.s
class Context:
    """
    Application Context
    """

    reactor = attr.ib()
    config = attr.ib()
    home = attr.ib()


@attr.s
class Config:
    """
    Application Config
    """

    nodeAddress = attr.ib(default="", validator=[validate_address])
    nodeApiKey = attr.ib(default="", validator=attr.validators.instance_of(str))
    nodeHost = attr.ib(default="", validator=attr.validators.instance_of(str))
    nodePort = attr.ib(default="", validator=[validate_node_port])
    telegramToken = attr.ib(default="", validator=attr.validators.instance_of(str))
    telegramChatId = attr.ib(default="", validator=attr.validators.instance_of(str))
    alertTimes = attr.ib(default=[], validator=[validate_alert_times])
    alertForEpoch = attr.ib(
        default=True,
        converter=bool,
        validator=attr.validators.instance_of(bool)
    )


def _update_config(old, changes):
    """Update configuration with new values"""
    valid_keys = {f.name for f in attr.fields(Config)}
    requested_keys = set(changes.keys())
    change_keys = valid_keys.intersection(requested_keys)

    to_apply = {}
    for k in change_keys:
        to_apply[k] = changes[k]

    try:
        newconfig = attr.evolve(old, **to_apply)
    except Exception:
        logger.exception("Unable to apply config changes")
        raise
    else:
        return newconfig


def load_config(home):
    """Load the configuration from disk or use the default.

    Note that if the saved configuration contains an invalid value,
    the entire saved configuration is deemed untrustworthy and discarded.
    """
    filename = os.path.join(home, CONFIG_FILE)
    default = Config()

    try:
        with open(filename) as f:
            saved = json.load(f)
    except Exception as e:
        logger.warning("Unable to load config file: %s", str(e))
        return default

    try:
        new = _update_config(default, saved)
    except Exception:
        logger.exception("Unable to use saved configuration, reverting to default")
        return default
    else:
        return new


def init_context(home, reactor):
    """Initialize the application context."""
    config = load_config(home)
    return Context(reactor, config, home)
