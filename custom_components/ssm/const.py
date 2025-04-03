"""Constants for the Swedish Radiation Safety Authority integration."""

DOMAIN = "ssm"

# Configuration constants
CONF_LOCATION_ID = "location_id"
CONF_LOCATION = "location"
DEFAULT_NAME = "SSM"

# Predefined stations with their location IDs - using string keys for translation
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

UV_LOCATIONS = [
    {"id": "sverige-gotland", "name": "Gotland"},
    {"id": "sverige-goteborg", "name": "Göteborg"},
    {"id": "sverige-malmo", "name": "Malmö"},
    {"id": "sverige-stockholm", "name": "Stockholm"},
    {"id": "sverige-polcirkeln", "name": "Polcirkeln"},
    {"id": "sverige-oland", "name": "Öland"},
    {"id": "sverige-ostersund", "name": "Östersund"},
]