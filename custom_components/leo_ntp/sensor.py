"""LeoNTP sensor platform."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import LeoNtpDataUpdateCoordinator
from .const import DOMAIN
from .entity import LeoNtpEntity
from .models import LeoNtpItem
from .utils import log_debug


@dataclass
class LeoNtpSensorDescription(SensorEntityDescription):
    """Class to describe a LeoNTP sensor."""

    value_fn: Callable[[Any], StateType] | None = None


SENSOR_DESCRIPTIONS: list[SensorEntityDescription] = [
    LeoNtpSensorDescription(
        key="utc_time",
        icon="mdi:clock-digital"
    ),
    LeoNtpSensorDescription(
        key="ntp_time",
        icon="mdi:clock-digital"
    ),
    LeoNtpSensorDescription(
        key="requests_served",
        icon="mdi:account-search-outline"
    ),
    LeoNtpSensorDescription(
        key="uptime",
        icon="mdi:timer-sand"
    ),
    LeoNtpSensorDescription(
        key="gps_lock_time",
        icon="mdi:timer-lock-open-outline"
    ),
    LeoNtpSensorDescription(
        key="gps_flags",
        icon="mdi:file-certificate-outline"
    ),
    LeoNtpSensorDescription(
        key="satellites",
        icon="mdi:satellite-uplink"
    ),
    LeoNtpSensorDescription(
        key="firmware_version",
        icon="mdi:tag"
    ),
    LeoNtpSensorDescription(
        key="serial_number",
        icon="mdi:tag-text"
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the LeoNTP sensors."""
    log_debug("[sensor|async_setup_entry|async_add_entities|start]")
    coordinator: LeoNtpDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[LeoNtpSensor] = []

    SUPPORTED_KEYS = {
        description.key: description for description in SENSOR_DESCRIPTIONS
    }

    # log_debug(f"[sensor|async_setup_entry|async_add_entities|SUPPORTED_KEYS] {SUPPORTED_KEYS}")

    if coordinator.data is not None:
        for item in coordinator.data:
            item = coordinator.data[item]

            if description := SUPPORTED_KEYS.get(item.type):
                if item.native_unit_of_measurement is not None:
                    native_unit_of_measurement = item.native_unit_of_measurement
                else:
                    native_unit_of_measurement = description.native_unit_of_measurement

                sensor_description = LeoNtpSensorDescription(
                    key=str(item.key),
                    name=item.name,
                    value_fn=description.value_fn,
                    native_unit_of_measurement=native_unit_of_measurement,
                    icon=description.icon,
                    translation_key=description.translation_key,
                )

                log_debug(f"[sensor|async_setup_entry|adding] {item.name}")
                entities.append(
                    LeoNtpSensor(
                        coordinator=coordinator,
                        description=sensor_description,
                        item=item,
                    )
                )
            else:
                log_debug(
                    f"[sensor|async_setup_entry|no support type found] {item.name}, type: {item.type}, keys: {SUPPORTED_KEYS.get(item.type)}",
                    True,
                )

        async_add_entities(entities)


class LeoNtpSensor(LeoNtpEntity, SensorEntity):
    """Representation of a LeoNTP sensor."""

    entity_description: LeoNtpSensorDescription

    def __init__(
        self,
        coordinator: LeoNtpDataUpdateCoordinator,
        description: EntityDescription,
        item: LeoNtpItem,
    ) -> None:
        """Set entity ID."""
        super().__init__(coordinator, description, item)
        self.entity_id = f"sensor.{DOMAIN}_{self.item.key}"

    @property
    def native_value(self) -> str:
        """Return the status of the sensor."""
        state = self.item.state

        if self.entity_description.value_fn:
            return self.entity_description.value_fn(state)

        return state

    @property
    def translation_key(self) -> str | None:
        """Set the translation key for the sensor."""
        if self.entity_description.translation_key:
            return self.entity_description.translation_key

        return None

    @property
    def extra_state_attributes(self):
        """Return attributes for sensor."""
        if not self.coordinator.data:
            return {}

        attributes = {
            "last_synced": self.last_synced,
        }

        if len(self.item.extra_attributes) > 0:
            for attr in self.item.extra_attributes:
                attributes[attr] = self.item.extra_attributes[attr]

        return attributes
