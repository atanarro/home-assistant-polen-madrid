# Polen Madrid - Home Assistant Integration

This Home Assistant custom integration retrieves pollen levels for various monitoring stations in the Community of Madrid, Spain.

Data is sourced from the [Polen | Comunidad de Madrid](https://www.comunidad.madrid/servicios/salud/polen).

## Features

*   Provides sensor entities for pollen levels (value and type) for user-selected monitoring stations.
*   Each station's sensors are grouped as a device in Home Assistant.
*   Attributes include pollen level (Bajo, Medio, Alto), measurement date, thresholds, and station details.
*   Configurable via the Home Assistant UI (no YAML configuration required).

## Installation

1.  **HACS (Recommended):**
    *   Ensure you have [HACS (Home Assistant Community Store)](https://hacs.xyz/) installed.
    *   In HACS, go to **Integrations**.
    *   Click the three dots in the top right and select **Custom repositories**.
    *   In the "Repository" field, enter the URL of this GitHub repository: `https://github.com/atanarro/home-assistant-polen-madrid`
    *   Select "Integration" as the category.
    *   Click **ADD**.
    *   Find the "Polen Madrid" integration in the HACS list and click **INSTALL**.
    *   Follow the prompts to install the integration.

2.  **Manual Installation:**
    *   Copy the `custom_components/polen_madrid` directory into your Home Assistant configuration's `custom_components` directory.
    *   If you don't have a `custom_components` directory, create it.
2.  **Restart Home Assistant:**
    *   Restart your Home Assistant instance to allow it to pick up the new integration.

## Configuration

1.  **Add Integration:**
    *   In Home Assistant, go to **Settings** -> **Devices & Services**.
    *   Click the **+ ADD INTEGRATION** button in the bottom right corner.
    *   Search for "Polen Madrid" and select it.

2.  **Select Stations:**
    *   You will be presented with a list of available pollen monitoring stations.
    *   Select the stations you wish to monitor.
    *   Click **SUBMIT**.

3.  **View Entities:**
    *   The integration will create sensor entities for each selected station and pollen type.
    *   These can be found in your entity list and added to dashboards.

## Options

After initial setup, you can change the selected stations:

1.  Go to **Settings** -> **Devices & Services**.
2.  Find the "Polen Madrid" integration card.
3.  Click on **CONFIGURE**.
4.  Adjust your station selection and click **SUBMIT**.

## Troubleshooting

*   Ensure you have the latest version of the integration.
*   Check the Home Assistant logs (Settings -> System -> Logs) for any errors related to `polen_madrid`.
*   If you encounter issues, please [open an issue](https://github.com/atanarro/home-assistant-polen-madrid/issues) on GitHub.

## Example Lovelace UI Gauge

Here's an example of how you can display a pollen sensor using a Lovelace gauge card:

```yaml
type: gauge
entity: sensor.polen_madrid_arganzuela_gramineas # Replace with your specific sensor
name: Gramíneas Arganzuela
unit: 'g/m³'
min: 0
max: 75 # Adjust as needed, consider very_high_threshold if available
severity:
  green: 0
  yellow: 26 # Corresponds to medium_threshold from sensor attributes
  red: 53    # Corresponds to high_threshold from sensor attributes
needle: true # Optional
```

Replace `sensor.polen_madrid_arganzuela_gramineas` with the actual entity ID of the sensor you want to display. The `medium_threshold` and `high_threshold` values in the `severity` section should ideally match the attributes of your specific sensor for accurate color representation.
