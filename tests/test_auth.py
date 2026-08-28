"""Station key checking, error codes and the Repairs issues they raise."""

from homeassistant.helpers import issue_registry as ir

from custom_components.personal_weather_station.const import DOMAIN

from .conftest import WSLINK_ENDPOINT, state_of

DEVICE_ID = "wsabcde123"
STATION_KEY = "s3cr3t"


def issues_for(hass):
    """Return the Repairs issues raised by the integration."""

    return [
        issue
        for (domain, _), issue in ir.async_get(hass).issues.items()
        if domain == DOMAIN
    ]


async def test_no_key_accepts_everything(hass, setup_pws):
    """Leaving the station key blank is documented as accepting any station."""

    _, client = await setup_pws()

    response = await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&t1tem=21")

    assert response.status == 200
    assert issues_for(hass) == []


async def test_wrong_key_is_rejected_and_reported(hass, setup_pws):
    """
    A wrong key used to be invisible unless debug logging was on.

    It is the single most likely reason for a station never showing up, so it
    has to reach the user through Repairs.
    """

    _, client = await setup_pws(password=STATION_KEY)

    response = await client.get(
        f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&wspw=wrong&t1tem=21"
    )

    assert response.status == 401

    issues = issues_for(hass)
    assert len(issues) == 1
    assert issues[0].translation_key == "invalid_station_key"
    assert issues[0].translation_placeholders["station_id"] == DEVICE_ID
    assert issues[0].severity == ir.IssueSeverity.WARNING

    # Nothing was created for a station that failed the check.
    assert state_of(hass, DEVICE_ID, "t1tem") is None


async def test_issue_clears_once_the_station_gets_through(hass, setup_pws):
    """The warning goes away on its own once the key is fixed."""

    _, client = await setup_pws(password=STATION_KEY)

    await client.get(f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&wspw=wrong&t1tem=21")
    assert len(issues_for(hass)) == 1

    await client.get(
        f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&wspw={STATION_KEY}&t1tem=21"
    )
    await hass.async_block_till_done()

    assert issues_for(hass) == []
    assert state_of(hass, DEVICE_ID, "t1tem").state == "21"


async def test_right_key_is_accepted(hass, setup_pws):
    _, client = await setup_pws(password=STATION_KEY)

    response = await client.get(
        f"{WSLINK_ENDPOINT}?wsid={DEVICE_ID}&wspw={STATION_KEY}&t1tem=21"
    )

    assert response.status == 200


async def test_weather_underground_password_parameter(hass, setup_pws):
    """The Weather Underground endpoint names the key PASSWORD."""

    _, client = await setup_pws(password=STATION_KEY)

    response = await client.get(
        f"/weatherstation/updateweatherstation.php?ID={DEVICE_ID}"
        f"&PASSWORD={STATION_KEY}&tempf=72"
    )

    assert response.status == 200


async def test_missing_device_id_returns_400(hass, setup_pws):
    """This used to answer 200 while the log claimed it had answered 400."""

    _, client = await setup_pws()

    response = await client.get(f"{WSLINK_ENDPOINT}?t1tem=21")

    assert response.status == 400

    issues = issues_for(hass)
    assert len(issues) == 1
    assert issues[0].translation_key == "missing_device_id"
