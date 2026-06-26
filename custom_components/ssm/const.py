"""Constants for the Swedish Radiation Safety Authority integration."""

from __future__ import annotations

from typing import Final, NotRequired, TypedDict

DOMAIN: Final = "ssm"

CONF_STATION: Final = "station"
CONF_LOCATION: Final = "location"
CONF_SKIN_TYPE: Final = "skin_type"

DEFAULT_NAME: Final = "SSM"

MANUFACTURER: Final = "Swedish Radiation Safety Authority"
MODEL: Final = "Radiation and UV Monitor"

RADIATION_HISTORY_URL: Final = (
    "https://karttjanst.ssm.se/data/getHistoryForStation"
)
UV_INDEX_URL: Final = (
    "https://www.stralsakerhetsmyndigheten.se/api/uvindex/{location}"
)
SUN_TIME_CALCULATE_URL: Final = (
    "https://www.stralsakerhetsmyndigheten.se/api/v1/suntime/calculate"
)
SUN_TIME_CALCULATE_WITH_INDEX_URL: Final = (
    "https://www.stralsakerhetsmyndigheten.se/api/v1/suntime/calculatewithindex"
)


class StationDescription(TypedDict):
    """Radiation measurement station description."""

    id: str
    name: str


class LocationDescription(TypedDict):
    """UV index and optional sun-time location description."""

    id: str
    name: str
    api_name: str
    sun_time_latitude: NotRequired[float]
    sun_time_longitude: NotRequired[float]


class SkinTypeDescription(TypedDict):
    """Skin type description."""

    id: str
    name: str


STATIONS: Final[list[StationDescription]] = [
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

LOCATIONS: Final[list[LocationDescription]] = [
    {
        "id": "sverige-abisko",
        "name": "Abisko",
        "api_name": "Sverige (Abisko)",
    },
    {
        "id": "sverige-gotland",
        "name": "Gotland",
        "api_name": "Sverige (Gotland)",
        "sun_time_latitude": 57.4716204656831,
        "sun_time_longitude": 18.4844815904125,
    },
    {
        "id": "sverige-gavle",
        "name": "Gävle",
        "api_name": "Sverige (Gävle)",
    },
    {
        "id": "sverige-goteborg",
        "name": "Göteborg",
        "api_name": "Sverige (Göteborg)",
        "sun_time_latitude": 57.7095511309657,
        "sun_time_longitude": 11.9623858055224,
    },
    {
        "id": "sverige-halmstad",
        "name": "Halmstad",
        "api_name": "Sverige (Halmstad)",
    },
    {
        "id": "sverige-idre-fjall",
        "name": "Idre Fjäll",
        "api_name": "Sverige (Idre Fjäll)",
    },
    {
        "id": "sverige-jonkoping",
        "name": "Jönköping",
        "api_name": "Sverige (Jönköping)",
    },
    {
        "id": "sverige-karlstad",
        "name": "Karlstad",
        "api_name": "Sverige (Karlstad)",
    },
    {
        "id": "sverige-kebnekaise",
        "name": "Kebnekaise",
        "api_name": "Sverige (Kebnekaise)",
    },
    {
        "id": "sverige-malmo",
        "name": "Malmö",
        "api_name": "Sverige (Malmö)",
        "sun_time_latitude": 55.6054274073227,
        "sun_time_longitude": 12.9816074029767,
    },
    {
        "id": "sverige-mora",
        "name": "Mora",
        "api_name": "Sverige (Mora)",
    },
    {
        "id": "sverige-polcirkeln",
        "name": "Polcirkeln",
        "api_name": "Sverige (Polcirkeln)",
        "sun_time_latitude": 66.5690137250601,
        "sun_time_longitude": 21.0187913396622,
    },
    {
        "id": "sverige-riksgransen",
        "name": "Riksgränsen",
        "api_name": "Sverige (Riksgränsen)",
    },
    {
        "id": "sverige-stockholm",
        "name": "Stockholm",
        "api_name": "Sverige (Stockholm)",
        "sun_time_latitude": 59.3325654896463,
        "sun_time_longitude": 18.0669553866814,
    },
    {
        "id": "sverige-sundsvall",
        "name": "Sundsvall",
        "api_name": "Sverige (Sundsvall)",
    },
    {
        "id": "sverige-salen",
        "name": "Sälen",
        "api_name": "Sverige (Sälen)",
    },
    {
        "id": "sverige-tanndalen",
        "name": "Tänndalen",
        "api_name": "Sverige (Tänndalen)",
    },
    {
        "id": "sverige-umea",
        "name": "Umeå",
        "api_name": "Sverige (Umeå)",
    },
    {
        "id": "sverige-vemdalen",
        "name": "Vemdalen",
        "api_name": "Sverige (Vemdalen)",
    },
    {
        "id": "sverige-oland",
        "name": "Öland",
        "api_name": "Sverige (Öland)",
        "sun_time_latitude": 56.6661070100662,
        "sun_time_longitude": 16.61967362829,
    },
    {
        "id": "sverige-orebro",
        "name": "Örebro",
        "api_name": "Sverige (Örebro)",
    },
    {
        "id": "sverige-ostersund",
        "name": "Östersund",
        "api_name": "Sverige (Östersund)",
        "sun_time_latitude": 63.177187907826,
        "sun_time_longitude": 14.6358205656499,
    },
]

SKIN_TYPES: Final[list[SkinTypeDescription]] = [
    {"id": "1", "name": "Type 1 (Very fair, burns easily)"},
    {"id": "2", "name": "Type 2 (Fair, burns easily)"},
    {"id": "3", "name": "Type 3 (Medium, sometimes burns)"},
    {"id": "4", "name": "Type 4 (Olive, rarely burns)"},
    {"id": "5", "name": "Type 5 (Brown, very rarely burns)"},
    {"id": "6", "name": "Type 6 (Dark brown, never burns)"},
]
