from __future__ import annotations

from typing import Any

from homeassistant.data_entry_flow import FlowResult

"""Config flow for the Atag component."""
import oekofen_api
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_PASSWORD, CONF_SCAN_INTERVAL

from . import const

DATA_SCHEMA = {
    vol.Required(CONF_HOST): str,
    vol.Required(CONF_PORT, default=oekofen_api.const.DEFAULT_PORT): vol.Coerce(int),
    vol.Required(CONF_PASSWORD): str,
    vol.Required(
        CONF_SCAN_INTERVAL, default=oekofen_api.const.UPDATE_INTERVAL_SECONDS
    ): vol.Coerce(int),
    vol.Optional(
        const.CONF_RAISE_EXCEPTION_ON_UPDATE, default=True
    ): vol.Coerce(bool),
}


class OekofenConfigFlow(config_entries.ConfigFlow, domain=const.DOMAIN):
    """Config flow for Oekofen."""

    VERSION = 2

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""

        if not user_input:
            return await self._show_form()

        host = user_input[CONF_HOST]
        port = user_input[CONF_PORT]
        json_password = user_input[CONF_PASSWORD]
        update_interval = user_input[CONF_SCAN_INTERVAL]
        client = oekofen_api.Oekofen(
            host=host,
            port=port,
            json_password=json_password,
            update_interval=update_interval,
        )
        try:
            await client.update_data()
            print("Finished oekofen_api.Oekofen client=%s" % client)
        except Exception as ex:
            return await self._show_form({"base": str(ex)})

        await self.async_set_unique_id(client.get_uid())
        self._abort_if_unique_id_configured(updates=user_input)

        model = client.get_model()
        title = f"Oekofen {model}"

        return self.async_create_entry(title=title, data=user_input)

    async def _show_form(self, errors=None):
        """Show the form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(DATA_SCHEMA),
            errors=errors if errors else {},
        )


class OekofenOptionsFlow(config_entries.OptionsFlow):
    """Handle Oekofen options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize the flux_led options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure the options."""
        errors: dict[str, str] = {}
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self._config_entry.options
        options_schema = vol.Schema(
            {
                vol.Required(
                    CONF_SCAN_INTERVAL, default=options.get(CONF_SCAN_INTERVAL)
                ): vol.Coerce(int),
                vol.Optional(
                    options.get(const.CONF_RAISE_EXCEPTION_ON_UPDATE), default=True
                ): vol.Coerce(bool),
            }
        )

        return self.async_show_form(
            step_id="init", data_schema=options_schema, errors=errors
        )
