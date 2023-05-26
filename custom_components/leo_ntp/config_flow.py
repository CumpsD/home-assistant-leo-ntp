"""Config flow to configure the LeoNTP integration."""
from abc import ABC
from abc import abstractmethod
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.config_entries import ConfigFlow
from homeassistant.config_entries import OptionsFlow

from homeassistant.const import CONF_HOST

from homeassistant.core import callback

from homeassistant.data_entry_flow import FlowHandler
from homeassistant.data_entry_flow import FlowResult

from homeassistant.helpers.selector import NumberSelector
from homeassistant.helpers.selector import NumberSelectorConfig
from homeassistant.helpers.selector import NumberSelectorMode

from homeassistant.helpers.selector import TextSelector
from homeassistant.helpers.selector import TextSelectorConfig
from homeassistant.helpers.selector import TextSelectorType

from homeassistant.helpers.typing import UNDEFINED

from .client import LeoNtpClient

from .const import CONF_UPDATE_INTERVAL
from .const import DEFAULT_UPDATE_INTERVAL
from .const import DOMAIN
from .const import NAME

from .exceptions import LeoNtpServiceException

from .models import LeoNtpConfigEntryData

from .utils import log_debug

DEFAULT_ENTRY_DATA = LeoNtpConfigEntryData(
    host = None,
    update_interval = DEFAULT_UPDATE_INTERVAL,
)

class LeoNtpCommonFlow(ABC, FlowHandler):
    """Base class for LeoNTP flows."""

    def __init__(self, initial_data: LeoNtpConfigEntryData) -> None:
        """Initialize LeoNtpCommonFlow."""
        self.initial_data = initial_data
        self.new_entry_data = LeoNtpConfigEntryData()
        self.new_title: str | None = None

    @abstractmethod
    def finish_flow(self) -> FlowResult:
        """Finish the flow."""

    def new_data(self):
        """Construct new data."""
        return DEFAULT_ENTRY_DATA | self.initial_data | self.new_entry_data

    async def async_validate_input(self, user_input: dict[str, Any]) -> None:
        """Validate server configuration."""

        client = LeoNtpClient(
            host = user_input[CONF_HOST],
            update_interval = user_input[CONF_UPDATE_INTERVAL],
        )

        return await self.hass.async_add_executor_job(client.validate_server)

    async def async_step_connection_init(
        self, user_input: dict | None = None
    ) -> FlowResult:
        """Handle connection configuration."""
        errors: dict = {}

        if user_input is not None:
            user_input = self.new_data() | user_input
            test = await self.test_connection(user_input)
            log_debug(f"[config_flow|async_step_connection_init] test_connection: {test}")

            if not test["errors"]:
                self.new_title = test["device"].get("name")
                self.new_entry_data |= user_input
                await self.async_set_unique_id(f"{DOMAIN}_" + test["device"].get("id"))

                self._abort_if_unique_id_configured()
                log_debug(f"New server {self.new_title} added")
                return self.finish_flow()

            errors = test["errors"]

        fields = {
            vol.Required(CONF_HOST): TextSelector(
                TextSelectorConfig(type = TextSelectorType.TEXT, autocomplete = "host")
            ),
            vol.Required(CONF_UPDATE_INTERVAL, default = DEFAULT_UPDATE_INTERVAL): NumberSelector(
                NumberSelectorConfig(min = 1, max = 3600, step = 1, mode = NumberSelectorMode.BOX)
            ),
        }

        return self.async_show_form(
            step_id = "connection_init",
            data_schema = vol.Schema(fields),
            errors = errors,
        )

    async def test_connection(self, user_input: dict | None = None) -> dict:
        """Test the connection to LeoNTP."""
        errors: dict = {}
        device: dict = {}

        if user_input is not None:
            user_input = self.new_data() | user_input

            try:
                device = await self.async_validate_input(user_input)
            except AssertionError as exception:
                errors["base"] = "cannot_connect"
                log_debug(f"[config_flow|test_connection] AssertionError {exception}")
            except ConnectionError as error:
                errors["base"] = "cannot_connect"
                log_debug(f"[config_flow|test_connection] ConnectionError {error}")
            except LeoNtpServiceException as exception:
                errors["base"] = "service_error"
                log_debug(f"[config_flow|test_connection] LeoNtpServiceException {exception}")
            except Exception as exception:
                errors["base"] = "unknown"
                log_debug(f"[config_flow|test_connection] Exception {exception}")

        return {"device": device, "errors": errors}

    async def async_step_host(self, user_input: dict | None = None) -> FlowResult:
        """Configure host."""
        errors: dict = {}

        if user_input is not None:
            user_input = self.new_data() | user_input
            test = await self.test_connection(user_input)

            if not test["errors"]:
                self.new_entry_data |= LeoNtpConfigEntryData(
                    host = user_input[CONF_HOST],
                )
                return self.finish_flow()

        fields = {
            vol.Required(CONF_HOST): TextSelector(
                TextSelectorConfig(type = TextSelectorType.TEXT, autocomplete = "host")
            ),
        }

        return self.async_show_form(
            step_id = "host",
            data_schema = self.add_suggested_values_to_schema(
                vol.Schema(fields),
                self.initial_data,
            ),
            errors = errors,
        )

    async def async_step_update_interval(self, user_input: dict | None = None) -> FlowResult:
        """Configure update interval."""
        errors: dict = {}

        if user_input is not None:
            self.new_entry_data |= user_input
            return self.finish_flow()

        fields = {
            vol.Required(CONF_UPDATE_INTERVAL): NumberSelector(
                NumberSelectorConfig(min = 1, max = 3600, step = 1, mode = NumberSelectorMode.BOX)
            ),
        }
        return self.async_show_form(
            step_id = "update_interval",
            data_schema = self.add_suggested_values_to_schema(
                vol.Schema(fields),
                self.initial_data,
            ),
            errors = errors,
        )


class LeoNtpOptionsFlow(LeoNtpCommonFlow, OptionsFlow):
    """Handle LeoNTP options."""

    general_settings: dict

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize LeoNTP options flow."""
        self.config_entry = config_entry
        super().__init__(initial_data = config_entry.data)  # type: ignore[arg-type]

    @callback
    def finish_flow(self) -> FlowResult:
        """Update the ConfigEntry and finish the flow."""
        new_data = DEFAULT_ENTRY_DATA | self.initial_data | self.new_entry_data

        self.hass.config_entries.async_update_entry(
            self.config_entry,
            data = new_data,
            title = self.new_title or UNDEFINED,
        )

        self.hass.async_create_task(
            self.hass.config_entries.async_reload(self.config_entry.entry_id)
        )

        return self.async_create_entry(title = "", data = {})

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage LeoNTP options."""

        return self.async_show_menu(
            step_id = "options_init",
            menu_options = [
                "host",
                "update_interval",
            ],
        )


class LeoNtpConfigFlow(LeoNtpCommonFlow, ConfigFlow, domain = DOMAIN):
    """Handle a config flow for LeoNTP."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize LeoNTP Config Flow."""
        super().__init__(initial_data = DEFAULT_ENTRY_DATA)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> LeoNtpOptionsFlow:
        """Get the options flow for this handler."""
        return LeoNtpOptionsFlow(config_entry)

    @callback
    def finish_flow(self) -> FlowResult:
        """Create the ConfigEntry."""
        title = self.new_title or NAME
        return self.async_create_entry(
            title = title,
            data = DEFAULT_ENTRY_DATA | self.new_entry_data,
        )

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Handle a flow initialized by the user."""
        return await self.async_step_connection_init()
