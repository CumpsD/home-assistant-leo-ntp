"""Models used by LeoNTP."""
from dataclasses import dataclass
from dataclasses import field
from typing import TypedDict


class LeoNtpConfigEntryData(TypedDict):
    """Config entry for the LeoNTP integration."""

    host: str | None
    update_interval: int | None


@dataclass
class LeoNtpItem:
    """LeoNTP item model."""

    name: str = ""
    key: str = ""
    type: str = ""
    state: str = ""
    data: dict = field(default_factory = dict)
    extra_attributes: dict = field(default_factory = dict)
    native_unit_of_measurement: str = None
