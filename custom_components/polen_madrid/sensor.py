from __future__ import annotations

"""Sensor platform for Polen Madrid integration."""
import logging
import json

import requests # This will be made async later
# import voluptuous as vol # Unused import
from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
# from homeassistant.helpers import config_validation as cv # Unused import

from .const import (
    DOMAIN,
    API_URL,
    API_HEADERS,
    API_DATA_PAYLOAD,
    FIELD_MAPPING,
    SCAN_INTERVAL,
    CONF_STATIONS,
)

_LOGGER = logging.getLogger(__name__)

# Helper function from download_script.py
def parse_api_response(json_data):
    """Parse the raw JSON data from the API into a structured list of records."""
    features = json_data.get('features', [])
    transformed_data = []
    for feature in features:
        properties = feature.get('properties', {})
        geometry = feature.get('geometry', {})
        coordinates = geometry.get('coordinates', [None, None])

        output_record = {}
        for source_field, target_field in FIELD_MAPPING.items():
            if target_field == "coordinates_utm":
                if coordinates and coordinates[0] is not None and coordinates[1] is not None:
                    output_record[target_field] = f"{coordinates[0]},{coordinates[1]}"
                else:
                    output_record[target_field] = None
            elif source_field in properties:
                output_record[target_field] = properties[source_field]
            else:
                output_record[target_field] = None
        transformed_data.append(output_record)
    transformed_data.sort(key=lambda x: (x.get('station_id'), x.get('pollen_code')))
    return transformed_data

# Helper function from render_pollen_table.py
def fix_encoding_issue(text):
    """Fix potential encoding issues for text strings from the API."""
    if isinstance(text, str):
        try:
            return text.encode('latin-1').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            return text
    return text

# Helper function from render_pollen_table.py
def get_pollen_level_details(value, medium_threshold, high_threshold):
    """Determine pollen level (Bajo, Medio, Alto) and descriptive text based on value and thresholds."""
    try:
        value = int(value)
        medium_threshold = int(medium_threshold if medium_threshold is not None else 0)
        high_threshold = int(high_threshold if high_threshold is not None else 0)
    except (ValueError, TypeError):
        _LOGGER.warning(
            "Invalid threshold or value for get_pollen_level: val=%s, med=%s, high=%s",
            value,
            medium_threshold,
            high_threshold,
        )
        return "Unknown", "Data N/A", "level-unknown"

    if high_threshold > 0 and value >= high_threshold:
        return "Alto", f"Alto (>= {high_threshold})", "level-alto"
    if medium_threshold > 0 and value >= medium_threshold:
        return "Medio", f"Medio (>= {medium_threshold})", "level-medio"

    threshold_text = f"< {medium_threshold}" if medium_threshold > 0 else ""
    return "Bajo", f"Bajo ({threshold_text})", "level-bajo"

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Polen Madrid sensors from a config entry."""
    _LOGGER.debug("Setting up Polen Madrid sensor platform.")
    
    # Get selected stations from config entry options or data
    selected_stations = entry.options.get(CONF_STATIONS, entry.data.get(CONF_STATIONS))
    if selected_stations is None: # Ensure it's a list if not found or explicitly None
        selected_stations = []

    _LOGGER.debug("Configured stations for Polen Madrid: %s", selected_stations)
    
    if not selected_stations:
        _LOGGER.warning(
            "No stations configured for Polen Madrid. No sensors will be created. "
            "Please configure stations in the integration options."
        )
        async_add_entities([])
        return

    coordinator = PolenMadridDataUpdateCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()
    _LOGGER.debug(
        "Coordinator data after first refresh: %s records",
        len(coordinator.data) if coordinator.data else 0
    )

    sensors = []
    if coordinator.data:
        _LOGGER.debug(
            "Coordinator.data is available. Processing %s records for selected stations.",
            len(coordinator.data)
        )
        for _, record in coordinator.data.items():
            station_id = record.get('station_id')
            
            # Filter by selected stations
            # Ensure station_id is string for comparison, as selected_stations contains strings
            if str(station_id) not in selected_stations:
                continue

            pollen_code = record.get('pollen_code')
            location_name = record.get('location_name')
            pollen_type = record.get('pollen_type')

            if station_id and pollen_code and location_name and pollen_type:
                _LOGGER.debug(
                    "Creating sensor for selected station: %s - %s (ID: %s, Code: %s)",
                    location_name, pollen_type, station_id, pollen_code
                )
                sensors.append(
                    PolenMadridSensor(coordinator, station_id, pollen_code, location_name, pollen_type)
                )
            else:
                _LOGGER.warning(
                    "Skipping sensor creation due to missing key fields in record for station %s: %s",
                    station_id, record
                )
    else:
        _LOGGER.warning(
            "Coordinator.data is None or empty after refresh. No sensors will be created."
        )

    if sensors:
        _LOGGER.info(
            "Adding %s Polen Madrid sensors to Home Assistant for the selected stations.",
            len(sensors)
        )
    else:
        _LOGGER.warning("No Polen Madrid sensors were created to add for the selected stations.")

    async_add_entities(sensors)
    _LOGGER.debug("Finished setting up Polen Madrid sensor platform for selected stations.")

class PolenMadridDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Polen Madrid data."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize."""
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        _LOGGER.debug("Attempting to fetch data from API.")
        try:
            # Define a helper function to pass to async_add_executor_job
            def _blocking_post_request():
                return requests.post(API_URL, headers=API_HEADERS, data=API_DATA_PAYLOAD, timeout=10)

            # Use hass.async_add_executor_job to run the blocking request
            response = await self.hass.async_add_executor_job(_blocking_post_request)

            response.raise_for_status()
            json_data = response.json()
            _LOGGER.debug(
                "Successfully fetched data, raw JSON keys: %s",
                list(json_data.keys()) if isinstance(json_data, dict) else 'Not a dict'
            )
            
            parsed_data = parse_api_response(json_data)
            _LOGGER.debug("Parsed_data count: %s", len(parsed_data))
            
            # Apply encoding fix
            processed_data = []
            for item in parsed_data:
                fixed_item = item.copy()
                if 'location_name' in fixed_item and fixed_item['location_name']:
                    fixed_item['location_name'] = fix_encoding_issue(fixed_item['location_name'])
                if 'pollen_type' in fixed_item and fixed_item['pollen_type']:
                    fixed_item['pollen_type'] = fix_encoding_issue(fixed_item['pollen_type'])
                processed_data.append(fixed_item)
            _LOGGER.debug(
                "Processed_data (after encoding fix) count: %s", len(processed_data)
            )

            # Organize data for sensors
            final_data_structure = {}
            for record in processed_data:
                station_id = record.get('station_id')
                pollen_code = record.get('pollen_code')
                if station_id and pollen_code:
                    final_data_structure[(station_id, pollen_code)] = record
            
            if not final_data_structure:
                _LOGGER.warning("No data in final_data_structure after processing.")
                return {}

            _LOGGER.debug(
                "Final_data_structure populated with %s entries.", len(final_data_structure)
            )
            return final_data_structure
            
        except requests.exceptions.HTTPError as errh:
            _LOGGER.error("Http Error: %s", errh)
            raise UpdateFailed(f"Error communicating with API: {errh}") from errh
        except requests.exceptions.ConnectionError as errc:
            _LOGGER.error("Error Connecting: %s", errc)
            raise UpdateFailed(f"Error connecting to API: {errc}") from errc
        except requests.exceptions.Timeout as errt:
            _LOGGER.error("Timeout Error: %s", errt)
            raise UpdateFailed(f"Timeout connecting to API: {errt}") from errt
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Request Error: %s", err)
            raise UpdateFailed(f"An unexpected error occurred with the request: {err}") from err
        except json.JSONDecodeError as j_err:
            _LOGGER.error("Failed to decode JSON response: %s", j_err)
            _LOGGER.debug(
                "Response text that failed to parse: %s",
                response.text if 'response' in locals() else 'Response object not available'
            )
            raise UpdateFailed(f"Invalid JSON response from API: {j_err}") from j_err
        except Exception as e:
            _LOGGER.exception("Unexpected error fetching pollen data: %s", e)
            raise UpdateFailed(f"Unexpected error: {e}") from e

class PolenMadridSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Polen Madrid Sensor."""

    def __init__(self, coordinator: PolenMadridDataUpdateCoordinator, station_id: str, pollen_code: str, location_name: str, pollen_type: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._station_id = station_id
        self._pollen_code = pollen_code
        self._location_name = location_name # Expected to be fixed encoding
        self._pollen_type = pollen_type     # Expected to be fixed encoding

        # Use fixed names for unique_id and name to avoid issues if encoding changes them slightly
        # But display names can use the (hopefully) corrected versions.
        self._attr_unique_id = f"{DOMAIN}_{self._station_id}_{self._pollen_code}"
        self._attr_name = f"Polen {self._location_name} - {self._pollen_type}"
        
        # Device info: Group sensors by physical location (station)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._station_id)},
            "name": f"Estación Polen {self._location_name}",
            "manufacturer": "Comunidad de Madrid",
            "model": "Sensor de Polen",
            # "sw_version": ... , # Could add if available
            # "via_device": (DOMAIN, "cloud_service"), # If we had a central device for the API itself
        }

    @property
    def _record(self):
        """Helper to get the specific record for this sensor from coordinator data."""
        if self.coordinator.data:
            return self.coordinator.data.get((self._station_id, self._pollen_code))
        return None

    @property
    def native_value(self):
        """Return the state of the sensor (pollen value)."""
        if self._record:
            return self._record.get('pollen_value')
        return None

    @property
    def unit_of_measurement(self) -> str | None:
        """Return the unit of measurement."""
        return "g/m³" # grains per cubic meter

    @property
    def state_class(self) -> SensorStateClass | None:
        return SensorStateClass.MEASUREMENT

    @property
    def extra_state_attributes(self):
        """Return other attributes of the sensor."""
        if not self._record:
            return {}

        attrs = {}
        value = self._record.get('pollen_value')
        medium_threshold = self._record.get('medium_threshold')
        high_threshold = self._record.get('high_threshold')

        level_name, level_text, _ = get_pollen_level_details(value, medium_threshold, high_threshold)

        attrs['pollen_type'] = self._pollen_type
        attrs['location_name'] = self._location_name
        attrs['pollen_level'] = level_name
        attrs['pollen_level_text'] = level_text
        attrs['pollen_value'] = value
        attrs['medium_threshold'] = medium_threshold
        attrs['high_threshold'] = high_threshold
        # commented as it is always 0
        # attrs['very_high_threshold'] = self._record.get('very_high_threshold')
        attrs['measurement_date'] = self._record.get('measurement_date')
        attrs['station_code'] = self._record.get('station_code')
        attrs['station_id'] = self._station_id
        attrs['pollen_code'] = self._pollen_code
        attrs['coordinates_utm'] = self._record.get('coordinates_utm')
        attrs['altitude'] = self._record.get('altitude')
        attrs['sensor_height'] = self._record.get('sensor_height')
        
        return attrs

    @property
    def available(self) -> bool:
        """Return True if entity is available (data is present in coordinator and record exists)."""
        return super().available and self._record is not None 