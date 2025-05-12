"""Tests for the Polen Madrid integration setup."""

from unittest.mock import patch, MagicMock

import pytest
import requests  # Import requests for patching
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
# Remove async_setup_component if only testing entry setup
# from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry
from homeassistant.helpers.update_coordinator import UpdateFailed  # Import UpdateFailed

from custom_components.polen_madrid.const import DOMAIN, CONF_STATIONS
# Import mock data if needed, or define simple mock structure
# from .test_sensor import MOCK_API_DATA # Remove relative import

# Define MOCK_API_DATA directly in this file - REMOVE THIS NOW, USE RAW DATA IN MOCK
# MOCK_API_DATA = {
#     "municipios": [
#         {
#             "codigo_municipio": "28079016",
#             "nombre_municipio": "Madrid - Retiro",
#             "polenes": [
#                 {"polen": "PLT", "nivel": 1, "nombre": "Platanus", "med": 2, "alt": 3 },
#                 {"polen": "CUP", "nivel": 0, "nombre": "Cupresáceas / Taxáceas", "med": 2, "alt": 3 },
#             ],
#         },
#         {
#             "codigo_municipio": "28001001",
#             "nombre_municipio": "Alcalá de Henares",
#             "polenes": [
#                 {"polen": "PLT", "nivel": 2, "nombre": "Platanus", "med": 2, "alt": 3 },
#             ],
#         }
#     ]
# }

# Mock the requests.post call - REMOVE THIS NOW, MOVED TO CONFTEST.PY
# @pytest.fixture
# def mock_requests_post():
#    ...


async def test_setup_entry(hass: HomeAssistant, mock_requests_post) -> None:
    """Test successful setup of the integration entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_STATIONS: ["28079016"]},
        title="Polen Madrid Test",
    )
    entry.add_to_hass(hass)

    # Use hass.config_entries.async_setup to setup the entry
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    # Check that the entry is loaded
    assert entry.state == ConfigEntryState.LOADED

    # Coordinator is managed by the sensor platform, not stored directly in hass.data[DOMAIN]
    # assert DOMAIN in hass.data
    # assert entry.entry_id in hass.data[DOMAIN]
    # assert "coordinator" in hass.data[DOMAIN][entry.entry_id]

    # Ensure requests.post was called by the coordinator's update
    mock_requests_post.assert_called_once()


async def test_unload_entry(hass: HomeAssistant, mock_requests_post) -> None:
    """Test successful unloading of the integration entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_STATIONS: ["28079016"]},
        title="Polen Madrid Test",
    )
    entry.add_to_hass(hass)

    # Setup the entry first
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state == ConfigEntryState.LOADED
    mock_requests_post.assert_called()  # Ensure setup called post

    # Unload the component
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    # Check that the entry is unloaded
    assert entry.state == ConfigEntryState.NOT_LOADED

    # hass.data check is removed as it's not applicable here
    # assert entry.entry_id not in hass.data.get(DOMAIN, {})


async def test_setup_entry_fails_api_error(hass: HomeAssistant) -> None:
    """Test setup failure when the initial API call fails."""
    # Note: This test doesn't use mock_requests_post fixture,
    # as we patch the coordinator method directly.
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_STATIONS: ["28079016"]},
        title="Polen Madrid Test",
    )
    entry.add_to_hass(hass)

    # Patch the coordinator's update method directly to raise UpdateFailed
    with patch(
        "custom_components.polen_madrid.sensor.PolenMadridDataUpdateCoordinator._async_update_data",
        side_effect=UpdateFailed("Simulated API Error"),
    ):
        # Run setup. We expect ConfigEntryNotReady to be raised internally by
        # first_refresh.
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    # Check that the entry state is SETUP_RETRY (standard behavior for
    # ConfigEntryNotReady)
    assert entry.state == ConfigEntryState.SETUP_RETRY

    # We didn't use the requests mock here, so no need to assert calls on it.
    # mock_requests_post.assert_called_once()


# TODO:
# - Add tests for specific platform forwarding if logic exists in __init__.py
# - Test migration logic if versioning is implemented in config flow
