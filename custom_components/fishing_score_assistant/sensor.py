"""Sensor platform for Fishing Score Assistant."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_ERROR, DOMAIN, CONF_FISH
from .coordinator import FishingScoreCoordinator

DAY_FR = {
    "Mon": "Lun",
    "Tue": "Mar",
    "Wed": "Mer",
    "Thu": "Jeu",
    "Fri": "Ven",
    "Sat": "Sam",
    "Sun": "Dim",
}


def _format_fr_datetime(value: str | None) -> str | None:
    """Format ISO datetime to a compact French-like string."""
    if not value:
        return None
    dt = dt_util.parse_datetime(value)
    if dt is None:
        return value
    local_dt = dt_util.as_local(dt)
    day = DAY_FR.get(local_dt.strftime("%a"), local_dt.strftime("%a"))
    return f"{day} {local_dt.strftime('%d/%m %H:%M')}"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Fishing Score sensor from a config entry."""
    coordinator: FishingScoreCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            FishingScoreSensor(coordinator, entry),
            FishingBestWindowSensor(coordinator, entry),
            FishingLevelSensor(coordinator, entry),
            FishingNextGoodWindowSensor(coordinator, entry),
        ],
        True,
    )


class FishingScoreSensor(CoordinatorEntity[FishingScoreCoordinator], SensorEntity):
    """Main fishing score sensor."""

    _attr_has_entity_name = True
    _attr_name = "Fishing Score"

    def __init__(self, coordinator: FishingScoreCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        spot_name = entry.data[CONF_NAME].strip().lower().replace(" ", "_")
        fish = entry.data[CONF_FISH]
        self._attr_unique_id = f"{entry.entry_id}_{fish}_score"
        self._attr_name = f"{spot_name} {fish} fishing score"
        self._attr_entity_id = f"sensor.{spot_name}_{fish}_fishing_score"

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        if data.get(ATTR_ERROR):
            return None
        return data.get("score")

    @property
    def available(self) -> bool:
        data = self.coordinator.data or {}
        return super().available and not bool(data.get(ATTR_ERROR))

    @property
    def extra_state_attributes(self) -> dict:
        data = self.coordinator.data or {}
        best_window = data.get("best_window") or {}
        attrs = {
            "fish": data.get("fish", self.coordinator.fish),
            "body_type": data.get("body_type", self.coordinator.body_type),
            "weather_entity": data.get("weather_entity", self.coordinator.weather_entity),
            "score_level": data.get("score_level"),
            "best_window_start": best_window.get("start"),
            "best_window_end": best_window.get("end"),
            "best_window_score": best_window.get("score"),
            "forecast": data.get("forecast", []),
            "missing_fields": data.get("missing_fields", []),
        }
        if data.get(ATTR_ERROR):
            attrs[ATTR_ERROR] = data[ATTR_ERROR]
        return attrs


class FishingBestWindowSensor(CoordinatorEntity[FishingScoreCoordinator], SensorEntity):
    """Best fishing window sensor."""

    _attr_has_entity_name = True
    _attr_name = "Best Fishing Window"

    def __init__(self, coordinator: FishingScoreCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        spot_name = entry.data[CONF_NAME].strip().lower().replace(" ", "_")
        fish = entry.data[CONF_FISH]
        self._attr_unique_id = f"{entry.entry_id}_{fish}_best_window"
        self._attr_name = f"{spot_name} {fish} best fishing window"
        self._attr_entity_id = f"sensor.{spot_name}_{fish}_best_fishing_window"

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        if data.get(ATTR_ERROR):
            return None
        best_window = data.get("best_window") or {}
        start = best_window.get("start")
        end = best_window.get("end")
        if not start or not end:
            return None
        start_fmt = _format_fr_datetime(start)
        end_dt = dt_util.parse_datetime(end)
        end_fmt = dt_util.as_local(end_dt).strftime("%H:%M") if end_dt else end
        if not start_fmt or not end_fmt:
            return None
        return f"{start_fmt} -> {end_fmt}"

    @property
    def available(self) -> bool:
        data = self.coordinator.data or {}
        return super().available and not bool(data.get(ATTR_ERROR))

    @property
    def extra_state_attributes(self) -> dict:
        data = self.coordinator.data or {}
        best_window = data.get("best_window") or {}
        attrs = {
            "best_window_start": best_window.get("start"),
            "best_window_end": best_window.get("end"),
            "best_window_score": best_window.get("score"),
            "best_window_start_formatted": _format_fr_datetime(best_window.get("start")),
            "best_window_end_formatted": _format_fr_datetime(best_window.get("end")),
        }
        if data.get(ATTR_ERROR):
            attrs[ATTR_ERROR] = data[ATTR_ERROR]
        return attrs


class FishingLevelSensor(CoordinatorEntity[FishingScoreCoordinator], SensorEntity):
    """Fishing level sensor."""

    _attr_has_entity_name = True
    _attr_name = "Fishing Level"

    def __init__(self, coordinator: FishingScoreCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        spot_name = entry.data[CONF_NAME].strip().lower().replace(" ", "_")
        fish = entry.data[CONF_FISH]
        self._attr_unique_id = f"{entry.entry_id}_{fish}_level"
        self._attr_name = f"{spot_name} {fish} fishing level"
        self._attr_entity_id = f"sensor.{spot_name}_{fish}_fishing_level"

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        if data.get(ATTR_ERROR):
            return None
        return data.get("score_level")

    @property
    def available(self) -> bool:
        data = self.coordinator.data or {}
        return super().available and not bool(data.get(ATTR_ERROR))

    @property
    def extra_state_attributes(self) -> dict:
        data = self.coordinator.data or {}
        attrs = {"score": data.get("score")}
        if data.get(ATTR_ERROR):
            attrs[ATTR_ERROR] = data[ATTR_ERROR]
        return attrs


class FishingNextGoodWindowSensor(CoordinatorEntity[FishingScoreCoordinator], SensorEntity):
    """Next good fishing window sensor."""

    _attr_has_entity_name = True
    _attr_name = "Next Good Window"

    def __init__(self, coordinator: FishingScoreCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        spot_name = entry.data[CONF_NAME].strip().lower().replace(" ", "_")
        fish = entry.data[CONF_FISH]
        self._attr_unique_id = f"{entry.entry_id}_{fish}_next_good_window"
        self._attr_name = f"{spot_name} {fish} next good window"
        self._attr_entity_id = f"sensor.{spot_name}_{fish}_next_good_window"

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        if data.get(ATTR_ERROR):
            return None
        return _format_fr_datetime(data.get("next_good_window"))

    @property
    def available(self) -> bool:
        data = self.coordinator.data or {}
        return super().available and not bool(data.get(ATTR_ERROR))

    @property
    def extra_state_attributes(self) -> dict:
        data = self.coordinator.data or {}
        attrs = {
            "threshold": 6.5,
            "next_good_window_raw": data.get("next_good_window"),
            "next_good_window_formatted": _format_fr_datetime(data.get("next_good_window")),
        }
        if data.get(ATTR_ERROR):
            attrs[ATTR_ERROR] = data[ATTR_ERROR]
        return attrs
