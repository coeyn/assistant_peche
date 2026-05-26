"""Scoring utilities for Fishing Score Assistant."""

from __future__ import annotations

from .fish_profiles import FISH_PROFILES


def _clamp_0_10(value: float) -> float:
    return round(max(0.0, min(10.0, value)), 1)


def score_to_level(score: float) -> str:
    if score < 3:
        return "very_bad"
    if score < 5:
        return "bad"
    if score < 6.5:
        return "average"
    if score < 8:
        return "good"
    return "excellent"


def calculate_temperature_score(temperature: float | None, fish_profile: dict) -> float | None:
    if temperature is None:
        return None
    ideal_min = fish_profile.get("ideal_temperature_min", 12)
    ideal_max = fish_profile.get("ideal_temperature_max", 24)
    acceptable_min = fish_profile.get("acceptable_temperature_min", ideal_min - 6)
    acceptable_max = fish_profile.get("acceptable_temperature_max", ideal_max + 6)

    if ideal_min <= temperature <= ideal_max:
        return 10.0
    if temperature < acceptable_min or temperature > acceptable_max:
        return 1.0

    if temperature < ideal_min:
        span = max(1.0, ideal_min - acceptable_min)
        return _clamp_0_10(4.0 + (temperature - acceptable_min) / span * 6.0)

    span = max(1.0, acceptable_max - ideal_max)
    return _clamp_0_10(10.0 - (temperature - ideal_max) / span * 6.0)


def calculate_pressure_score(pressure: float | None, fish_profile: dict) -> float | None:
    if pressure is None:
        return None
    pmin = fish_profile.get("ideal_pressure_min", 1008)
    pmax = fish_profile.get("ideal_pressure_max", 1020)
    if pmin <= pressure <= pmax:
        return 9.0
    distance = min(abs(pressure - pmin), abs(pressure - pmax))
    return _clamp_0_10(9.0 - distance * 0.5)


def calculate_wind_score(wind_speed: float | None, fish_profile: dict) -> float | None:
    if wind_speed is None:
        return None
    ideal_wind_max = fish_profile.get("ideal_wind_max", 25)
    if wind_speed <= ideal_wind_max:
        return _clamp_0_10(9.0 - (wind_speed / max(1.0, ideal_wind_max)) * 2.0)
    return _clamp_0_10(7.0 - ((wind_speed - ideal_wind_max) / max(1.0, ideal_wind_max)) * 6.0)


def calculate_rain_score(precipitation: float | None, fish_profile: dict) -> float | None:
    if precipitation is None:
        return None
    tolerance = fish_profile.get("rain_tolerance", "medium")
    if precipitation <= 0.2:
        return 9.0
    if precipitation <= 1.0:
        return 8.0 if tolerance in ("medium", "high") else 6.5
    if precipitation <= 3.0:
        return 6.5 if tolerance in ("medium", "high") else 4.0
    return 4.5 if tolerance == "high" else 2.5


def calculate_cloud_score(cloud_coverage: float | None, fish_profile: dict) -> float | None:
    if cloud_coverage is None:
        return None
    ideal = fish_profile.get("cloud_coverage_ideal", 50)
    distance = abs(cloud_coverage - ideal)
    return _clamp_0_10(9.0 - (distance / 50.0) * 5.0)


def calculate_condition_score(condition: str | None, fish_profile: dict) -> float | None:
    if condition is None:
        return None
    preferred = fish_profile.get("best_conditions", ["partlycloudy", "cloudy"])
    if condition in preferred:
        return 8.5
    if condition in ("sunny", "clear-night", "clear"):
        return 6.0
    if condition in ("lightning", "lightning-rainy", "hail", "snowy", "pouring"):
        return 2.0
    return 5.5


def calculate_fishing_score(forecast_item: dict, fish: str, body_type: str) -> dict:
    fish_profile = FISH_PROFILES.get(fish, FISH_PROFILES["generic"])

    temperature = forecast_item.get("temperature")
    pressure = forecast_item.get("pressure")
    wind_speed = forecast_item.get("wind_speed")
    precipitation = forecast_item.get("precipitation")
    cloud_coverage = forecast_item.get("cloud_coverage")
    condition = forecast_item.get("condition")

    temperature_score = calculate_temperature_score(temperature, fish_profile)
    pressure_score = calculate_pressure_score(pressure, fish_profile)
    pressure_trend_score = pressure_score
    wind_score = calculate_wind_score(wind_speed, fish_profile)
    rain_score = calculate_rain_score(precipitation, fish_profile)
    cloud_score = calculate_cloud_score(cloud_coverage, fish_profile)
    condition_score = calculate_condition_score(condition, fish_profile)

    weighted = {
        "temperature": (temperature_score, 0.30),
        "pressure": (pressure_score, 0.20),
        "pressure_trend": (pressure_trend_score, 0.10),
        "wind": (wind_score, 0.15),
        "rain": (rain_score, 0.10),
        "cloud": (cloud_score, 0.10),
        "condition": (condition_score, 0.05),
    }

    present = {k: v for k, v in weighted.items() if v[0] is not None}
    missing_fields = [
        field for field, value in {
            "temperature": temperature,
            "pressure": pressure,
            "wind_speed": wind_speed,
            "precipitation": precipitation,
            "cloud_coverage": cloud_coverage,
            "condition": condition,
        }.items() if value is None
    ]

    if not present:
        return {
            "score": None,
            "level": None,
            "details": {},
            "missing_fields": missing_fields,
        }

    weight_sum = sum(weight for _, weight in present.values())
    score = sum(score * weight for score, weight in present.values()) / weight_sum

    if body_type == "river":
        score -= 0.2
    elif body_type == "pond":
        score += 0.1

    final_score = _clamp_0_10(score)
    return {
        "score": final_score,
        "level": score_to_level(final_score),
        "details": {
            "temperature_score": temperature_score,
            "pressure_score": pressure_score,
            "pressure_trend_score": pressure_trend_score,
            "wind_score": wind_score,
            "rain_score": rain_score,
            "cloud_score": cloud_score,
            "condition_score": condition_score,
        },
        "missing_fields": missing_fields,
    }


def find_best_window(scored_forecast: list[dict], window_size: int = 3) -> dict:
    valid = [item for item in scored_forecast if item.get("score") is not None]
    if not valid:
        return {}

    if len(valid) < window_size:
        best = max(valid, key=lambda x: x["score"])
        return {
            "start": best.get("datetime"),
            "end": best.get("datetime"),
            "score": best.get("score"),
        }

    best_avg = -1.0
    best_data: dict = {}
    for idx in range(0, len(valid) - window_size + 1):
        window = valid[idx : idx + window_size]
        avg = sum(item["score"] for item in window) / window_size
        if avg > best_avg:
            best_avg = avg
            best_data = {
                "start": window[0].get("datetime"),
                "end": window[-1].get("datetime"),
                "score": _clamp_0_10(avg),
            }
    return best_data
