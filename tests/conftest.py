import pytest
from unittest.mock import patch, MagicMock

# Define MOCK_API_DATA globally for tests needing API responses
# (Ensure structure matches what parse_api_response expects AFTER json decode)
MOCK_PARSED_DATA_STRUCTURE = {
    ("28079016", "PLT"): {
        'station_id': "28079016", 'pollen_code': "PLT",
        'location_name': "Madrid - Retiro", 'pollen_type': "Platanus",
        'pollen_value': 1, 'medium_threshold': 2, 'high_threshold': 3,
        # Add other required fields based on PolenMadridSensor usage
        'station_code': "STN-R", 'measurement_date': '2024-01-01T10:00:00Z',
        'coordinates_utm': 'coords', 'altitude': 600, 'sensor_height': 10
    },
    ("28079016", "CUP"): {
        'station_id': "28079016", 'pollen_code': "CUP",
        'location_name': "Madrid - Retiro", 'pollen_type': "Cupresáceas / Taxáceas",
        'pollen_value': 0, 'medium_threshold': 2, 'high_threshold': 3,
        'station_code': "STN-R", 'measurement_date': '2024-01-01T10:00:00Z',
        'coordinates_utm': 'coords', 'altitude': 600, 'sensor_height': 10
    },
    # Add data for Alcalá if needed for other tests
}

# Example raw API data that parse_api_response would process
MOCK_RAW_API_RESPONSE = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": None,
            "properties": {
                "NM_ID_CAPTADORES": "28079016", "CD_CAPTADORES": "STN-R",
                "DS_NOMBRE": "Madrid - Retiro",
                "NM_LONGITUD": 440598, "NM_LATITUD": 4474200, "NM_ALTITUD": 667,
                "NM_ALTURA": 10, "FC_FECHA_MEDICION": "2024-01-01T10:00:00Z",
                "NM_VALOR": 1, "CD_MATERIAS": "PLT", "DS_MATERIAS": "Platanus",
                "NM_ALTO": 3, "NM_MEDIO": 2, "NM_MUYALTO": 0
            }
        },
        {
            "type": "Feature",
            "geometry": None,
            "properties": {
                "NM_ID_CAPTADORES": "28079016", "CD_CAPTADORES": "STN-R",
                "DS_NOMBRE": "Madrid - Retiro",
                "NM_LONGITUD": 440598, "NM_LATITUD": 4474200, "NM_ALTITUD": 667,
                "NM_ALTURA": 10, "FC_FECHA_MEDICION": "2024-01-01T10:00:00Z",
                "NM_VALOR": 0, "CD_MATERIAS": "CUP", "DS_MATERIAS": "Cupresáceas / Taxáceas",
                "NM_ALTO": 3, "NM_MEDIO": 2, "NM_MUYALTO": 0
            }
        },
        # Add Alcalá feature if needed
    ]
}


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations defined in the custom_components directory."""
    yield


@pytest.fixture
def mock_requests_post():
    """Fixture to mock requests.post, returning RAW API data by default."""
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        # Default mock returns raw data structure parse_api_response expects
        mock_response.json.return_value = MOCK_RAW_API_RESPONSE
        mock_post.return_value = mock_response
        yield mock_post
