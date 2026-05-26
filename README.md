# Fishing Score Assistant

Fishing Score Assistant is a custom Home Assistant integration for HACS.
It computes a fishing score from an existing Home Assistant weather entity forecast.

Unlike integrations that call external weather APIs directly, this integration only uses Home Assistant weather data via `weather.get_forecasts`.

## Why this integration exists

- Reuse the weather provider you already trust in Home Assistant
- Avoid direct external API calls from this integration
- Keep setup simple and robust

## Difference with classic Fishing Assistant

- `fishing_assistant`: can query external weather APIs
- `fishing_score_assistant`: never calls external weather APIs; it only consumes Home Assistant weather entities

## Installation (HACS Custom Repository)

1. Open HACS.
2. Click the menu (three dots) -> `Custom repositories`.
3. Add your GitHub repository URL.
4. Select type: `Integration`.
5. Search for `Fishing Score Assistant` and click `Download`.
6. Restart Home Assistant.

Then add it from:
`Settings -> Devices & Services -> Add Integration -> Fishing Score Assistant`.

## Configuration

The config flow asks for:

- Spot name
- Weather entity (`weather.*`)
- Forecast type (`hourly` or `daily`)
- Water body type (`lake`, `river`, `pond`, `reservoir`, `sea`)
- Target fish (`carp`, `pike`, `zander`, `perch`, `trout`, `bream`, `tench`, `catfish`, `bass`, `generic`)

## Entity created

For each config entry, one main sensor is created:

- `sensor.<spot>_<fish>_fishing_score`

State: `0..10` (or `unavailable` if no forecast data)

Main attributes:

- `fish`
- `body_type`
- `weather_entity`
- `score_level`
- `best_window_start`
- `best_window_end`
- `best_window_score`
- `forecast`
- `missing_fields`
- `error` (when unavailable)

## Lovelace examples

### Markdown card

```yaml
type: markdown
content: |
  ## Fishing Score

  **Current score: {{ states('sensor.yffiniac_carp_fishing_score') }}/10**

  Level: {{ state_attr('sensor.yffiniac_carp_fishing_score', 'score_level') }}

  Best window:
  {{ state_attr('sensor.yffiniac_carp_fishing_score', 'best_window_start') }}
  ->
  {{ state_attr('sensor.yffiniac_carp_fishing_score', 'best_window_end') }}

  {% set forecast = state_attr('sensor.yffiniac_carp_fishing_score', 'forecast') %}
  {% if forecast %}
  ### Forecast
  {% for item in forecast[:8] %}
  - {{ item.datetime }} : {{ item.score }}/10
  {% endfor %}
  {% else %}
  No forecast available.
  {% endif %}
```

### Gauge card

```yaml
type: gauge
entity: sensor.yffiniac_carp_fishing_score
name: Fishing Score - Carp
min: 0
max: 10
needle: true
severity:
  green: 7
  yellow: 5
  red: 0
```

## How scoring works

Weighted weather score (dynamic if some fields are missing):

- Temperature: 30%
- Pressure: 20%
- Pressure trend: 10%
- Wind: 15%
- Rain: 10%
- Cloud coverage: 10%
- General condition: 5%

If some fields are missing, only available dimensions are used.
No forecast data means `unavailable` (never a fake `0`).

## Supported fish

- carp
- pike
- zander
- perch
- trout
- bream
- tench
- catfish
- bass
- generic

## Troubleshooting

- Sensor is `unavailable`:
  - verify the selected `weather.*` entity exists
  - verify that `weather.get_forecasts` returns a `forecast` list
- Missing fields in attributes:
  - your weather provider may not expose all metrics (normal)
- No updates:
  - reload the integration
  - check Home Assistant logs for `fishing_score_assistant`

## Roadmap

### 0.1.0
- HACS installable integration
- Config flow
- Home Assistant weather entity selection
- Main score sensor
- Carp profile priority

### 0.2.0
- More fish tuning
- Additional helper sensors
- Finer missing-data handling

### 1.0.0
- Extended tests
- Stable profiles
- Diagnostics
