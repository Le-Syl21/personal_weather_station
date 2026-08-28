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

AVAILABILITY_TIMEOUT_SELECTOR = vol.All(vol.Coerce(int), vol.Range(min=0, max=1440))


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the initial setup."""

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

        return self.async_create_entry(
            title="Personal Weather Station", data=user_input
        )


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle the options."""

    def __init__(self, config_entry):
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            # Merge rather than replace: the per station wind calibration lives
            # in the options too and is not part of this form.
            return self.async_create_entry(
                title="", data={**self._config_entry.options, **user_input}
            )

        options = self._config_entry.options

        return self.async_show_form(
            step_id="init",
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
