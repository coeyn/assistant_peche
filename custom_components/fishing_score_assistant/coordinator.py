"""Coordinator for Fishing Score Assistant."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    ATTR_ERROR,
    CONF_BODY_TYPE,
    CONF_FISH,
    CONF_FORECAST_TYPE,
    CONF_WEATHER_ENTITY,
    DOMAIN,
    UPDATE_INTERVAL_HOURS,
)
from .score import calculate_fishing_score, find_best_window, score_to_level

_LOGGER = logging.getLogger(__name__)


def normalize_forecast_item(item: dict) -> dict:
    """Normalize a weather forecast item to a common shape."""
    return {
        "datetime": item.get("datetime"),
        "condition": item.get("condition"),
        "temperature": item.get("temperature"),
        "pressure": item.get("pressure"),
        "humidity": item.get("humidity"),
        "wind_speed": item.get("wind_speed") or item.get("wind_speed_10m"),
        "precipitation": item.get("precipitation"),
        "precipitation_probability": item.get("precipitation_probability"),
        "cloud_coverage": item.get("cloud_coverage") or item.get("cloud_cover"),
    }


class FishingScoreCoordinator(DataUpdateCoordinator[dict]):
    """Fetch weather forecasts and compute fishing scores."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.weather_entity = entry.data[CONF_WEATHER_ENTITY]
        self.forecast_type = entry.data[CONF_FORECAST_TYPE]
        self.body_type = entry.data[CONF_BODY_TYPE]
        self.fish = entry.data[CONF_FISH]
        self.spot_name = entry.data[CONF_NAME]

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(hours=UPDATE_INTERVAL_HOURS),
        )

    async def _async_update_data(self) -> dict:
        """Update data via weather.get_forecasts and compute scores."""
        try:
            response = await self.hass.services.async_call(
                "weather",
                "get_forecasts",
                {
                    "entity_id": self.weather_entity,
                    "type": self.forecast_type,
                },
                blocking=True,
                return_response=True,
            )
        except HomeAssistantError as err:
            raise UpdateFailed(f"Service call failed: {err}") from err

        if not isinstance(response, dict):
            raise UpdateFailed("weather.get_forecasts returned an unexpected response type")

        entity_payload = response.get(self.weather_entity)
        if not isinstance(entity_payload, dict):
            _LOGGER.error("No payload found for weather entity %s", self.weather_entity)
            return {ATTR_ERROR: "No forecast data returned by weather entity", "forecast": []}

        raw_forecast = entity_payload.get("forecast")
        if not isinstance(raw_forecast, list) or not raw_forecast:
            _LOGGER.error("No forecast list returned for weather entity %s", self.weather_entity)
            return {ATTR_ERROR: "No forecast data returned by weather entity", "forecast": []}

        normalized = [normalize_forecast_item(item) for item in raw_forecast if isinstance(item, dict)]
        scored_forecast: list[dict] = []
        all_missing: set[str] = set()

        for item in normalized:
            scored = calculate_fishing_score(item, self.fish, self.body_type)
            all_missing.update(scored["missing_fields"])
            scored_forecast.append(
                {
                    **item,
                    "score": scored["score"],
                    "score_level": scored["level"],
                    "details": scored["details"],
                    "missing_fields": scored["missing_fields"],
                }
            )

        valid_scores = [item["score"] for item in scored_forecast if item.get("score") is not None]
        if not valid_scores:
            return {
                ATTR_ERROR: "No usable weather fields available to compute score",
                "forecast": scored_forecast,
                "missing_fields": sorted(all_missing),
            }

        current_score = round(valid_scores[0], 1)
        window_size = 3 if self.forecast_type == "hourly" else 1
        best_window = find_best_window(scored_forecast, window_size=window_size)
        next_good_window = next(
            (
                item.get("datetime")
                for item in scored_forecast
                if item.get("score") is not None and item.get("score", 0) >= 6.5
            ),
            None,
        )

        return {
            "score": current_score,
            "score_level": score_to_level(current_score),
            "fish": self.fish,
            "body_type": self.body_type,
            "weather_entity": self.weather_entity,
            "forecast_type": self.forecast_type,
            "forecast": scored_forecast,
            "best_window": best_window,
            "next_good_window": next_good_window,
            "missing_fields": sorted(all_missing),
        }
