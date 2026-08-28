"""Config flow for the Personal Weather Station integration."""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD
from homeassistant.core import callback

from .const import (
    CONF_AVAILABILITY_TIMEOUT,
    CONF_DEBUG,
    DEFAULT_AVAILABILITY_TIMEOUT,
    DOMAIN,
)
from .instructions import async_placeholders, async_placeholders_for_entry

AVAILABILITY_TIMEOUT_SELECTOR = vol.All(vol.Coerce(int), vol.Range(min=0, max=1440))


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the initial setup."""

    def __init__(self):
        self._data = {}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({vol.Optional(CONF_PASSWORD): str}),
            )

        self._data = user_input

        return await self.async_step_instructions()

    async def async_step_instructions(self, user_input=None):
        """
        Show what to type into the station before finishing.

        There is no "add device" button to click afterwards: a station appears
        on its own the first time it posts, so this is the moment to say what
        makes that happen.
        """

        if user_input is not None:
            return self.async_create_entry(
                title="Personal Weather Station", data=self._data
            )

        return self.async_show_form(
            step_id="instructions",
            data_schema=vol.Schema({}),
            description_placeholders=async_placeholders(
                self.hass, self._data.get(CONF_PASSWORD)
            ),
        )


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle the options."""

    def __init__(self, config_entry):
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """
        Offer the settings, or the instructions for setting up a station.

        The onboarding repair goes away once a station has posted, so this is
        where the address to point a second one at stays reachable.
        """

        return self.async_show_menu(
            step_id="init", menu_options=["options", "instructions"]
        )

    async def async_step_instructions(self, user_input=None):
        if user_input is not None:
            return await self.async_step_init()

        return self.async_show_form(
            step_id="instructions",
            data_schema=vol.Schema({}),
            description_placeholders=async_placeholders_for_entry(
                self.hass, self._config_entry
            ),
        )

    async def async_step_options(self, user_input=None):
        if user_input is not None:
            # Merge rather than replace: the per station wind calibration lives
            # in the options too and is not part of this form.
            return self.async_create_entry(
                title="", data={**self._config_entry.options, **user_input}
            )

        options = self._config_entry.options

        return self.async_show_form(
            step_id="options",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_PASSWORD,
                        default=options.get(
                            CONF_PASSWORD,
                            self._config_entry.data.get(CONF_PASSWORD, ""),
                        ),
                    ): str,
                    vol.Optional(
                        CONF_AVAILABILITY_TIMEOUT,
                        default=options.get(
                            CONF_AVAILABILITY_TIMEOUT, DEFAULT_AVAILABILITY_TIMEOUT
                        ),
                    ): AVAILABILITY_TIMEOUT_SELECTOR,
                    vol.Optional(
                        CONF_DEBUG, default=options.get(CONF_DEBUG, False)
                    ): bool,
                }
            ),
        )
