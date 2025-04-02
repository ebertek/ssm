"""Constants for the Swedish Radiation Safety Authority integration."""

DOMAIN = "ssm"

# Configuration constants
CONF_LOCATION_ID = "location_id"
CONF_LOCATION = "location"
DEFAULT_NAME = "SSM"

# Predefined stations with their location IDs - using string keys for translation
RADIATION_STATIONS = [
    {"id": "20", "name": "bjuruklubb"},
    {"id": "5", "name": "bramon"},
    {"id": "7", "name": "farosund"},
    {"id": "18", "name": "gielas"},
    {"id": "8", "name": "gavle"},
    {"id": "17", "name": "goteborg"},
    {"id": "16", "name": "hallands_vadero"},
    {"id": "21", "name": "hallum"},
    {"id": "6", "name": "jarnasklubb"},
    {"id": "11", "name": "karesuando"},
    {"id": "1278", "name": "kilsbergen"},
    {"id": "4", "name": "krangede"},
    {"id": "22", "name": "malmo"},
    {"id": "19", "name": "mala"},
    {"id": "2", "name": "mora"},
    {"id": "1276", "name": "norrkoping"},
    {"id": "12", "name": "pajala"},
    {"id": "9", "name": "ritsem"},
    {"id": "1", "name": "sala"},
    {"id": "25", "name": "skarpo"},
    {"id": "14", "name": "skillinge"},
    {"id": "10", "name": "storon"},
    {"id": "15", "name": "sunne"},
    {"id": "3", "name": "tannas"},
    {"id": "24", "name": "visingo"},
    {"id": "1277", "name": "vaxjo"},
    {"id": "23", "name": "olands_norra_udde"},
    {"id": "13", "name": "olands_sodra_udde"},
]

UV_LOCATIONS = [
    {"id": "Sverige (Gotland)", "name": "gotland"},
    {"id": "Sverige (Göteborg)", "name": "goteborg"},
    {"id": "Sverige (Malmö)", "name": "malmo"},
    {"id": "Sverige (Stockholm)", "name": "stockholm"},
    {"id": "Sverige (polcirkeln)", "name": "polcirkeln"},
    {"id": "Sverige (Öland)", "name": "oland"},
    {"id": "Sverige (Östersund)", "name": "ostersund"},
]