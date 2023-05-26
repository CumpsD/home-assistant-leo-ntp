"""LeoNTP integration."""
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .client import LeoNtpClient
from .const import _LOGGER
from .const import CONF_UPDATE_INTERVAL
from .const import DEFAULT_UPDATE_INTERVAL
from .const import DOMAIN
from .const import PLATFORMS
from .models import LeoNtpItem

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Robonect from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    client = LeoNtpClient(
        host=entry.data[CONF_HOST],
        update_interval=entry.data[CONF_UPDATE_INTERVAL]
        if CONF_UPDATE_INTERVAL in entry.data
        else DEFAULT_UPDATE_INTERVAL,
    )

    dev_reg = dr.async_get(hass)

    hass.data[DOMAIN][entry.entry_id] = coordinator = LeoNtpDataUpdateCoordinator(
        hass,
        config_entry_id=entry.entry_id,
        dev_reg=dev_reg,
        client=client,
    )

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class LeoNtpDataUpdateCoordinator(DataUpdateCoordinator):
    """Data update coordinator for LeoNTP."""

    data: list[LeoNtpItem]
    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry_id: str,
        dev_reg: dr.DeviceRegistry,
        client: LeoNtpClient,
    ) -> None:
        """Initialize coordinator."""
        self._config_entry_id = config_entry_id
        self._device_registry = dev_reg
        self.client = client
        self.hass = hass
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=self.client.update_interval),
        )
