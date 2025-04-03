"""Sensor platform for Swedish Radiation Safety Authority integration."""
import logging
from datetime import datetime
import time
from urllib.parse import quote

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.const import CONF_NAME, UnitOfTime
import homeassistant.util.dt as dt_util

from .const import DOMAIN, CONF_LOCATION_ID, CONF_LOCATION, CONF_SKIN_TYPE

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up SSM sensors based on a config entry."""
    name = entry.data.get(CONF_NAME)
    location_id = entry.data.get(CONF_LOCATION_ID)
    location = entry.data.get(CONF_LOCATION)
    skintype = entry.data.get(CONF_SKIN_TYPE)

    session = async_get_clientsession(hass)

    uv_sensor = SSMUVIndexSensor(hass, session, name, location, entry.entry_id)
    radiation_sensor = SSMRadiationSensor(hass, session, name, location_id, entry.entry_id)
    sun_time_sensor = SSMSunTimeSensor(hass, session, name, skintype, entry.entry_id, uv_sensor.entity_id)
    sensors = [
        uv_sensor,
        radiation_sensor,
        sun_time_sensor
    ]
    async_add_entities(sensors, True)

class SSMRadiationSensor(SensorEntity):
    """Representation of a SSM Radiation Sensor."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "nSv/h"

    def __init__(self, hass, session, name, location_id, entry_id):
        """Initialize the sensor."""
        self.hass = hass
        self._session = session
        self._attr_name = "Radiation Level"
        self._location_id = location_id
        self._entry_id = entry_id

        self._attr_unique_id = f"{entry_id}_radiation"
        self._attr_native_value = None
        self._attr_icon = "mdi:radioactive"
        self._attr_available = True
        self._attr_extra_state_attributes = {
            "min_level": None,
            "max_level": None,
            "avg_level": None,
            "last_updated": None,
            "raw_data": [],
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
            # Calculate midnight timestamp in UTC (milliseconds)
            now = dt_util.utcnow()
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            start_timestamp = int(start_of_day.timestamp() * 1000)
            end_timestamp = int(now.timestamp() * 1000)

            url = f"https://karttjanst.ssm.se/data/getHistoryForStation?locationId={self._location_id}&start={start_timestamp}&end={end_timestamp}"

            async with self._session.get(url) as response:
                if response.status == 200:
                    data = await response.json()

                    if "values" in data and data["values"]:
                        values = data["values"]
                        radiation_values = [item[1] for item in values]  # Extract radiation values

                        # Convert from μSv/h to nSv/h
                        self._attr_native_value = round(radiation_values[-1] * 1000)  # Most recent value
                        self._attr_extra_state_attributes["min_level"] = round(min(radiation_values) * 1000)
                        self._attr_extra_state_attributes["max_level"] = round(max(radiation_values) * 1000)
                        self._attr_extra_state_attributes["avg_level"] = round(sum(radiation_values) / len(radiation_values) * 1000)
                        self._attr_extra_state_attributes["raw_data"] = values
                        self._attr_extra_state_attributes["last_updated"] = dt_util.utcnow().isoformat()
                        self._attr_available = True
                    else:
                        _LOGGER.error("Invalid data format received from SSM Radiation API")
                        self._attr_available = False
                else:
                    _LOGGER.error("Failed to fetch radiation data from SSM API: %s", response.status)
                    self._attr_available = False
        except Exception as e:
            _LOGGER.error("Error updating SSM Radiation sensor: %s", e)
            self._attr_available = False


class SSMUVIndexSensor(SensorEntity):
    """Representation of a SSM UV Index Sensor."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "UV"

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
            return "Extreme"
        elif uv_index >= 8:
            return "Very High"
        elif uv_index >= 6:
            return "High"
        elif uv_index >= 3:
            return "Moderate"
        elif uv_index > 0:
            return "Low"
        return "None"

    def _get_icon(self, uv_index):
        """Get the appropriate icon based on UV index value."""
        if uv_index >= 8:
            return "mdi:weather-sunny-alert"
        elif uv_index >= 6:
            return "mdi:weather-sunny"
        elif uv_index >= 3:
            return "mdi:weather-partly-sunny"
        elif uv_index > 0:
            return "mdi:weather-sunny-off"
        else:
            return "mdi:weather-night"

    def _map_location_id_to_api_value(self, location_id):
        """Map the location ID to the API value."""
        mapping = {
            "sverige-gotland": "Sverige (Gotland)",
            "sverige-goteborg": "Sverige (Göteborg)",
            "sverige-malmo": "Sverige (Malmö)",
            "sverige-stockholm": "Sverige (Stockholm)",
            "sverige-polcirkeln": "Sverige (polcirkeln)",
            "sverige-oland": "Sverige (Öland)",
            "sverige-ostersund": "Sverige (Östersund)",
        }
        return mapping.get(location_id, location_id)

    async def async_update(self):
        """Get the latest data from the API and update the state."""
        try:
            # Determine if DST is in effect to set correct offset
            is_dst = time.localtime().tm_isdst > 0
            offset = "-2" if is_dst else "-1"

            # Map location ID to API value and URL encode it
            api_location = self._map_location_id_to_api_value(self._location)
            encoded_location = quote(api_location)
            url = f"https://www.stralsakerhetsmyndigheten.se/api/uvindex/{encoded_location}?offset={offset}"

            async with self._session.get(url) as response:
                if response.status == 200:
                    data = await response.json()

                    if "response" in data and "location" in data["response"] and "date" in data["response"]["location"]:
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
                        max_time_obj = datetime.strptime(max_uv_time, "%Y-%m-%dT%H:%M:%S")
                        max_time_formatted = max_time_obj.strftime("%H:%M")

                        # Get tomorrow's data if available
                        max_uv_tomorrow = None
                        if len(location_data["date"]) > 1:
                            max_uv_tomorrow = location_data["date"][1]["maxUvIndex"]

                        # Update state and attributes
                        self._attr_native_value = current_uv
                        self._attr_extra_state_attributes["current_uv"] = current_uv
                        self._attr_extra_state_attributes["max_uv_today"] = max_uv_today
                        self._attr_extra_state_attributes["max_uv_time"] = max_time_formatted
                        self._attr_extra_state_attributes["max_uv_tomorrow"] = max_uv_tomorrow
                        self._attr_extra_state_attributes["hourly_forecast"] = hourly_data
                        self._attr_extra_state_attributes["risk_level"] = self._get_risk_level(max_uv_today)
                        self._attr_extra_state_attributes["last_updated"] = dt_util.utcnow().isoformat()

                        # Update icon based on current UV value
                        self._attr_icon = self._get_icon(current_uv)

                        self._attr_available = True
                    else:
                        _LOGGER.error("Invalid data format received from SSM UV Index API")
                        self._attr_available = False
                else:
                    _LOGGER.error("Failed to fetch UV index data from SSM API: %s", response.status)
                    self._attr_available = False
        except Exception as e:
            _LOGGER.error("Error updating SSM UV Index sensor: %s", e)
            self._attr_available = False

class SSMSunTimeSensor(SensorEntity):
    """Representation of a SSM Min Soltid Sensor."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "minutes"
    _attr_icon = "mdi:weather-sunny"

    def __init__(self, hass, session, name, skintype, entry_id, uv_entity_id):
        """Initialize the sensor."""
        self.hass = hass
        self._session = session
        self._attr_name = "Min soltid"
        self._skintype = skintype
        self._entry_id = entry_id
        self._uv_entity_id = uv_entity_id  # Store UV entity ID

        self._attr_unique_id = f"{entry_id}_sun_time"
        self._attr_native_value = None
        self._attr_available = True
        self._attr_extra_state_attributes = {
            "shade_direct_sun": None,
            "shade_partial": None,
            "shade_full": None,
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
            # Get the latest UV index from the UV sensor
            uv_state = self.hass.states.get(self._uv_entity_id)
            if not uv_state or uv_state.state in (None, "unknown", "unavailable"):
                _LOGGER.warning("UV Index sensor state is unavailable or invalid, skipping Min Soltid update")
                self._attr_available = False
                return

            try:
                uv_index = int(float(uv_state.state))  # Convert to float to ensure correct formatting
            except ValueError:
                _LOGGER.warning("UV Index sensor state is not a valid number: %s", uv_state.state)
                self._attr_available = False
                return

            _LOGGER.debug("UV sensor entity ID: %s", self._uv_entity_id)
            _LOGGER.debug("Retrieved UV state: %s", uv_state.state if uv_state else "None")
            _LOGGER.debug("Converted UV index: %d", uv_index)

            # Prepare request payload
            payload = {
                "skintypeId": str(self._skintype),
                "uvIndex": str(uv_index),
            }

            url = "https://www.stralsakerhetsmyndigheten.se/api/v1/suntime/calculatewithindex"

            async with self._session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()

                    if "result" in data and "safeTimeResults" in data["result"]:
                        results = data["result"]["safeTimeResults"]
                        
                        # Check if shadowDescription is None before calling lower()
                        direct_sun = next((r for r in results if r.get("shadowDescription") and "direkt solljus" in r["shadowDescription"].lower()), None)
                        partial_shade = next((r for r in results if r.get("shadowDescription") and "lite skugga" in r["shadowDescription"].lower()), None)
                        full_shade = next((r for r in results if r.get("shadowDescription") and "mycket skugga" in r["shadowDescription"].lower()), None)

                        # Extract values using safeTime instead of safeTimeMinutes
                        self._attr_native_value = direct_sun["safeTime"] if direct_sun else None
                        self._attr_extra_state_attributes["shade_direct_sun"] = direct_sun["safeTime"] if direct_sun else None
                        self._attr_extra_state_attributes["shade_partial"] = partial_shade["safeTime"] if partial_shade else None
                        self._attr_extra_state_attributes["shade_full"] = full_shade["safeTime"] if full_shade else None
                        self._attr_extra_state_attributes["last_updated"] = dt_util.utcnow().isoformat()
                        self._attr_available = True
                    else:
                        _LOGGER.error("Invalid response from SSM Sun Time API")
                        self._attr_available = False
                else:
                    _LOGGER.error("Failed to fetch sun time data: %s", response.status)
                    self._attr_available = False
        except Exception as e:
            _LOGGER.error("Error updating Min Soltid sensor: %s", e)
            self._attr_available = False
