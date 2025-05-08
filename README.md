# Polen Madrid - Home Assistant Custom Component

[![GitHub Release][releases-shield]][releases]
[![License][license-shield]][license]

Integrates pollen level data from the Comunidad de Madrid with Home Assistant.

This component fetches pollen data for various stations and pollen types provided by the [Comunidad de Madrid: Polen y Salud](https://www.comunidad.madrid/servicios/salud/polen) and creates sensors for each combination in Home Assistant.

## Installation

1.  **Ensure Home Assistant is up to date.** (This component is developed against recent versions).
2.  **Copy the Component Files:**
    *   Copy the `custom_components/polen_madrid` directory (containing `__init__.py`, `sensor.py`, `const.py`, `manifest.json`, and `config_flow.py`) into your Home Assistant configuration's `custom_components` directory.
    *   If you don't have a `custom_components` directory in your Home Assistant configuration folder, create it.
3.  **Restart Home Assistant:**
    *   Restart your Home Assistant instance to allow it to pick up the new component.

## Configuration

This integration can be configured through the UI:

Once the YAML entry has been processed (or if you remove the YAML entry after the first setup), you can manage the integration via the UI.

*   Go to **Settings > Devices & Services**.
*   Click **+ ADD INTEGRATION**.
*   Search for "Polen Madrid" and follow the on-screen instructions (currently, no configuration options are presented, it will add directly).

If you added via YAML, an instance should already appear here.

## Sensors

The integration will create multiple sensor entities, one for each pollen type at each measurement station. For example:

*   `sensor.polen_arganzuela_gramineas`
*   `sensor.polen_coslada_platanus`

Each sensor will have a state representing the pollen value (typically in grains/m³) and will include additional attributes such as:

*   Pollen type
*   Location name
*   Pollen level (Bajo, Medio, Alto)
*   Pollen level text (e.g., "Alto (>= 50)")
*   Measurement date
*   Thresholds (medium, high, very_high)
*   Station ID and code
*   Coordinates (UTM)
*   Altitude
*   Sensor height

## Development

*   **Data Update Interval**: Data is fetched every hour by default (defined by `SCAN_INTERVAL` in `sensor.py`).

## Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the `LICENSE.md` file for details.

<!-- Shield Definitions -->
[releases]: https://github.com/alvarotanarro/polen-madrid/releases
[license]: https://github.com/alvarotanarro/polen-madrid/blob/main/LICENSE.md

[releases-shield]: https://img.shields.io/github/release/alvarotanarro/polen-madrid.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/alvarotanarro/polen-madrid.svg?style=for-the-badge 