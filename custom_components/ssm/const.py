"""Constants for the Swedish Radiation Safety Authority integration."""

DOMAIN = "ssm"

# Configuration constants
CONF_LOCATION_ID = "location_id"
CONF_LOCATION = "location"
DEFAULT_NAME = "SSM"

# Predefined stations with their location IDs - using string keys for translation
RADIATION_STATIONS = [
    {"id": "20", "name": "stations.bjuruklubb"},
    {"id": "5", "name": "stations.bramon"},
    {"id": "7", "name": "stations.farosund"},
    {"id": "18", "name": "stations.gielas"},
    {"id": "8", "name": "stations.gavle"},
    {"id": "17", "name": "stations.goteborg"},
    {"id": "16", "name": "stations.hallands_vadero"},
    {"id": "21", "name": "stations.hallum"},
    {"id": "6", "name": "stations.jarnasklubb"},
    {"id": "11", "name": "stations.karesuando"},
    {"id": "1278", "name": "stations.kilsbergen"},
    {"id": "4", "name": "stations.krangede"},
    {"id": "22", "name": "stations.malmo"},
    {"id": "19", "name": "stations.mala"},
    {"id": "2", "name": "stations.mora"},
    {"id": "1276", "name": "stations.norrkoping"},
    {"id": "12", "name": "stations.pajala"},
    {"id": "9", "name": "stations.ritsem"},
    {"id": "1", "name": "stations.sala"},
    {"id": "25", "name": "stations.skarpo"},
    {"id": "14", "name": "stations.skillinge"},
    {"id": "10", "name": "stations.storon"},
    {"id": "15", "name": "stations.sunne"},
    {"id": "3", "name": "stations.tannas"},
    {"id": "24", "name": "stations.visingo"},
    {"id": "1277", "name": "stations.vaxjo"},
    {"id": "23", "name": "stations.olands_norra_udde"},
    {"id": "13", "name": "stations.olands_sodra_udde"},
]

UV_LOCATIONS = [
    {"id": "Sverige (Gotland)", "name": "uv_locations.gotland"},
    {"id": "Sverige (Göteborg)", "name": "uv_locations.goteborg"},
    {"id": "Sverige (Malmö)", "name": "uv_locations.malmo"},
    {"id": "Sverige (Stockholm)", "name": "uv_locations.stockholm"},
    {"id": "Sverige (polcirkeln)", "name": "uv_locations.polcirkeln"},
    {"id": "Sverige (Öland)", "name": "uv_locations.oland"},
    {"id": "Sverige (Östersund)", "name": "uv_locations.ostersund"},
]