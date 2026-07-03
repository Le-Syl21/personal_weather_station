def normalize_battery(value, scale=None):
    if value is None:
        return None

    try:
        value = float(value)
    except (TypeError, ValueError):
        return None

    if scale:
        value = value / scale * 100

    return max(0, min(100, round(value)))