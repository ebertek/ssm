"""Config flow for Swedish Radiation Safety Authority integration."""
import logging
import voluptuous as vol
from typing import Any, Dict, Optional

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.const import CONF_NAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig
)

from .const import (
    DOMAIN,
    CONF_STATION,
    CONF_LOCATION,
    CONF_SKIN_TYPE,
    DEFAULT_NAME,
    STATIONS,
    LOCATIONS,
    SKIN_TYPES
)

_LOGGER = logging.getLogger(__name__)

async def validate_input(hass: HomeAssistant, data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the user input allows us to connect."""
    # Test radiation API endpoint if station is provided
    session = async_get_clientsession(hass)

    if data.get(CONF_STATION):
        try:
            url = f"https://karttjanst.ssm.se/data/getHistoryForStation?locationId={data[CONF_STATION]}&start=0&end=1"
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Radiation API returned status {response.status}")
        except Exception as e:
            _LOGGER.error("Error validating Radiation API: %s", e)
            raise

    # Validate the UV index endpoint if location is provided
    if data.get(CONF_LOCATION):
        try:
            location = data[CONF_LOCATION].replace(" ", "%20")
            url = f"https://www.stralsakerhetsmyndigheten.se/api/uvindex/{location}?offset=-1"
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"UV Index API returned status {response.status}")
        except Exception as e:
            _LOGGER.error("Error validating UV Index API: %s", e)
            raise

    # Return validated data
    return {"title": data[CONF_NAME]}

class SSMConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SSM integration."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                
                # Create a unique ID from location ID and location
                await self.async_set_unique_id(f"{user_input.get(CONF_STATION)}_{user_input.get(CONF_LOCATION)}")
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )
            except Exception:
                errors["base"] = "cannot_connect"

        # Create dropdown options for location ID
        station_options = [
            {"value": station["id"], "label": station["name"]}
            for station in STATIONS
        ]

        # Create dropdown options for UV locations
        location_options = [
            {"value": location["id"], "label": location["name"]}
            for location in LOCATIONS
        ]

        # Create dropdown options for skin type
        skin_type_options = [
            {"value": skin_type["id"], "label": skin_type["name"]}
            for skin_type in SKIN_TYPES
        ]

        # Provide a form for user input
        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Optional(CONF_STATION): SelectSelector(
                    SelectSelectorConfig(
                        options=station_options,
                        translation_key="station",
                        mode="dropdown",
                    )
                ),
                vol.Optional(CONF_LOCATION): SelectSelector(
                    SelectSelectorConfig(
                        options=location_options,
                        translation_key="location",
                        mode="dropdown",
                    )
                ),
                vol.Optional(CONF_SKIN_TYPE): SelectSelector(
                    SelectSelectorConfig(
                        options=skin_type_options,
                        translation_key="skin_type",
                        mode="dropdown",
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return SSMOptionsFlow(config_entry)


class SSMOptionsFlow(config_entries.OptionsFlow):
    """Handle options for SSM integration."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        _LOGGER.debug("Options flow started")
        if user_input is not None:
            _LOGGER.debug("User input received: %s", user_input)
            return self.async_create_entry(title="", data=user_input)

        # Create dropdown options for location ID
        station_options = [
            {"value": station["id"], "label": station["name"]}
            for station in STATIONS
        ]

        # Create dropdown options for UV locations
        location_options = [
            {"value": location["id"], "label": location["name"]}
            for location in LOCATIONS
        ]

        # Create dropdown options for skin type
        skin_type_options = [
            {"value": skin_type["id"], "label": skin_type["name"]}
            for skin_type in SKIN_TYPES
        ]

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_STATION,
                        default=self.config_entry.options.get(
                            CONF_STATION, 
                            self.config_entry.data.get(CONF_STATION)
                        ),
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=station_options,
                            translation_key="station",
                            mode="dropdown",
                        )
                    ),
                    vol.Optional(
                        CONF_LOCATION,
                        default=self.config_entry.options.get(
                            CONF_LOCATION,
                            self.config_entry.data.get(CONF_LOCATION)
                        ),
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=location_options,
                            translation_key="location",
                            mode="dropdown",
                        )
                    ),
                    vol.Optional(
                        CONF_SKIN_TYPE,
                        default=self.config_entry.options.get(
                            CONF_SKIN_TYPE,
                            self.config_entry.data.get(CONF_SKIN_TYPE)
                        ),
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=skin_type_options,
                            translation_key="skin_type",
                            mode="dropdown",
                        )
                    ),
                }
            ),
        )
