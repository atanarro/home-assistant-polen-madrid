"""Tests for the Polen Madrid config flow."""

from unittest.mock import patch

import pytest
from homeassistant import config_entries, data_entry_flow
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.polen_madrid.const import DOMAIN, CONF_STATIONS

# TODO: Add more comprehensive tests, mocking API responses and user
# interactions


async def test_user_flow_minimum_fields(hass: HomeAssistant, mock_requests_post) -> None:
    """Test the user config flow with minimum fields."""
    # The mock_requests_post fixture will mock the call in _fetch_stations
    # Ensure MOCK_RAW_API_RESPONSE in conftest.py provides data
    # _fetch_stations can parse

    # Initialize the config flow
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    # Since the mock provides data, we should get the form
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"
    assert not result.get("errors")

    # Check that the mock was called by _fetch_stations
    mock_requests_post.assert_called_once()

    # Simulate user input
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_STATIONS: ["28079016"],  # Example station ID
        },
    )
    await hass.async_block_till_done()

    # Should create the entry
    assert result2["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    # Default name or based on config
    assert result2["title"] == "Polen Madrid"
    assert result2["data"] == {
        CONF_STATIONS: ["28079016"],
    }
    # Check entry is actually added
    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1
    assert entries[0].data == {CONF_STATIONS: ["28079016"]}


# Example of how to test options flow if implemented
# async def test_options_flow(hass: HomeAssistant) -> None:
#     """Test the options flow."""
#     entry = MockConfigEntry(
#         domain=DOMAIN,
#         data={CONF_STATIONS: ["28079016"]},
#         title="Polen Madrid Test",
#     )
#     entry.add_to_hass(hass)

#     await hass.config_entries.async_setup(entry.entry_id)
#     await hass.async_block_till_done()

#     result = await hass.config_entries.options.async_init(entry.entry_id)

#     assert result["type"] == data_entry_flow.FlowResultType.FORM
#     assert result["step_id"] == "init"

#     # Simulate user input for options
#     result2 = await hass.config_entries.options.async_configure(
#         result["flow_id"],
#         user_input={
#             CONF_STATIONS: ["28079016", "28001001"], # Example change
#         },
#     )

#     assert result2["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
#     assert entry.options == {
#         CONF_STATIONS: ["28079016", "28001001"],
#     }

# Add more tests for different scenarios:
# - No stations selected
# - Invalid input
# - API errors during validation (if applicable)
# - Re-authentication flow (if applicable)
