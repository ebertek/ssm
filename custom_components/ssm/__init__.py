"""The Swedish Radiation Safety Authority (SSM) integration."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform, CONF_NAME
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_LOCATION_ID,
    CONF_LOCATION,
    DEFAULT_NAME,
    RADIATION_STATIONS,
    UV_LOCATIONS,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_LOCATION_ID): cv.string,
        vol.Required(CONF_LOCATION): cv.string,
    }),
}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the SSM component from YAML."""
    if DOMAIN not in config:
        return True

    conf = config[DOMAIN]

    # Check if a config entry with the same unique ID already exists
    unique_id = f"{conf[CONF_LOCATION_ID]}_{conf[CONF_LOCATION]}"
    existing_entry = await hass.config_entries.async_get_entry(unique_id)

    if existing_entry:
        _LOGGER.warning(f"Config entry with unique ID '{unique_id}' already exists.")
        return True

    # Create a config entry from the YAML configuration
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_IMPORT},
            data=conf,
        )
    )

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SSM from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok