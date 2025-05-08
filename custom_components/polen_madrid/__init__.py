"""The Polen Madrid integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import DOMAIN

# Define an empty schema for the domain. This tells HA that `polen_madrid:` is valid in YAML.
CONFIG_SCHEMA = vol.Schema({DOMAIN: cv.deprecated(DOMAIN)}, extra=vol.ALLOW_EXTRA)


# List of platforms to support. There is only one platform (sensor) in this case.
PLATFORMS: list[Platform] = [Platform.SENSOR]

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Polen Madrid component from YAML configuration."""
    # Check if an entry for this domain already exists.
    # This prevents creating duplicate entries if already set up via UI (once we add config flow)
    # or if HA is restarted.
    if not hass.config_entries.async_entries(DOMAIN):
        # Create a new config entry.
        # We pass an empty dictionary for data and unique_id=DOMAIN as this integration
        # doesn't have specific configuration options from YAML for now.
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, context={"source": "import"}, data={}
            )
        )
    return True

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