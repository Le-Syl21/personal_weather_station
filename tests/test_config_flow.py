"""Config and options flows, and removing a station."""

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import device_registry as dr

from custom_components.personal_weather_station import (
    async_remove_config_entry_device,
)
from custom_components.personal_weather_station.const import (
    CONF_AVAILABILITY_TIMEOUT,
    CONF_WIND_OFFSETS,
    DOMAIN,
)

from .conftest import WSLINK_ENDPOINT, state_of

DEVICE_ID = "wsabcde123"


async def test_user_flow_creates_the_entry(hass):
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_PASSWORD: "s3cr3t"}
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_PASSWORD: "s3cr3t"}


async def test_only_one_entry_is_allowed(hass, setup_pws):
    """One HTTP server, one station key, any number of stations."""

    await setup_pws()

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "single_instance_allowed"


async def test_options_flow_defaults(hass, setup_pws):
    entry, _ = await setup_pws(password="s3cr3t")

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == FlowResultType.FORM

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_PASSWORD: "s3cr3t",
            CONF_AVAILABILITY_TIMEOUT: 45,
            "debug": True,
        },
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert entry.options[CONF_AVAILABILITY_TIMEOUT] == 45
    assert entry.options["debug"] is True


async def test_station_can_be_removed(hass, setup_pws):
    """
    Devices show up on their own, so a typo in the sender ID would otherwise
    leave a ghost station behind for good.
    """

    entry, client = await setup_pws()

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1wdir=237&t1tem=21")
    await hass.async_block_till_done()

    await hass.services.async_call(
        "button",
        "press",
        {
            "entity_id": hass.states.async_entity_ids("button")[0],
        },
        blocking=True,
    )
    await hass.async_block_till_done()
    assert entry.options[CONF_WIND_OFFSETS] == {DEVICE_ID: 123}

    device_entry = dr.async_get(hass).async_get_device_by_identifier(
        (DOMAIN, DEVICE_ID), entry.entry_id
    )
    assert device_entry is not None

    assert await async_remove_config_entry_device(hass, entry, device_entry)
    await hass.async_block_till_done()

    runtime = hass.data[DOMAIN]
    assert DEVICE_ID not in runtime.devices

    # Its calibration is dropped along with it.
    assert entry.options[CONF_WIND_OFFSETS] == {}


async def test_removed_station_reappears_when_it_posts_again(hass, setup_pws):
    entry, client = await setup_pws()

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=21")
    await hass.async_block_till_done()

    device_entry = dr.async_get(hass).async_get_device_by_identifier(
        (DOMAIN, DEVICE_ID), entry.entry_id
    )
    await async_remove_config_entry_device(hass, entry, device_entry)
    dr.async_get(hass).async_remove_device(device_entry.id)
    await hass.async_block_till_done()

    response = await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=24")
    assert response.status == 200
    await hass.async_block_till_done()

    assert state_of(hass, DEVICE_ID, "t1tem").state == "24"
