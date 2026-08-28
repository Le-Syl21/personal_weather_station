"""Binary sensor platform: connection and water leak status.

The WSLink API documents these as 1/0 readings. Exposing them as numbers made
them unusable with Home Assistant's standard leak cards and alerts.
"""

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.const import EntityCategory
from homeassistant.util import slugify

from .const import (
    DOMAIN,
    SENSOR_KEY_MAP,
    SENSOR_LIST,
    SENSOR_TRANSLATION_KEYS,
)
from .entity import PwsEntity
from .models import PwsDevice
from .registry import async_rebuild_platform

PLATFORM = "binary_sensor"


async def async_setup_entry(hass, entry, async_add_entities):
    """
    Set up the binary sensor platform.

    Args:
        hass: Home Assistant instance.
        entry: Config entry object.
        async_add_entities: Function to add new entities to Home Assistant.

    Returns:
        None
    """

    runtime = hass.data[DOMAIN]
    runtime.add_entities[PLATFORM] = async_add_entities

    restored = async_rebuild_platform(hass, runtime, PLATFORM, _restore_binary_sensor)

    if restored:
        async_add_entities(restored)


def _restore_binary_sensor(device, key):
    """Build the binary sensor matching a unique ID suffix in the registry."""

    if key in device.entities:
        return None

    canonical = SENSOR_KEY_MAP.get(key)

    if canonical is None or not SENSOR_LIST[canonical].get("binary"):
        return None

    return PwsBinarySensor(device, canonical)


def build_new_entities(device, keys):
    """
    Build the binary sensors a freshly received payload calls for.

    Devices that already expose these keys as numeric sensors are left alone
    until the user asks for the conversion from Repairs.

    Args:
        device: PwsDevice being updated.
        keys: Canonical sensor keys present in the payload.

    Returns:
        list: Newly created entities.
    """

    if device.legacy_status_sensors:
        return []

    return [
        PwsBinarySensor(device, key)
        for key in keys
        if key not in device.entities and SENSOR_LIST[key].get("binary")
    ]


class PwsBinarySensor(PwsEntity, BinarySensorEntity):
    """A connection or water leak status reported by a PWS device."""

    _pws_platform = PLATFORM

    def __init__(self, device: PwsDevice, key: str):
        """
        Initialize the binary sensor.

        Args:
            device: PwsDevice instance the sensor belongs to.
            key: String key identifying the sensor type.

        Returns:
            None
        """

        self._meta = SENSOR_LIST[key]
        self._attr_translation_key = SENSOR_TRANSLATION_KEYS.get(key, slugify(key))
        self._attr_device_class = BinarySensorDeviceClass(self._meta["binary"])

        if self._attr_device_class is BinarySensorDeviceClass.CONNECTIVITY:
            self._attr_entity_category = EntityCategory.DIAGNOSTIC

        super().__init__(device, key, self._meta["name"])

    @property
    def is_on(self):
        """
        Both protocols use 1 for the active state.

        Connected=1 for a connection status, Leak=1 for a water leak sensor.
        """

        value = self.device.data.get(self._key)

        if value is None:
            return None

        return value == 1
