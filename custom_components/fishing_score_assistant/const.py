"""Constants for Fishing Score Assistant."""

DOMAIN = "fishing_score_assistant"

CONF_WEATHER_ENTITY = "weather_entity"
CONF_FORECAST_TYPE = "forecast_type"
CONF_BODY_TYPE = "body_type"
CONF_FISH = "fish"
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"

DEFAULT_FORECAST_TYPE = "hourly"

FORECAST_TYPES = ["hourly", "daily"]
BODY_TYPES = ["lake", "river", "pond", "reservoir", "sea"]
FISH_TYPES = [
    "carp",
    "pike",
    "zander",
    "perch",
    "trout",
    "bream",
    "tench",
    "catfish",
    "bass",
    "generic",
]

DEFAULT_NAME = "Fishing Spot"
UPDATE_INTERVAL_HOURS = 3
ATTR_ERROR = "error"
