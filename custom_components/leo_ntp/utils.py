"""LeoNTP utils."""
from __future__ import annotations

import logging
import re

from .const import SHOW_DEBUG_AS_WARNING

_LOGGER = logging.getLogger(__name__)


def log_debug(input, force = False) -> None:
    """Log to logger as debug or force as warning."""
    if SHOW_DEBUG_AS_WARNING is True or force is True:
        _LOGGER.warning(input)
    else:
        _LOGGER.debug(input)


def format_entity_name(string: str) -> str:
    """Format entity name."""
    string = string.strip()
    string = re.sub(r"\s+", "_", string)
    string = re.sub(r"\W+", "", string).lower()
    return string


def sensor_name(string: str) -> str:
    """Format sensor name."""
    string = string.strip().replace("_", " ").title()
    return string
