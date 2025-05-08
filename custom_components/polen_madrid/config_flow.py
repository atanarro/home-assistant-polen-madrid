"""Config flow for Polen Madrid."""
import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class PolenMadridConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Polen Madrid."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        # This integration does not require any user configuration.
        # If it's already configured (e.g., from YAML or a previous user step), abort.
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        # If the user submits the (empty) form, create the config entry.
        if user_input is not None:
            _LOGGER.debug("Creating config entry from user step")
            return self.async_create_entry(title="Polen Madrid", data={})

        # Show an empty form to the user to confirm adding the integration.
        _LOGGER.debug("Showing user form for Polen Madrid")
        return self.async_show_form(step_id="user", data_schema=vol.Schema({}))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        # This integration has no options, so we return a simple options flow.
        # If you wanted options, you would define a class here.
        return PolenMadridOptionsFlowHandler(config_entry)

    async def async_step_import(self, import_config=None):
        """Handle a flow initialized by import from configuration.yaml."""
        _LOGGER.debug(f"Starting import step for Polen Madrid with config: {import_config}")
        # Check if an instance is already configured
        if self._async_current_entries():
            _LOGGER.debug("Polen Madrid already configured, aborting import.")
            return self.async_abort(reason="single_instance_allowed")
        
        _LOGGER.debug("Creating config entry for Polen Madrid from YAML import.")
        # Data is empty as this integration takes no config from YAML directly for the entry
        return self.async_create_entry(title="Polen Madrid (YAML)", data={})


class PolenMadridOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle an options flow for Polen Madrid."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        # This integration has no options, so we just show a form
        # and if submitted, create an empty options entry.
        if user_input is not None:
            return self.async_create_entry(title="", data={})

        return self.async_show_form(step_id="init", data_schema=vol.Schema({})) 