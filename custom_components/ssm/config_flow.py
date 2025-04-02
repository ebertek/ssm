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

from .const import DOMAIN, CONF_LOCATION_ID, CONF_LOCATION, DEFAULT_NAME

_LOGGER = logging.getLogger(__name__)

# Predefined stations with their location IDs
RADIATION_STATIONS = [
    {"id": "20", "name": "Bjuruklubb (Skellefteå)"},
    {"id": "5", "name": "Brämön"},
    {"id": "7", "name": "Fårösund"},
    {"id": "18", "name": "Gielas (Kittelfjäll)"},
    {"id": "8", "name": "Gävle"},
    {"id": "17", "name": "Göteborg"},
    {"id": "16", "name": "Hallands Väderö"},
    {"id": "21", "name": "Hällum"},
    {"id": "6", "name": "Järnäsklubb"},
    {"id": "11", "name": "Karesuando"},
    {"id": "1278", "name": "Kilsbergen"},
    {"id": "4", "name": "Krångede"},
    {"id": "22", "name": "Malmö"},
    {"id": "19", "name": "Malå"},
    {"id": "2", "name": "Mora"},
    {"id": "1276", "name": "Norrköping"},
    {"id": "12", "name": "Pajala"},
    {"id": "9", "name": "Ritsem"},
    {"id": "1", "name": "Sala"},
    {"id": "25", "name": "Skarpö"},
    {"id": "14", "name": "Skillinge"},
    {"id": "10", "name": "Storön"},
    {"id": "15", "name": "Sunne"},
    {"id": "3", "name": "Tännäs"},
    {"id": "24", "name": "Visingsö"},
    {"id": "1277", "name": "Växjö"},
    {"id": "23", "name": "Ölands Norra Udde"},
    {"id": "13", "name": "Ölands Södra Udde"},
]

async def validate_input(hass: HomeAssistant, data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the user input allows us to connect.
    
    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    # Test radiation API endpoint
    session = async_get_clientsession(hass)
    
    # Validate the radiation endpoint
    try:
        url = f"https://karttjanst.ssm.se/data/getHistoryForStation?locationId={data[CONF_LOCATION_ID]}&start=0&end=1"
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Radiation API returned status {response.status}")
            # Don't need to parse the JSON since we just want to verify the endpoint works
    except Exception as e:
        _LOGGER.error("Error validating Radiation API: %s", e)
        raise

    # Validate the UV index endpoint
    try:
        location = data[CONF_LOCATION].replace(" ", "%20")
        url = f"https://www.stralsakerhetsmyndigheten.se/api/uvindex/{location}?offset=-1"
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"UV Index API returned status {response.status}")
            # Don't need to parse the JSON since we just want to verify the endpoint works
    except Exception as e:
        _LOGGER.error("Error validating UV Index API: %s", e)
        raise

    # Return validated data
    return {"title": data[CONF_NAME]}

class SSMConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SSM integration."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                
                # Create a unique ID from location ID and location
                await self.async_set_unique_id(f"{user_input[CONF_LOCATION_ID]}_{user_input[CONF_LOCATION]}")
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
            for station in RADIATION_STATIONS
        ]

        # Provide a form for user input
        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(CONF_LOCATION_ID): SelectSelector(
                    SelectSelectorConfig(
                        options=station_options,
                        translation_key="station",
                        mode="dropdown",
                    )
                ),
                vol.Required(CONF_LOCATION): str,
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
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Create dropdown options for location ID
        station_options = [
            {"value": station["id"], "label": station["name"]}
            for station in RADIATION_STATIONS
        ]

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_LOCATION_ID,
                        default=self.config_entry.options.get(
                            CONF_LOCATION_ID, 
                            self.config_entry.data.get(CONF_LOCATION_ID)
                        ),
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=station_options,
                            translation_key="station",
                            mode="dropdown",
                        )
                    ),
                    vol.Required(
                        CONF_LOCATION,
                        default=self.config_entry.options.get(
                            CONF_LOCATION, 
                            self.config_entry.data.get(CONF_LOCATION)
                        ),
                    ): str,
                }
            ),
        )