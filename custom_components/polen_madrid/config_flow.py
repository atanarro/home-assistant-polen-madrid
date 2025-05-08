"""Config flow for Polen Madrid."""
from __future__ import annotations

import json
import logging

import requests
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from requests.exceptions import RequestException

from .const import (
    API_DATA_PAYLOAD,
    API_HEADERS,
    API_URL,
    CONF_STATIONS,
    DOMAIN,
    FIELD_MAPPING,
)

_LOGGER = logging.getLogger(__name__)


def _fix_encoding_issue(text: str) -> str:
    """Fix encoding issues for text."""
    if isinstance(text, str):
        try:
            return text.encode('latin-1').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            return text
    return text


def _get_raw_key_for_value(value_to_find: str) -> str | None:
    for raw_key, mapped_value in FIELD_MAPPING.items():
        if mapped_value == value_to_find:
            return raw_key
    return None


RAW_STATION_ID_KEY = _get_raw_key_for_value("station_id")
RAW_STATION_NAME_KEY = _get_raw_key_for_value("location_name")


class PolenMadridConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Polen Madrid."""

    VERSION = 1

    async def _fetch_stations(self) -> dict[str, str] | None:
        """Fetch available stations from the API."""
        if not RAW_STATION_ID_KEY or not RAW_STATION_NAME_KEY:
            _LOGGER.error(
                "Raw keys for station ID or name could not be determined from FIELD_MAPPING."
            )
            return None

        def _blocking_fetch() -> dict[str, str] | None:
            try:
                response = requests.post(
                    API_URL, headers=API_HEADERS, data=API_DATA_PAYLOAD, timeout=10
                )
                response.raise_for_status()
                json_data = response.json()
                
                stations: dict[str, str] = {}
                features = json_data.get('features', [])
                for feature in features:
                    properties = feature.get('properties', {})
                    station_id = properties.get(RAW_STATION_ID_KEY)
                    station_name = properties.get(RAW_STATION_NAME_KEY)
                    if station_id and station_name:
                        fixed_name = _fix_encoding_issue(station_name)
                        # Ensure station_id is string for dict keys/HA select options
                        stations[str(station_id)] = fixed_name
                return stations
            except RequestException as e:
                _LOGGER.error("Error fetching stations for config flow: %s", e)
                return None
            except json.JSONDecodeError as e:
                _LOGGER.error("Error decoding stations JSON for config flow: %s", e)
                return None
            except Exception as e: # Catch any other unexpected errors
                _LOGGER.error("Unexpected error fetching stations: %s", e)
                return None

        return await self.hass.async_add_executor_job(_blocking_fetch)

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}

        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            if not user_input.get(CONF_STATIONS):
                errors["base"] = "no_stations_selected"
            else:
                _LOGGER.debug(
                    "Creating config entry with selected stations: %s", user_input[CONF_STATIONS]
                )
                return self.async_create_entry(title="Polen Madrid", data=user_input)

        # Fetch stations to show in the form
        stations = await self._fetch_stations()

        if stations is None: # Error during fetch
            errors["base"] = "fetch_stations_failed"
            # Show an empty form with an error, or abort. Aborting might be cleaner.
            # For now, show form with error message if we want user to retry.
            # Or, just abort if stations are critical for setup.
            # Let's allow showing the form with an error.
            _LOGGER.error("Failed to fetch stations for user configuration step.")
            # If we show a form, it won't have station options.
            # It's better to abort if we can't get stations
            return self.async_abort(reason="fetch_stations_failed")

        if not stations: # No stations returned, even if fetch was successful
            _LOGGER.warning("No stations found from API.")
            return self.async_abort(reason="no_stations_found")

        # Sort stations by name for better UX
        sorted_stations = dict(sorted(stations.items(), key=lambda item: item[1]))

        data_schema = vol.Schema({
            vol.Required(CONF_STATIONS): cv.multi_select(sorted_stations)
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "station_count": str(len(sorted_stations))
            } # Optional: for translations
        )

    @staticmethod
    @callback
    def async_get_options_flow(_config_entry: config_entries.ConfigEntry):
        """Get the options flow for this handler."""
        return PolenMadridOptionsFlowHandler(_config_entry)


class PolenMadridOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle an options flow for Polen Madrid."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self._stations: dict[str, str] | None = None # Cache fetched stations

    async def _fetch_stations_for_options(self) -> bool:
        """Fetch and cache stations for options flow. Returns True on success."""
        # For simplicity, directly using the structure of _fetch_stations from parent.
        if not RAW_STATION_ID_KEY or not RAW_STATION_NAME_KEY:
            _LOGGER.error(
                "Raw keys for station ID or name could not be determined from FIELD_MAPPING (options)."
            )
            return False

        def _blocking_fetch() -> dict[str, str] | None:
            try:
                response = requests.post(
                    API_URL, headers=API_HEADERS, data=API_DATA_PAYLOAD, timeout=10
                )
                response.raise_for_status()
                json_data = response.json()
                
                stations: dict[str, str] = {}
                features = json_data.get('features', [])
                for feature in features:
                    properties = feature.get('properties', {})
                    station_id = properties.get(RAW_STATION_ID_KEY)
                    station_name = properties.get(RAW_STATION_NAME_KEY)
                    if station_id and station_name:
                        fixed_name = _fix_encoding_issue(station_name)
                        stations[str(station_id)] = fixed_name
                return stations
            except RequestException as e:
                _LOGGER.error("Error fetching stations for options flow: %s", e)
                return None
            except json.JSONDecodeError as e:
                _LOGGER.error("Error decoding stations JSON for options flow: %s", e)
                return None
            except Exception as e:
                _LOGGER.error("Unexpected error fetching stations for options: %s", e)
                return None

        fetched_data = await self.hass.async_add_executor_job(_blocking_fetch)
        if fetched_data is not None:
            self._stations = dict(sorted(fetched_data.items(), key=lambda item: item[1]))
            return True
        return False

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            if not user_input.get(CONF_STATIONS): # Check if list is empty
                errors["base"] = "no_stations_selected_options" # A new error string
            else:
                _LOGGER.debug(
                    "Updating options with selected stations: %s", user_input[CONF_STATIONS]
                )
                return self.async_create_entry(title="", data=user_input)

        if self._stations is None: # Fetch only if not already fetched
            if not await self._fetch_stations_for_options():
                # Failed to fetch stations, show error and abort or allow retry.
                # For options, perhaps show current config and an error.
                # Aborting might be simplest if stations can't be loaded.
                return self.async_abort(reason="fetch_stations_failed_options")

        if not self._stations: # No stations available from API
            return self.async_abort(reason="no_stations_found_options")
            
        current_selection = self.config_entry.options.get(CONF_STATIONS, [])
        # Ensure current_selection items are strings, as station IDs are stored as strings
        current_selection = [str(s) for s in current_selection]

        options_schema = vol.Schema({
            vol.Required(
                CONF_STATIONS,
                default=current_selection
            ): cv.multi_select(self._stations)
        })

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            errors=errors
        )