"""What to type into the weather station, worked out for this installation.

This integration has no "add device" button: stations appear on their own the
first time they post. Someone who has not read the documentation gets an empty
page and no hint, so the setup flow ends on these instructions and a repair
brings them back until a station actually shows up.
"""

from homeassistant.const import CONF_PASSWORD
from homeassistant.helpers.network import NoURLAvailableError, get_url

from .const import ENDPOINTS


def async_urls(hass):
    """
    Addresses a station can post to, internal first.

    Returns:
        list: URLs, possibly empty when Home Assistant knows of none.
    """

    urls = []

    for kwargs in (
        {"allow_external": False, "allow_ip": True},
        {"allow_internal": False, "allow_cloud": False},
    ):
        try:
            url = get_url(hass, **kwargs)
        except NoURLAvailableError:
            continue

        if url not in urls:
            urls.append(url)

    return urls


def async_placeholders(hass, station_key):
    """
    Build the placeholders of the instructions screen.

    Args:
        hass: Home Assistant instance.
        station_key: Key the user configured, or a falsy value when blank.

    Returns:
        dict: translation placeholders.
    """

    urls = async_urls(hass)

    if urls:
        addresses = "\n".join(f"  - `{url}`" for url in urls)
    else:
        addresses = (
            "  - Home Assistant could not work out its own address. Use the one "
            "you reach it at, port included."
        )

    # Phrased to read correctly both after a dash and after a colon, since the
    # setup screen and the failure screen both use it.
    key_hint = (
        "the one you entered here"
        if station_key
        else "not needed, you left it blank — every request is accepted"
    )

    return {
        "urls": addresses,
        "key_hint": key_hint,
        "endpoints": "\n".join(f"  - `{path}`" for path in ENDPOINTS),
    }


def async_placeholders_for_entry(hass, entry):
    """Same, for an entry that already exists."""

    return async_placeholders(
        hass,
        entry.options.get(CONF_PASSWORD, entry.data.get(CONF_PASSWORD)),
    )
