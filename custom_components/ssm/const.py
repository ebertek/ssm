"""Constants for the Swedish Radiation Safety Authority integration."""

# pylint: disable=C0301

DOMAIN = "ssm"

# Configuration constants
CONF_STATION = "station"
CONF_LOCATION = "location"
CONF_SKIN_TYPE = "skin_type"
DEFAULT_NAME = "SSM"

# Radiation measurement stations with their location IDs
STATIONS = [
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

# UV index measurement locations with their API names and values
LOCATIONS = [
    {
        "id": "sverige-abisko",
        "name": "Abisko",
        "api_name": "Sverige (Abisko)",
        "latitude": "68.4",
    },
    {
        "id": "sverige-gotland",
        "name": "Gotland",
        "api_name": "Sverige (Gotland)",
        "latitude": "57.621875",
    },
    {
        "id": "sverige-gavle",
        "name": "Gävle",
        "api_name": "Sverige (Gävle)",
        "latitude": "60.8",
    },
    {
        "id": "sverige-goteborg",
        "name": "Göteborg",
        "api_name": "Sverige (Göteborg)",
        "latitude": "57.70887",
    },
    {
        "id": "sverige-halmstad",
        "name": "Halmstad",
        "api_name": "Sverige (Halmstad)",
        "latitude": "56.8",
    },
    {
        "id": "sverige-idre-fjall",
        "name": "Idre Fjäll",
        "api_name": "Sverige (Idre Fjäll)",
        "latitude": "62",
    },
    {
        "id": "sverige-jonkoping",
        "name": "Jönköping",
        "api_name": "Sverige (Jönköping)",
        "latitude": "57.6",
    },
    {
        "id": "sverige-karlstad",
        "name": "Karlstad",
        "api_name": "Sverige (Karlstad)",
        "latitude": "59.2",
    },
    {
        "id": "sverige-kebnekaise",
        "name": "Kebnekaise",
        "api_name": "Sverige (Kebnekaise)",
        "latitude": "68",
    },
    {
        "id": "sverige-malmo",
        "name": "Malmö",
        "api_name": "Sverige (Malmö)",
        "latitude": "55.60498",
    },
    {
        "id": "sverige-mora",
        "name": "Mora",
        "api_name": "Sverige (Mora)",
        "latitude": "61.2",
    },
    {
        "id": "sverige-polcirkeln",
        "name": "Polcirkeln",
        "api_name": "Sverige (polcirkeln)",
        "latitude": "66.54772",
    },
    {
        "id": "sverige-riksgransen",
        "name": "Riksgränsen",
        "api_name": "Sverige (Riksgränsen)",
        "latitude": "68.4",
    },
    {
        "id": "sverige-stockholm",
        "name": "Stockholm",
        "api_name": "Sverige (Stockholm)",
        "latitude": "59.32893",
    },
    {
        "id": "sverige-sundsvall",
        "name": "Sundsvall",
        "api_name": "Sverige (Sundsvall)",
        "latitude": "62.4",
    },
    {
        "id": "sverige-salen",
        "name": "Sälen",
        "api_name": "Sverige (Sälen)",
        "latitude": "61.2",
    },
    {
        "id": "sverige-tanndalen",
        "name": "Tänndalen",
        "api_name": "Sverige (Tänndalen)",
        "latitude": "62.4",
    },
    {
        "id": "sverige-umea",
        "name": "Umeå",
        "api_name": "Sverige (Umeå)",
        "latitude": "64",
    },
    {
        "id": "sverige-vemdalen",
        "name": "Vemdalen",
        "api_name": "Sverige (Vemdalen)",
        "latitude": "62.4",
    },
    {
        "id": "sverige-oland",
        "name": "Öland",
        "api_name": "Sverige (Öland)",
        "latitude": "58.866991",
    },
    {
        "id": "sverige-orebro",
        "name": "Örebro",
        "api_name": "Sverige (Örebro)",
        "latitude": "59.2",
    },
    {
        "id": "sverige-ostersund",
        "name": "Östersund",
        "api_name": "Sverige (Östersund)",
        "latitude": "63.17668",
    },
]

# Skin types for Min soltid calculations
SKIN_TYPES = [
    {"id": "1", "name": "Type 1 (Very fair, burns easily)"},
    {"id": "2", "name": "Type 2 (Fair, burns easily)"},
    {"id": "3", "name": "Type 3 (Medium, sometimes burns)"},
    {"id": "4", "name": "Type 4 (Olive, rarely burns)"},
    {"id": "5", "name": "Type 5 (Brown, very rarely burns)"},
    {"id": "6", "name": "Type 6 (Dark brown, never burns)"},
]
