"""LeoNTP integration."""
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed

from .client import LeoNtpClient
from .const import _LOGGER
from .const import CONF_UPDATE_INTERVAL
from .const import DEFAULT_UPDATE_INTERVAL
from .const import DOMAIN
from .const import PLATFORMS
from .exceptions import LeoNtpException
from .exceptions import LeoNtpServiceException
from .models import LeoNtpItem
from .utils import log_debug

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up LeoNTP from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    client = LeoNtpClient(
        host = entry.data[CONF_HOST],
        update_interva = entry.data[CONF_UPDATE_INTERVAL]
        if CONF_UPDATE_INTERVAL in entry.data
        else DEFAULT_UPDATE_INTERVAL,
    )

    dev_reg = dr.async_get(hass)

    hass.data[DOMAIN][entry.entry_id] = coordinator = LeoNtpDataUpdateCoordinator(
        hass,
        config_entry_id = entry.entry_id,
        dev_reg = dev_reg,
        client = client,
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
            name = DOMAIN,
            update_interval = timedelta(seconds = self.client.update_interval),
        )


    async def _async_update_data(self) -> dict | None:
        """Update data."""
        try:
            items = await self.hass.async_add_executor_job(self.client.fetch_data)
        except ConnectionError as exception:
            raise UpdateFailed(f"ConnectionError {exception}") from exception
        except LeoNtpServiceException as exception:
            raise UpdateFailed(f"LeoNtpServiceException {exception}") from exception
        except LeoNtpException as exception:
            raise UpdateFailed(f"LeoNtpException {exception}") from exception
        except Exception as exception:
            raise UpdateFailed(f"Exception {exception}") from exception

        items: list[LeoNtpItem] = items

        current_items = {
            list(device.identifiers)[0][1]
            for device in dr.async_entries_for_config_entry(
                self._device_registry, self._config_entry_id
            )
        }

        if len(items) > 0:
            fetched_items = {str(items[item].device_key) for item in items}

            log_debug(
                f"[init|LeoNtpDataUpdateCoordinator|_async_update_data|fetched_items] {fetched_items}"
            )

            if stale_items := current_items - fetched_items:
                for device_key in stale_items:
                    if device := self._device_registry.async_get_device(
                        {(DOMAIN, device_key)}
                    ):
                        log_debug(
                            f"[init|LeoNtpDataUpdateCoordinator|_async_update_data|async_remove_device] {device_key}",
                            True,
                        )
                        self._device_registry.async_remove_device(device.id)

            # If there are new items, we should reload the config entry so we can
            # create new devices and entities.
            if self.data and fetched_items - {
                str(self.data[item].device_key) for item in self.data
            }:
                # log_debug(f"[init|LeoNtpDataUpdateCoordinator|_async_update_data|async_reload] {product.product_name}", True)
                self.hass.async_create_task(
                    self.hass.config_entries.async_reload(self._config_entry_id)
                )
                return None
            return items
        return []
