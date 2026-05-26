"""Config flow for Fishing Score Assistant."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers import selector

from .const import (
    BODY_TYPES,
    CONF_BODY_TYPE,
    CONF_FISH,
    CONF_FORECAST_TYPE,
    CONF_WEATHER_ENTITY,
    DEFAULT_FORECAST_TYPE,
    DEFAULT_NAME,
    DOMAIN,
    FISH_TYPES,
    FORECAST_TYPES,
)


class FishingScoreConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Fishing Score Assistant."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            weather_entity = user_input[CONF_WEATHER_ENTITY]
            await self.async_set_unique_id(f"{weather_entity}:{user_input[CONF_NAME]}")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): selector.TextSelector(),
                vol.Required(CONF_WEATHER_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="weather")
                ),
                vol.Required(CONF_FORECAST_TYPE, default=DEFAULT_FORECAST_TYPE): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=FORECAST_TYPES,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(CONF_BODY_TYPE, default="lake"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=BODY_TYPES,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(CONF_FISH, default="carp"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=FISH_TYPES,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
