"""The Polen Madrid integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# List of platforms to support. There is only one platform (sensor) in this case.
PLATFORMS: list[Platform] = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Polen Madrid from a config entry."""
    # Initial data is stored in entry.data (from async_step_user)
    # Options are stored in entry.options (from options flow)
    # The sensor platform will read from entry.options or entry.data for selected stations.

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Add an options listener to reload the entry when options change.
    entry.add_update_listener(async_options_update_listener)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Home Assistant automatically removes listeners associated with the entry upon unload.
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

async def async_options_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    _LOGGER.debug(f"Polen Madrid options updated for entry {entry.entry_id}, reloading integration.")
    await hass.config_entries.async_reload(entry.entry_id) 