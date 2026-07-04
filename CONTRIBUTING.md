# Contributing

First of all, thank you for considering contributing to **Personal Weather Station**!

Whether you want to report a bug, add support for a new weather station, improve the documentation, or submit code, your help is greatly appreciated.

## Reporting issues

Before opening an issue:

- Search existing issues to avoid duplicates.
- Use the appropriate issue template.
- Include as much information as possible:
  - Home Assistant version
  - Integration version
  - Weather station model
  - Firmware version (if known)
  - Example HTTP request or WSLink payload
  - Debug logs (if applicable)

## Adding support for new sensors

Most sensors are defined in:

```
custom_components/personal_weather_station/const.py
```

When adding a new sensor:

- Use the appropriate Home Assistant `device_class` and `state_class`.
- Use the correct unit of measurement.
- Follow the existing naming conventions.
- If the sensor represents a battery level, add a `battery_scale` when the raw value is not already expressed as a percentage.

Example:

```python
"t8bat": {
    "name": "PM Sensor Battery Level",
    "icon": "mdi:battery",
    "device_class": SensorDeviceClass.BATTERY,
    "state_class": SensorStateClass.MEASUREMENT,
    "precision": 0,
    "battery_scale": 5,
}
```

## Code style

Please try to keep the code consistent with the rest of the project:

- Follow PEP 8.
- Keep functions small and readable.
- Add comments only when they improve understanding.
- Prefer configuration-driven logic over hardcoded special cases.
- Keep backward compatibility whenever possible.

## Pull requests

Before submitting a pull request:

- Make sure the integration still loads correctly.
- Test with a real weather station whenever possible.
- Update the documentation if new features or sensors are added.
- Keep pull requests focused on a single feature or fix.

## New weather station models

If you successfully tested the integration with a new weather station, feel free to submit a pull request updating the README.

Please include:

- Manufacturer
- Model number
- Firmware version (if available)
- Whether it uses Weather Underground or WSLink mode

## Questions

If you're unsure about an implementation or want to discuss a feature before coding it, feel free to open a GitHub Discussion or Issue first.

Thank you for helping improve this integration!
