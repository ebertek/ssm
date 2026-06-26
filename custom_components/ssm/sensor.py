"""Sensor platform for Swedish Radiation Safety Authority integration."""

# pylint: disable=C0301, E0401, R0902, R0903, R0911, R0912, R0913, R0914, R0915, R0917, W0718

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import quote
from zoneinfo import ZoneInfo

from aiohttp import ClientError, ClientSession  # type: ignore
from homeassistant.components.sensor import (  # type: ignore
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry  # type: ignore
from homeassistant.const import CONF_NAME, UnitOfTime  # type: ignore
from homeassistant.core import HomeAssistant  # type: ignore
from homeassistant.helpers.aiohttp_client import async_get_clientsession  # type: ignore
from homeassistant.helpers.device_registry import DeviceInfo  # type: ignore
from homeassistant.helpers.entity_platform import (  # type: ignore
    AddConfigEntryEntitiesCallback,
)

from .const import (
    CONF_LOCATION,
    CONF_SKIN_TYPE,
    CONF_STATION,
    DOMAIN,
    LOCATIONS,
    MANUFACTURER,
    MODEL,
    RADIATION_HISTORY_URL,
    SUN_TIME_CALCULATE_URL,
    SUN_TIME_CALCULATE_WITH_INDEX_URL,
    UV_INDEX_URL,
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=30)
STOCKHOLM_TIMEZONE = ZoneInfo("Europe/Stockholm")


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up SSM sensors based on a config entry."""
    name = _entry_string_value(config_entry, CONF_NAME, "SSM") or "SSM"
    station = _entry_string_value(config_entry, CONF_STATION)
    location = _entry_string_value(config_entry, CONF_LOCATION)
    skin_type = _entry_string_value(config_entry, CONF_SKIN_TYPE)

    session = async_get_clientsession(hass)
    entities: list[SensorEntity] = []

    if station:
        entities.append(
            SSMRadiationSensor(
                session=session,
                name=name,
                station=station,
                entry_id=config_entry.entry_id,
            )
        )

    if location:
        uv_sensor = SSMUVIndexSensor(
            session=session,
            name=name,
            location=location,
            entry_id=config_entry.entry_id,
        )
        entities.append(uv_sensor)

        if skin_type:
            entities.append(
                SSMSunTimeSensor(
                    session=session,
                    name=name,
                    skin_type=skin_type,
                    uv_sensor=uv_sensor,
                    location=location,
                    entry_id=config_entry.entry_id,
                )
            )

    if entities:
        async_add_entities(entities, update_before_add=True)


def _last_updated_iso() -> str:
    """Return current UTC timestamp as ISO string."""
    return datetime.now(UTC).isoformat()


def _entry_string_value(
    config_entry: ConfigEntry,
    key: str,
    default: str | None = None,
) -> str | None:
    """Return a config entry option or data value as a string."""
    value = config_entry.options.get(key, config_entry.data.get(key, default))

    if value is None:
        return default

    return str(value)


def _to_number(value: Any) -> int | float | None:
    """Convert a value to int or float if possible."""
    if value is None or isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        return value

    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None

        try:
            number = float(value)
        except ValueError:
            return None

        if number.is_integer():
            return int(number)

        return number

    return None


def _device_info(entry_id: str, name: str) -> DeviceInfo:
    """Return device info used by all SSM sensors."""
    return DeviceInfo(
        identifiers={(DOMAIN, entry_id)},
        name=name,
        manufacturer=MANUFACTURER,
        model=MODEL,
    )


class SSMRadiationSensor(SensorEntity):
    """Representation of a SSM Radiation Sensor."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "nSv/h"
    _attr_icon = "mdi:radioactive"
    _attr_translation_key = "radiation_level"
    _unrecorded_attributes = frozenset({"last_updated"})

    def __init__(
        self,
        session: ClientSession,
        name: str,
        station: str,
        entry_id: str,
    ) -> None:
        """Initialize the sensor."""
        self._session = session
        self._station = station

        self._attr_name = "Radiation Level"
        self._attr_unique_id = f"{entry_id}_radiation"
        self._attr_native_value = None
        self._attr_available = True
        self._attr_device_info = _device_info(entry_id, name)
        self._attr_extra_state_attributes: dict[str, Any] = {
            "min_level": None,
            "max_level": None,
            "avg_level": None,
            "last_updated": None,
        }

    async def async_update(self) -> None:
        """Get the latest data from the API and update the state."""
        now = datetime.now(STOCKHOLM_TIMEZONE)
        is_dst = bool(now.dst())

        def get_time_range(strategy: str) -> tuple[int, int]:
            """Return query time range in Unix milliseconds."""
            end = now.replace(minute=0, second=0, microsecond=0)

            if strategy == "normal":
                start = end - timedelta(hours=3 if is_dst else 2)
            elif strategy == "fallback":
                start = end - timedelta(hours=4 if is_dst else 3)
            elif strategy == "midnight":
                start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                raise ValueError(f"Unknown strategy: {strategy}")

            _LOGGER.debug(
                "Query window for Radiation API (%s): %s to %s",
                strategy,
                start,
                end,
            )

            return int(start.timestamp() * 1000), int(end.timestamp() * 1000)

        try:
            for strategy in ("normal", "fallback", "midnight"):
                start_timestamp, end_timestamp = get_time_range(strategy)

                url = (
                    f"{RADIATION_HISTORY_URL}"
                    f"?locationId={self._station}"
                    f"&start={start_timestamp}"
                    f"&end={end_timestamp}"
                )

                _LOGGER.debug("Sending request to Radiation API: %s", url)

                async with self._session.get(url) as response:
                    if response.status != 200:
                        _LOGGER.debug(
                            "Failed to fetch radiation data from SSM API: %s",
                            response.status,
                        )
                        continue

                    data = await response.json()
                    _LOGGER.debug("Received response from Radiation API: %s", data)

                values = data.get("values")
                if not values:
                    _LOGGER.debug(
                        "No radiation values received from SSM Radiation API: %s",
                        data,
                    )
                    continue

                radiation_values = [
                    item[1]
                    for item in values
                    if isinstance(item, (list, tuple)) and len(item) > 1
                ]

                if not radiation_values:
                    _LOGGER.debug(
                        "Invalid radiation values received from SSM Radiation API: %s",
                        data,
                    )
                    continue

                valid_values = [
                    float(value)
                    for value in (_to_number(value) for value in radiation_values)
                    if value is not None
                ]

                if not valid_values:
                    _LOGGER.debug(
                        "No valid numeric radiation values from Radiation API: %s",
                        radiation_values,
                    )
                    continue

                # API values are μSv/h. Sensor exposes nSv/h.
                latest_value: float = valid_values[-1]
                min_value: float = min(valid_values)
                max_value: float = max(valid_values)
                avg_value: float = sum(valid_values) / len(valid_values)

                self._attr_native_value = round(latest_value * 1000)
                self._attr_extra_state_attributes["min_level"] = round(min_value * 1000)
                self._attr_extra_state_attributes["max_level"] = round(max_value * 1000)
                self._attr_extra_state_attributes["avg_level"] = round(avg_value * 1000)
                self._attr_extra_state_attributes["last_updated"] = _last_updated_iso()
                self._attr_available = True
                return

            _LOGGER.warning(
                "Failed to retrieve valid radiation data after all fallback attempts."
            )
            self._attr_available = False

        except (ClientError, TimeoutError, ValueError, KeyError, TypeError) as error:
            _LOGGER.warning("Error updating SSM Radiation sensor: %s", error)
            self._attr_available = False
        except Exception as error:
            _LOGGER.exception(
                "Unexpected error updating SSM Radiation sensor: %s", error
            )
            self._attr_available = False


class SSMUVIndexSensor(SensorEntity):
    """Representation of a SSM UV Index Sensor."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:sun-wireless"
    _attr_translation_key = "uv_index"
    _unrecorded_attributes = frozenset({"hourly_forecast", "last_updated"})

    def __init__(
        self, session: ClientSession, name: str, location: str, entry_id: str
    ) -> None:
        """Initialize the sensor."""
        self._session = session
        self._location = location

        self._attr_name = "UV Index"
        self._attr_unique_id = f"{entry_id}_uv_index"
        self._attr_native_value = None
        self._attr_available = True
        self._attr_device_info = _device_info(entry_id, name)
        self._attr_extra_state_attributes: dict[str, Any] = {
            "current_uv": None,
            "max_uv_today": None,
            "max_uv_time": None,
            "max_uv_tomorrow": None,
            "hourly_forecast": [],
            "risk_level": None,
            "last_updated": None,
        }

    @property
    def current_uv(self) -> int | float | None:
        """Return current UV index."""
        return _to_number(self._attr_extra_state_attributes.get("current_uv"))

    @staticmethod
    def _get_risk_level(uv_index: int | float) -> str:
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

    @staticmethod
    def _get_icon(uv_index: int | float) -> str:
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

    @staticmethod
    def _get_api_location_name(location_id: str) -> str | None:
        """Get the API location name for a given location ID."""
        location = next((loc for loc in LOCATIONS if loc["id"] == location_id), None)
        return location["api_name"] if location else None

    async def async_update(self) -> None:
        """Get the latest data from the API and update the state."""
        try:
            now = datetime.now(STOCKHOLM_TIMEZONE)
            offset = "-2" if now.dst() else "-1"

            api_location = self._get_api_location_name(self._location)
            if api_location is None:
                _LOGGER.error("API location not found for location: %s", self._location)
                self._attr_available = False
                return

            encoded_location = quote(api_location, safe="")
            url = f"{UV_INDEX_URL.format(location=encoded_location)}?offset={offset}"

            _LOGGER.debug("Sending request to UV Index API: %s", url)

            async with self._session.get(url) as response:
                if response.status != 200:
                    _LOGGER.error(
                        "Failed to fetch UV index data from SSM API: %s",
                        response.status,
                    )
                    self._attr_available = False
                    return

                data = await response.json()
                _LOGGER.debug("Received response from UV Index API: %s", data)

            location_data = data["response"]["location"]
            dates = location_data["date"]

            if not dates:
                _LOGGER.error(
                    "No UV date data received from SSM UV Index API: %s", data
                )
                self._attr_available = False
                return

            today_data = dates[0]
            hourly_data = today_data["hourlyUvIndex"]

            current_hour = now.hour
            if current_hour >= len(hourly_data):
                _LOGGER.error(
                    "UV hourly data does not contain current hour %s: %s",
                    current_hour,
                    hourly_data,
                )
                self._attr_available = False
                return

            current_uv: int | float | None = _to_number(hourly_data[current_hour])
            max_uv_today: int | float | None = _to_number(today_data["maxUvIndex"])

            if current_uv is None or max_uv_today is None:
                _LOGGER.error(
                    "Invalid UV values received from SSM UV Index API: %s",
                    data,
                )
                self._attr_available = False
                return

            max_uv_time = today_data.get("maxUvIndexTime")
            max_time_formatted: str | None = None
            if max_uv_time:
                max_time_obj = datetime.strptime(max_uv_time, "%Y-%m-%dT%H:%M:%S")
                max_time_formatted = max_time_obj.strftime("%H:%M")

            max_uv_tomorrow: int | float | None = None
            if len(dates) > 1:
                max_uv_tomorrow = _to_number(dates[1].get("maxUvIndex"))

            hourly_forecast = [
                {
                    "time": f"{hour:02d}:00",
                    "uv_index": _to_number(uv),
                }
                for hour, uv in enumerate(hourly_data)
            ]

            self._attr_native_value = current_uv
            self._attr_extra_state_attributes["current_uv"] = current_uv
            self._attr_extra_state_attributes["max_uv_today"] = max_uv_today
            self._attr_extra_state_attributes["max_uv_time"] = max_time_formatted
            self._attr_extra_state_attributes["max_uv_tomorrow"] = max_uv_tomorrow
            self._attr_extra_state_attributes["hourly_forecast"] = hourly_forecast
            self._attr_extra_state_attributes["risk_level"] = self._get_risk_level(
                max_uv_today
            )
            self._attr_extra_state_attributes["last_updated"] = _last_updated_iso()
            self._attr_icon = self._get_icon(current_uv)
            self._attr_available = True

        except (ClientError, TimeoutError, ValueError, KeyError, TypeError) as error:
            _LOGGER.error("Error updating SSM UV Index sensor: %s", error)
            self._attr_available = False
        except Exception as error:
            _LOGGER.exception(
                "Unexpected error updating SSM UV Index sensor: %s", error
            )
            self._attr_available = False


class SSMSunTimeSensor(SensorEntity):
    """Representation of a SSM Min Soltid Sensor."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_icon = "mdi:sun-clock"
    _attr_translation_key = "min_soltid"
    _unrecorded_attributes = frozenset({"last_updated"})

    def __init__(
        self,
        session: ClientSession,
        name: str,
        skin_type: str,
        uv_sensor: SSMUVIndexSensor,
        location: str,
        entry_id: str,
    ) -> None:
        """Initialize the sensor."""
        self._session = session
        self._skin_type = skin_type
        self._uv_sensor = uv_sensor
        self._location = location

        self._attr_name = "Min soltid"
        self._attr_unique_id = f"{entry_id}_sun_time"
        self._attr_native_value = None
        self._attr_available = True
        self._attr_device_info = _device_info(entry_id, name)
        self._attr_extra_state_attributes: dict[str, Any] = {
            "shade_direct_sun": None,
            "shade_partial": None,
            "shade_full": None,
            "i_shade_direct_sun": None,
            "i_shade_partial": None,
            "i_shade_full": None,
            "last_updated": None,
        }

    @staticmethod
    def _get_sun_time_coordinates(
        location_id: str,
    ) -> tuple[float | None, float | None]:
        """Get official sun-time latitude and longitude for a given location ID."""
        location = next((loc for loc in LOCATIONS if loc["id"] == location_id), None)

        if location is None:
            return None, None

        return (
            location.get("sun_time_latitude"),
            location.get("sun_time_longitude"),
        )

    def _get_uv_index(self) -> int | None:
        """Return the current UV index from the UV sensor."""
        current_uv = self._uv_sensor.current_uv

        if current_uv is None:
            _LOGGER.debug("UV index unavailable from UV sensor")
            return None

        return int(round(float(current_uv)))

    @staticmethod
    def _parse_safe_times(
        results: list[dict[str, Any]],
    ) -> dict[str, int | float | None]:
        """Parse safe times from the SSM sun time API response."""
        safe_times: dict[str, int | float | None] = {
            "direkt solljus": None,
            "lite skugga": None,
            "mycket skugga": None,
        }

        for item in results:
            desc = item.get("shadowDescription", "").lower()

            for key in safe_times:
                if key in desc:
                    safe_times[key] = _to_number(item.get("safeTime"))

        return safe_times

    async def _update_from_location_calculation(self, now: datetime) -> bool:
        """Update sun-time values from location/date/hour based calculation."""
        latitude, longitude = self._get_sun_time_coordinates(self._location)

        if latitude is None or longitude is None:
            _LOGGER.debug(
                "No official sun-time coordinates for location %s; "
                "skipping location-based calculation.",
                self._location,
            )
            self._attr_extra_state_attributes["shade_direct_sun"] = None
            self._attr_extra_state_attributes["shade_partial"] = None
            self._attr_extra_state_attributes["shade_full"] = None
            return False

        payload = {
            "skintypeId": int(self._skin_type),
            "latitude": latitude,
            "longitude": longitude,
            "dateStr": now.strftime("%Y-%m-%d"),
            "hour": now.hour,
        }

        _LOGGER.debug("Sending request to Sun Time API (/calculate): %s", payload)

        try:
            async with self._session.post(
                SUN_TIME_CALCULATE_URL,
                json=payload,
            ) as response:
                if response.status != 200:
                    _LOGGER.warning(
                        "Failed to fetch Sun Time API (/calculate) response: %s",
                        response.status,
                    )
                    self._attr_extra_state_attributes["shade_direct_sun"] = None
                    self._attr_extra_state_attributes["shade_partial"] = None
                    self._attr_extra_state_attributes["shade_full"] = None
                    return False

                data = await response.json()
                _LOGGER.debug(
                    "Received response from Sun Time API (/calculate): %s",
                    data,
                )

            safe_times = self._parse_safe_times(
                data.get("result", {}).get("safeTimeResults", [])
            )

            direct_sun: int | float | None = safe_times.get("direkt solljus")
            partial_shade: int | float | None = safe_times.get("lite skugga")
            full_shade: int | float | None = safe_times.get("mycket skugga")

            if direct_sun is None:
                _LOGGER.warning(
                    "Location-based Sun Time API response did not contain "
                    "direct-sun safe time: %s",
                    data,
                )
                self._attr_extra_state_attributes["shade_direct_sun"] = None
                self._attr_extra_state_attributes["shade_partial"] = None
                self._attr_extra_state_attributes["shade_full"] = None
                return False

            # Main state is location/date/hour based direct-sun safe time.
            self._attr_native_value = direct_sun
            self._attr_extra_state_attributes["shade_direct_sun"] = direct_sun
            self._attr_extra_state_attributes["shade_partial"] = partial_shade
            self._attr_extra_state_attributes["shade_full"] = full_shade
            self._attr_extra_state_attributes["last_updated"] = _last_updated_iso()

            return True

        except (ClientError, TimeoutError, ValueError, KeyError, TypeError) as error:
            _LOGGER.warning("Error calling Sun Time API (/calculate): %s", error)
            self._attr_extra_state_attributes["shade_direct_sun"] = None
            self._attr_extra_state_attributes["shade_partial"] = None
            self._attr_extra_state_attributes["shade_full"] = None
            return False
        except Exception as error:
            _LOGGER.exception(
                "Unexpected error calling Sun Time API (/calculate): %s",
                error,
            )
            self._attr_extra_state_attributes["shade_direct_sun"] = None
            self._attr_extra_state_attributes["shade_partial"] = None
            self._attr_extra_state_attributes["shade_full"] = None
            return False

    async def _update_from_index_calculation(
        self,
        prefer_as_state: bool,
    ) -> bool:
        """Update sun-time values from current UV-index based calculation."""
        uv_index = self._get_uv_index()
        if uv_index is None:
            _LOGGER.debug(
                "Skipping Sun Time API (/calculatewithindex) due to "
                "unavailable UV index."
            )
            self._attr_extra_state_attributes["i_shade_direct_sun"] = None
            self._attr_extra_state_attributes["i_shade_partial"] = None
            self._attr_extra_state_attributes["i_shade_full"] = None
            return False

        payload = {
            "skintypeId": int(self._skin_type),
            "uvIndex": uv_index,
        }

        _LOGGER.debug(
            "Sending request to Sun Time API (/calculatewithindex): %s",
            payload,
        )

        try:
            async with self._session.post(
                SUN_TIME_CALCULATE_WITH_INDEX_URL,
                json=payload,
            ) as response:
                if response.status != 200:
                    _LOGGER.warning(
                        "Failed to fetch Sun Time API (/calculatewithindex) "
                        "response: %s",
                        response.status,
                    )
                    self._attr_extra_state_attributes["i_shade_direct_sun"] = None
                    self._attr_extra_state_attributes["i_shade_partial"] = None
                    self._attr_extra_state_attributes["i_shade_full"] = None
                    return False

                data = await response.json()
                _LOGGER.debug(
                    "Received response from Sun Time API (/calculatewithindex): %s",
                    data,
                )

            safe_times = self._parse_safe_times(
                data.get("result", {}).get("safeTimeResults", [])
            )

            index_direct_sun: int | float | None = safe_times.get("direkt solljus")
            index_partial_shade: int | float | None = safe_times.get("lite skugga")
            index_full_shade: int | float | None = safe_times.get("mycket skugga")

            if index_direct_sun is None:
                _LOGGER.warning(
                    "Index-based Sun Time API response did not contain "
                    "direct-sun safe time: %s",
                    data,
                )
                self._attr_extra_state_attributes["i_shade_direct_sun"] = None
                self._attr_extra_state_attributes["i_shade_partial"] = None
                self._attr_extra_state_attributes["i_shade_full"] = None
                return False

            self._attr_extra_state_attributes["i_shade_direct_sun"] = index_direct_sun
            self._attr_extra_state_attributes["i_shade_partial"] = index_partial_shade
            self._attr_extra_state_attributes["i_shade_full"] = index_full_shade
            self._attr_extra_state_attributes["last_updated"] = _last_updated_iso()

            if prefer_as_state:
                # Fallback mode: no official sun-time coordinates exist.
                # Use current-UV-index safe time as the entity state.
                self._attr_native_value = index_direct_sun

            return True

        except (ClientError, TimeoutError, ValueError, KeyError, TypeError) as error:
            _LOGGER.warning(
                "Error calling Sun Time API (/calculatewithindex): %s",
                error,
            )
            self._attr_extra_state_attributes["i_shade_direct_sun"] = None
            self._attr_extra_state_attributes["i_shade_partial"] = None
            self._attr_extra_state_attributes["i_shade_full"] = None
            return False
        except Exception as error:
            _LOGGER.exception(
                "Unexpected error calling Sun Time API (/calculatewithindex): %s",
                error,
            )
            self._attr_extra_state_attributes["i_shade_direct_sun"] = None
            self._attr_extra_state_attributes["i_shade_partial"] = None
            self._attr_extra_state_attributes["i_shade_full"] = None
            return False

    async def async_update(self) -> None:
        """Get the latest data from the API and update the state."""
        now = datetime.now(STOCKHOLM_TIMEZONE)

        location_updated = await self._update_from_location_calculation(now)
        index_updated = await self._update_from_index_calculation(
            prefer_as_state=not location_updated
        )

        self._attr_available = location_updated or index_updated

        if not self._attr_available:
            self._attr_native_value = None
            self._attr_extra_state_attributes["last_updated"] = _last_updated_iso()
