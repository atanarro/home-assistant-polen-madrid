"""The Polen Madrid integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import DOMAIN

# List of platforms to support. There is only one platform (sensor) in this case.
PLATFORMS: list[Platform] = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Polen Madrid from a config entry."""
    # The coordinator is created and refreshed in the sensor platform's async_setup_entry.
    # We rely on the sensor platform to raise ConfigEntryNotReady if it fails to initialize.
    # However, to be more explicit as per HA guidelines, if we were creating the
    # coordinator here, we would do:
    # coordinator = PolenMadridDataUpdateCoordinator(hass) # Assuming coordinator is defined or imported
    # await coordinator.async_config_entry_first_refresh()
    # if not coordinator.last_update_success:
    #     raise ConfigEntryNotReady
    # hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS) 