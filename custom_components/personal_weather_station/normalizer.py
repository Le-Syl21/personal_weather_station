"""Value normalization helpers for incoming weather station payloads."""


def parse_value(raw):
    """
    Convert a raw query string value into a usable Python value.

    Weather stations send everything as text, and both supported protocols may
    send a parameter with an empty value when the matching sensor has nothing to
    report (the WSLink API example does this for "t1feels" and "t1heat").
    Returning None for those keeps Home Assistant happy: a numeric sensor simply
    becomes "unknown" instead of raising on a non numeric state.

    Args:
        raw: Raw value taken from the query string.

    Returns:
        int, float, str or None.
    """

    if raw is None:
        return None

    if not isinstance(raw, str):
        return raw

    raw = raw.strip()

    if not raw:
        return None

    try:
        return int(raw)
    except ValueError:
        pass

    try:
        return float(raw)
    except ValueError:
        return raw


def normalize_battery(value, scale=None):
    """
    Convert a raw battery reading to a percentage.

    Args:
        value: Raw battery value.
        scale: Full scale value as documented by the station API. 1 for the
            binary "Normal=1, Low battery=0" sensors, 5 for the 0~5 sensors.

    Returns:
        int between 0 and 100, or None when the value is unusable.
    """

    if value is None:
        return None

    try:
        value = float(value)
    except (TypeError, ValueError):
        return None

    if scale:
        value = value / scale * 100

    return max(0, min(100, round(value)))


def apply_wind_offset(value, offset):
    """
    Rotate a wind direction by the configured calibration offset.

    Args:
        value: Raw direction in degrees, as received from the station.
        offset: Calibration offset in degrees.

    Returns:
        The corrected direction in the 0-359 range, or the untouched value when
        it is not a number.
    """

    if not offset or value is None:
        return value

    try:
        return round((float(value) + offset) % 360, 1)
    except (TypeError, ValueError):
        return value
