"""Fish profiles used by score calculation."""

FISH_PROFILES: dict[str, dict] = {
    "carp": {
        "label": "Carp",
        "ideal_temperature_min": 18,
        "ideal_temperature_max": 28,
        "acceptable_temperature_min": 10,
        "acceptable_temperature_max": 32,
        "ideal_pressure_min": 1008,
        "ideal_pressure_max": 1020,
        "ideal_wind_max": 20,
        "cloud_coverage_ideal": 50,
        "rain_tolerance": "medium",
        "best_conditions": ["cloudy", "partlycloudy", "rainy"],
    },
    "pike": {"ideal_temperature_min": 8, "ideal_temperature_max": 18, "ideal_wind_max": 25},
    "zander": {"ideal_temperature_min": 10, "ideal_temperature_max": 20, "ideal_wind_max": 25},
    "perch": {"ideal_temperature_min": 12, "ideal_temperature_max": 22, "ideal_wind_max": 25},
    "trout": {"ideal_temperature_min": 6, "ideal_temperature_max": 16, "ideal_wind_max": 30},
    "bream": {"ideal_temperature_min": 14, "ideal_temperature_max": 24, "ideal_wind_max": 22},
    "tench": {"ideal_temperature_min": 16, "ideal_temperature_max": 26, "ideal_wind_max": 20},
    "catfish": {"ideal_temperature_min": 18, "ideal_temperature_max": 30, "ideal_wind_max": 20},
    "bass": {"ideal_temperature_min": 15, "ideal_temperature_max": 26, "ideal_wind_max": 24},
    "generic": {"ideal_temperature_min": 12, "ideal_temperature_max": 24, "ideal_wind_max": 25},
}
