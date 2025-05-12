"""The Polen Madrid integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.helpers.update_coordinator import ConfigEntryNotReady

from .const import DOMAIN, CONF_STATIONS
from .sensor import PolenMadridDataUpdateCoordinator # Import the coordinator

_LOGGER = logging.getLogger(__name__)

# List of platforms to support. There is only one platform (sensor) in this case.
PLATFORMS: list[Platform] = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Polen Madrid from a config entry."""
    # Initial data is stored in entry.data (from async_step_user)
    # Options are stored in entry.options (from options flow)
    # The sensor platform will read from entry.options or entry.data for selected stations.

    # Create and refresh the coordinator
    coordinator = PolenMadridDataUpdateCoordinator(hass)
    
    # Perform the first refresh. If this fails, ConfigEntryNotReady will be raised
    # and setup will be retried later. This prevents forwarding to platforms on failure.
    await coordinator.async_config_entry_first_refresh()
    
    # Store the coordinator instance in hass.data for platforms to use
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Now forward the setup to the sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Add an options listener to reload the entry when options change.
    entry.add_update_listener(async_options_update_listener)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Home Assistant automatically removes listeners associated with the entry upon unload.
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    # Remove the coordinator from hass.data if unload was successful
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        
    return unload_ok

async def async_options_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    _LOGGER.debug(
        "Polen Madrid options updated for entry %s, reloading integration.",
        entry.entry_id
    )
    await hass.config_entries.async_reload(entry.entry_id)
