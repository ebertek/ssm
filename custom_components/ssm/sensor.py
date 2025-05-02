"""Sensor platform for Swedish Radiation Safety Authority integration."""

# pylint: disable=C0301, E0401, R0902, R0903, R0912, R0913, R0914, R0915, R0917, W0511, W0718

import asyncio
import logging
import time
from datetime import datetime, timedelta
from urllib.parse import quote
from zoneinfo import ZoneInfo

from homeassistant.components.sensor import (  # type: ignore
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import CONF_NAME  # type: ignore
from homeassistant.helpers.aiohttp_client import async_get_clientsession  # type: ignore
from homeassistant.helpers.entity import DeviceInfo  # type: ignore
from homeassistant.util import dt as dt_util  # type: ignore

from .const import CONF_LOCATION, CONF_SKIN_TYPE, CONF_STATION, DOMAIN, LOCATIONS

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=30)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up SSM sensors based on a config entry."""
    # Get combined data from the hass.data[DOMAIN] dictionary
    name = config_entry.options.get(CONF_NAME, config_entry.data.get(CONF_NAME))
    station = config_entry.options.get(
        CONF_STATION, config_entry.data.get(CONF_STATION)
    )
    location = config_entry.options.get(
        CONF_LOCATION, config_entry.data.get(CONF_LOCATION)
    )
    skin_type = config_entry.options.get(
        CONF_SKIN_TYPE, config_entry.data.get(CONF_SKIN_TYPE)
    )

    # Create session
    session = async_get_clientsession(hass)

    # List to track added entities
    entities = []

    if station:
        radiation_sensor = SSMRadiationSensor(
            hass, session, name, station, config_entry.entry_id
        )
        entities.append(radiation_sensor)

    if location:
        uv_sensor = SSMUVIndexSensor(
            hass, session, name, location, config_entry.entry_id
        )
        entities.append(uv_sensor)

        # Only add sun time sensor if both location and skin_type are available
        if skin_type:
            sun_time_sensor = SSMSunTimeSensor(
                hass,
                session,
                name,
                skin_type,
                uv_sensor,
                location,
                config_entry.entry_id,
            )
            entities.append(sun_time_sensor)

    if entities:
        async_add_entities(entities, True)


class SSMRadiationSensor(SensorEntity):
    """Representation of a SSM Radiation Sensor."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "nSv/h"
    _attr_icon = "mdi:radioactive"
    _attr_translation_key = "radiation_level"

    def __init__(self, hass, session, name, station, entry_id):
        """Initialize the sensor."""
        self.hass = hass
        self._session = session
        self._attr_name = "Radiation Level"
        self._station = station
        self._entry_id = entry_id

        self._attr_unique_id = f"{entry_id}_radiation"
        self._attr_native_value = None
        self._attr_available = True

        self._attr_extra_state_attributes = {
            "last_updated": None,
        }

        # Define device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=name,
            manufacturer="Swedish Radiation Safety Authority",
            model="Radiation and UV Monitor",
        )

    async def async_update(self):
        """Get the latest data from the API and update the state."""
        try:
            # Explicitly use Stockholm time (handles DST transitions correctly)
            stockholm = ZoneInfo("Europe/Stockholm")
            now = datetime.now(stockholm)
            is_dst = bool(now.dst())

            # Fetch the last two values
            end = now.replace(minute=0, second=0, microsecond=0)
            start = end - timedelta(hours=3 if is_dst else 2)

            # Convert to Unix timestamps in milliseconds
            start_timestamp = int(start.timestamp() * 1000)
            end_timestamp = int(end.timestamp() * 1000)

            url = f"https://karttjanst.ssm.se/data/getHistoryForStation?locationId={self._station}&start={start_timestamp}&end={end_timestamp}"  #pylint: disable=line-too-long

            _LOGGER.debug("Sending request to Radiation API: %s", url)

            async with self._session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    _LOGGER.debug("Received response from Radiation API: %s", data)

                    if "values" in data and data["values"]:
                        values = data["values"]
                        radiation_values = [
                            item[1] for item in values
                        ]  # Extract radiation values

                        # Convert from μSv/h to nSv/h
                        self._attr_native_value = round(
                            radiation_values[-1] * 1000
                        )  # Most recent value
                        self._attr_extra_state_attributes["last_updated"] = (
                            dt_util.utcnow().isoformat()
                        )
                        self._attr_available = True
                    else:
                        _LOGGER.error(
                            "Invalid data format received from SSM Radiation API: %s",
                            data,
                        )
                        self._attr_available = False
                else:
                    _LOGGER.error(
                        "Failed to fetch radiation data from SSM API: %s",
                        response.status,
                    )
                    self._attr_available = False
        except Exception as e:
            _LOGGER.error("Error updating SSM Radiation sensor: %s", e)
            self._attr_available = False


class SSMUVIndexSensor(SensorEntity):
    """Representation of a SSM UV Index Sensor."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "UV"
    _attr_icon = "mdi:sun-wireless"
    _attr_translation_key = "uv_index"

    def __init__(self, hass, session, name, location, entry_id):
        """Initialize the sensor."""
        self.hass = hass
        self._session = session
        self._attr_name = "UV Index"
        self._location = location
        self._entry_id = entry_id

        self._attr_unique_id = f"{entry_id}_uv_index"
        self._attr_native_value = None
        self._attr_available = True

        self._attr_extra_state_attributes = {
            "current_uv": None,
            "max_uv_today": None,
            "max_uv_time": None,
            "max_uv_tomorrow": None,
            "hourly_forecast": [],
            "risk_level": None,
            "last_updated": None,
        }

        # Define device info (same as radiation sensor for grouping)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=name,
            manufacturer="Swedish Radiation Safety Authority",
            model="Radiation and UV Monitor",
        )

    def _get_risk_level(self, uv_index):
        """Get the UV risk level based on the index value."""
        if uv_index >= 11:
            return "extreme"
        if uv_index >= 8:
            return "very_high"
        if uv_index >= 6:
            return "high"
        if uv_index >= 3:
            return "moderate"
        if uv_index > 0:
            return "low"
        return "none"

    def _get_icon(self, uv_index):
        """Get the appropriate icon based on UV index value."""
        if uv_index >= 11:
            return "mdi:fire"
        if uv_index >= 8:
            return "mdi:weather-sunny-alert"
        if uv_index >= 6:
            return "mdi:weather-sunny"
        if uv_index >= 3:
            return "mdi:weather-partly-cloudy"
        if uv_index > 0:
            return "mdi:weather-sunny-off"
        return "mdi:weather-night"

    def _get_api_location_name(self, location_id):
        """Get the API location name for a given location ID."""
        location = next((loc for loc in LOCATIONS if loc["id"] == location_id), None)
        return location.get("api_name") if location else None

    async def async_update(self):
        """Get the latest data from the API and update the state."""
        try:
            # Determine if DST is in effect to set correct offset
            is_dst = time.localtime().tm_isdst > 0
            offset = "-2" if is_dst else "-1"

            # Map location to API value and URL encode it
            api_location = self._get_api_location_name(self._location)
            encoded_location = quote(api_location)
            url = f"https://www.stralsakerhetsmyndigheten.se/api/uvindex/{encoded_location}?offset={offset}"

            _LOGGER.debug("Sending request to UV Index API: %s", url)

            async with self._session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    _LOGGER.debug("Received response from UV Index API: %s", data)

                    if (
                        "response" in data
                        and "location" in data["response"]
                        and "date" in data["response"]["location"]
                    ):
                        location_data = data["response"]["location"]
                        today_data = location_data["date"][0]

                        # Get current hour UV index
                        current_hour = datetime.now().hour
                        hourly_data = today_data["hourlyUvIndex"]
                        current_uv = hourly_data[current_hour]

                        # Maximum UV for today
                        max_uv_today = today_data["maxUvIndex"]
                        max_uv_time = today_data["maxUvIndexTime"]

                        # Format time to HH:MM
                        max_time_obj = datetime.strptime(
                            max_uv_time, "%Y-%m-%dT%H:%M:%S"
                        )
                        max_time_formatted = max_time_obj.strftime("%H:%M")

                        # Get tomorrow's data if available
                        max_uv_tomorrow = None
                        if len(location_data["date"]) > 1:
                            max_uv_tomorrow = location_data["date"][1]["maxUvIndex"]

                        # Format hourly forecast
                        hourly_forecast = ", ".join(
                            f"{hour:02d}:00 — {uv:.2f}"
                            for hour, uv in enumerate(hourly_data)
                        )

                        # Update state and attributes
                        self._attr_native_value = current_uv
                        self._attr_extra_state_attributes["current_uv"] = current_uv
                        self._attr_extra_state_attributes["max_uv_today"] = max_uv_today
                        self._attr_extra_state_attributes["max_uv_time"] = (
                            max_time_formatted
                        )
                        self._attr_extra_state_attributes["max_uv_tomorrow"] = (
                            max_uv_tomorrow
                        )
                        self._attr_extra_state_attributes["hourly_forecast"] = (
                            hourly_forecast
                        )
                        risk_level_key = self._get_risk_level(max_uv_today)
                        self._attr_extra_state_attributes["risk_level"] = risk_level_key
                        self._attr_extra_state_attributes["last_updated"] = (
                            dt_util.utcnow().isoformat()
                        )

                        # Update icon based on current UV value
                        self._attr_icon = self._get_icon(current_uv)

                        self._attr_available = True
                    else:
                        _LOGGER.error(
                            "Invalid data format received from SSM UV Index API: %s",
                            data,
                        )
                        self._attr_available = False
                else:
                    _LOGGER.error(
                        "Failed to fetch UV index data from SSM API: %s",
                        response.status,
                    )
                    self._attr_available = False
        except Exception as e:
            _LOGGER.error("Error updating SSM UV Index sensor: %s", e)
            self._attr_available = False


class SSMSunTimeSensor(SensorEntity):
    """Representation of a SSM Min Soltid Sensor."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "minutes"
    _attr_icon = "mdi:sun-clock"
    _attr_translation_key = "min_soltid"

    def __init__(self, hass, session, name, skin_type, uv_sensor, location, entry_id):
        """Initialize the sensor."""
        self.hass = hass
        self._session = session
        self._attr_name = "Min soltid"
        self._skin_type = skin_type
        self._uv_sensor = uv_sensor
        self._location = location
        self._entry_id = entry_id

        self._attr_unique_id = f"{entry_id}_sun_time"
        self._attr_native_value = None
        self._attr_available = True

        self._attr_extra_state_attributes = {
            "shade_direct_sun": None,
            "shade_partial": None,
            "shade_full": None,
            "i_shade_direct_sun": None,
            "i_shade_partial": None,
            "i_shade_full": None,
            "last_updated": None,
        }

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=name,
            manufacturer="Swedish Radiation Safety Authority",
            model="Radiation and UV Monitor",
        )

    def _get_location_latitude(self, location_id: str):
        """Get the latitude for a given location ID."""
        location = next((loc for loc in LOCATIONS if loc["id"] == location_id), None)
        return location.get("latitude") if location else None

    async def _get_uv_index(self, retries=5, delay=2):
        """Fetch the current UV index from the UV sensor, with retries."""
        for attempt in range(1, retries + 1):
            try:
                if (
                    not hasattr(self._uv_sensor, "entity_id")
                    or not self._uv_sensor.entity_id
                ):
                    _LOGGER.debug(
                        "UV sensor not ready (attempt %d/%d), retrying in %ds...",
                        attempt,
                        retries,
                        delay,
                    )
                else:
                    uv_state = self.hass.states.get(self._uv_sensor.entity_id)
                    if uv_state and uv_state.state not in (
                        None,
                        "unknown",
                        "unavailable",
                    ):
                        uv_index = uv_state.attributes.get("current_uv")
                        if uv_index is not None:
                            _LOGGER.debug(
                                "UV index successfully retrieved: %s (attempt %d)",
                                uv_index,
                                attempt,
                            )
                            return int(round(float(uv_index)))
                    else:
                        _LOGGER.debug(
                            "UV sensor state unavailable (attempt %d/%d), retrying in %ds...",
                            attempt,
                            retries,
                            delay,
                        )
            except Exception as e:
                _LOGGER.warning(
                    "Error retrieving UV index on attempt %d: %s", attempt, e
                )

            # Only wait if not on last attempt
            if attempt < retries:
                await asyncio.sleep(delay)

        _LOGGER.debug("UV index unavailable after %d attempts", retries)
        return None

    def _parse_safe_times(self, results):
        safe_times = {
            "direkt solljus": None,
            "lite skugga": None,
            "mycket skugga": None,
        }
        for item in results:
            desc = item.get("shadowDescription", "").lower()
            for key in safe_times:
                if key in desc:
                    safe_times[key] = item.get("safeTime")
        return safe_times

    async def async_update(self):
        """Get the latest data from the API and update the state."""

        latitude = self._get_location_latitude(self._location)
        if not latitude:
            _LOGGER.error("Latitude not found for location: %s", self._location)
            self._attr_available = False
            return

        date_str = datetime.now().strftime("%Y-%m-%d")
        hour_str = str(datetime.now().hour)

        payload = {
            "skintypeId": str(self._skin_type),
            "latitude": latitude,
            "dateStr": date_str,
            "hour": hour_str,
        }

        url = "https://www.stralsakerhetsmyndigheten.se/api/v1/suntime/calculate"
        _LOGGER.debug("Sending request to Sun Time API (/calculate): %s", payload)

        try:
            async with self._session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    _LOGGER.debug(
                        "Received response from Sun Time API (/calculate): %s", data
                    )

                    safe_times = self._parse_safe_times(
                        data.get("result", {}).get("safeTimeResults", [])
                    )

                    self._attr_native_value = safe_times.get("direkt solljus")
                    self._attr_extra_state_attributes["shade_direct_sun"] = (
                        safe_times.get("direkt solljus")
                    )
                    self._attr_extra_state_attributes["shade_partial"] = safe_times.get(
                        "lite skugga"
                    )
                    self._attr_extra_state_attributes["shade_full"] = safe_times.get(
                        "mycket skugga"
                    )
                    self._attr_extra_state_attributes["last_updated"] = (
                        dt_util.utcnow().isoformat()
                    )
                    self._attr_available = True
                else:
                    _LOGGER.error(
                        "Failed to fetch Sun Time API (/calculate) response: %s",
                        response.status,
                    )
                    self._attr_native_value = None
                    self._attr_available = False
                    return
        except Exception as e:
            _LOGGER.error("Error calling Sun Time API (/calculate): %s", e)
            self._attr_available = False
            return

        # Enrich with /calculatewithindex if UV index is available
        uv_index = await self._get_uv_index()
        if uv_index is None:
            _LOGGER.debug(
                "Skipping Sun Time API (/calculatewithindex) due to unavailable UV index."
            )
            return

        payload = {
            "skintypeId": str(self._skin_type),
            "uvIndex": str(uv_index),
        }

        url = (
            "https://www.stralsakerhetsmyndigheten.se/api/v1/suntime/calculatewithindex"
        )
        _LOGGER.debug(
            "Sending request to Sun Time API (/calculatewithindex): %s", payload
        )

        try:
            async with self._session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    _LOGGER.debug(
                        "Received response from Sun Time API (/calculatewithindex): %s",
                        data,
                    )

                    safe_times = self._parse_safe_times(
                        data.get("result", {}).get("safeTimeResults", [])
                    )

                    self._attr_extra_state_attributes["i_shade_direct_sun"] = (
                        safe_times.get("direkt solljus")
                    )
                    self._attr_extra_state_attributes["i_shade_partial"] = (
                        safe_times.get("lite skugga")
                    )
                    self._attr_extra_state_attributes["i_shade_full"] = safe_times.get(
                        "mycket skugga"
                    )
                else:
                    _LOGGER.warning(
                        "Failed to fetch Sun Time API (/calculatewithindex) response: %s",
                        response.status,
                    )
        except Exception as e:
            _LOGGER.warning("Error calling Sun Time API (/calculatewithindex): %s", e)
