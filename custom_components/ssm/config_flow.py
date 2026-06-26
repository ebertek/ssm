"""Config flow for Swedish Radiation Safety Authority integration."""

# pylint: disable=C0301, E0401, R0903, W0718, W0719

from __future__ import annotations

import logging
import uuid
from typing import Any

import voluptuous as vol  # type: ignore
from homeassistant import config_entries  # type: ignore
from homeassistant.config_entries import ConfigEntry, ConfigFlowResult  # type: ignore
from homeassistant.const import CONF_NAME  # type: ignore
from homeassistant.core import HomeAssistant, callback  # type: ignore
from homeassistant.helpers.selector import (  # type: ignore
    SelectSelector,
    SelectSelectorConfig,
)

from .const import (
    CONF_LOCATION,
    CONF_SKIN_TYPE,
    CONF_STATION,
    DEFAULT_NAME,
    DOMAIN,
    LOCATIONS,
    SKIN_TYPES,
    STATIONS,
)

_LOGGER = logging.getLogger(__name__)


class CannotConnect(Exception):
    """Error to indicate invalid configuration."""


def _get_api_location_name(location_id: str) -> str | None:
    """Get the API location name for a given location ID."""
    location = next((loc for loc in LOCATIONS if loc["id"] == location_id), None)
    return location["api_name"] if location else None


async def validate_input(
    _hass: HomeAssistant,
    data: dict[str, Any],
) -> dict[str, Any]:
    """Validate the user input.

    Only validate local selector values during setup. Do not block setup on
    transient SSM API failures; sensors will become unavailable if polling fails.
    """
    if data.get(CONF_STATION) and not any(
        station["id"] == data[CONF_STATION] for station in STATIONS
    ):
        raise CannotConnect

    if data.get(CONF_LOCATION) and _get_api_location_name(data[CONF_LOCATION]) is None:
        raise CannotConnect

    if data.get(CONF_SKIN_TYPE) and not any(
        skin_type["id"] == data[CONF_SKIN_TYPE] for skin_type in SKIN_TYPES
    ):
        raise CannotConnect

    return {"title": data[CONF_NAME]}


def _station_options() -> list[dict[str, str]]:
    """Return station selector options."""
    return [{"value": station["id"], "label": station["name"]} for station in STATIONS]


def _location_options() -> list[dict[str, str]]:
    """Return location selector options."""
    return [
        {"value": location["id"], "label": location["name"]} for location in LOCATIONS
    ]


def _skin_type_options() -> list[dict[str, str]]:
    """Return skin type selector options."""
    return [
        {"value": skin_type["id"], "label": skin_type["name"]}
        for skin_type in SKIN_TYPES
    ]


def _config_schema() -> vol.Schema:
    """Return the config flow schema."""
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
            vol.Optional(CONF_STATION): SelectSelector(
                SelectSelectorConfig(
                    options=_station_options(),
                    translation_key="station",
                    mode="dropdown",
                )
            ),
            vol.Optional(CONF_LOCATION): SelectSelector(
                SelectSelectorConfig(
                    options=_location_options(),
                    translation_key="location",
                    mode="dropdown",
                )
            ),
            vol.Optional(CONF_SKIN_TYPE): SelectSelector(
                SelectSelectorConfig(
                    options=_skin_type_options(),
                    translation_key="skin_type",
                    mode="dropdown",
                )
            ),
        }
    )


def _options_schema() -> vol.Schema:
    """Return the options flow schema."""
    return vol.Schema(
        {
            vol.Optional(CONF_STATION): SelectSelector(
                SelectSelectorConfig(
                    options=_station_options(),
                    translation_key="station",
                    mode="dropdown",
                )
            ),
            vol.Optional(CONF_LOCATION): SelectSelector(
                SelectSelectorConfig(
                    options=_location_options(),
                    translation_key="location",
                    mode="dropdown",
                )
            ),
            vol.Optional(CONF_SKIN_TYPE): SelectSelector(
                SelectSelectorConfig(
                    options=_skin_type_options(),
                    translation_key="skin_type",
                    mode="dropdown",
                )
            ),
        }
    )


class SSMConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg]
    """Handle a config flow for SSM integration."""

    VERSION = 1
    MINOR_VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                _LOGGER.debug(
                    "Invalid SSM configuration input: %s",
                    user_input,
                    exc_info=True,
                )
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception validating input")
                errors["base"] = "unknown"
            else:
                # This UUID keeps each entry unique, but it does not prevent duplicate
                # entries with the same selected station/location.
                unique_id = str(uuid.uuid4())
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_config_schema(),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        _config_entry: ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return SSMOptionsFlow()


class SSMOptionsFlow(config_entries.OptionsFlowWithReload):
    """Handle options for SSM integration."""

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            cleaned_input = {
                key: value
                for key, value in user_input.items()
                if value not in (None, "")
            }

            return self.async_create_entry(data=cleaned_input)

        current_values = {
            CONF_STATION: self.config_entry.options.get(
                CONF_STATION,
                self.config_entry.data.get(CONF_STATION),
            ),
            CONF_LOCATION: self.config_entry.options.get(
                CONF_LOCATION,
                self.config_entry.data.get(CONF_LOCATION),
            ),
            CONF_SKIN_TYPE: self.config_entry.options.get(
                CONF_SKIN_TYPE,
                self.config_entry.data.get(CONF_SKIN_TYPE),
            ),
        }

        current_values = {
            key: value
            for key, value in current_values.items()
            if value not in (None, "")
        }

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                _options_schema(),
                current_values,
            ),
        )
