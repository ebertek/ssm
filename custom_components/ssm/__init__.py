"""The Swedish Radiation Safety Authority (SSM) integration."""

# pylint: disable=E0401

import logging

from homeassistant.config_entries import ConfigEntry  # type: ignore
from homeassistant.const import Platform  # type: ignore
from homeassistant.core import HomeAssistant  # type: ignore

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SSM from a config entry."""
    _LOGGER.debug("Setting up SSM integration with entry_id: %s", entry.entry_id)

    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})

    # Combine data from entry.data and entry.options
    combined_data = dict(entry.data)
    # Update with options, options take precedence over data
    if entry.options:
        combined_data.update(entry.options)

    # Store the combined data
    hass.data[DOMAIN][entry.entry_id] = combined_data
    _LOGGER.debug("Combined configuration data for SSM: %s", combined_data)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.add_update_listener(async_reload_entry)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading SSM integration with entry_id: %s", entry.entry_id)

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        _LOGGER.debug(
            "Successfully unloaded SSM integration with entry_id: %s", entry.entry_id
        )
    else:
        _LOGGER.warning(
            "Failed to unload SSM integration with entry_id: %s", entry.entry_id
        )

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    _LOGGER.debug("Reloading SSM integration with entry_id: %s", entry.entry_id)

    unload_ok = await async_unload_entry(hass, entry)
    if unload_ok:
        await async_setup_entry(hass, entry)
    else:
        _LOGGER.error("Failed to unload before reload of entry_id: %s", entry.entry_id)
