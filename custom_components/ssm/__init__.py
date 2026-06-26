"""The Swedish Radiation Safety Authority (SSM) integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry  # type: ignore
from homeassistant.const import Platform  # type: ignore
from homeassistant.core import HomeAssistant  # type: ignore

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SSM from a config entry."""
    _LOGGER.debug("Setting up SSM integration with entry_id: %s", entry.entry_id)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading SSM integration with entry_id: %s", entry.entry_id)

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
