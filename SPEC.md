# Fishing Score Assistant — Intégration HACS Home Assistant

## Objectif

Créer une intégration HACS pour Home Assistant permettant de calculer un score de pêche à partir des données météo déjà disponibles dans Home Assistant.

Contrairement à l’intégration `fishing_assistant` existante, cette intégration ne doit pas appeler directement Open-Meteo ou une API météo externe.

Elle doit utiliser une entité météo Home Assistant existante, par exemple :

- `weather.maison`
- `weather.yffiniac`
- `weather.forecast_home`
- `weather.meteo_france`

L’objectif est d’avoir une intégration plus robuste, compatible avec les sources météo déjà configurées par l’utilisateur.

---

## Nom du projet

Nom public :

```text
Fishing Score Assistant
```

Nom technique / domain Home Assistant :

```text
fishing_score_assistant
```

---

## Fonctionnalités principales

### Configuration via l’interface Home Assistant

L’intégration doit être ajoutable depuis :

```text
Paramètres → Appareils et services → Ajouter une intégration
```

Le `config_flow` doit demander :

- Nom du spot de pêche
- Entité météo Home Assistant à utiliser
- Type de prévision :
  - `hourly`
  - `daily`
- Type de plan d’eau :
  - `lake`
  - `river`
  - `pond`
  - `reservoir`
  - `sea`
- Poisson ciblé :
  - `carp`
  - `pike`
  - `zander`
  - `perch`
  - `trout`
  - `bream`
  - `tench`
  - `catfish`
  - `bass`
  - `generic`

---

## Principe de fonctionnement

L’intégration doit récupérer les prévisions météo depuis l’entité météo choisie via le service Home Assistant :

```yaml
action: weather.get_forecasts
target:
  entity_id: weather.xxx
data:
  type: hourly
```

Côté Python, l’intégration doit appeler le service Home Assistant avec `return_response=True`.

Exemple attendu du retour :

```python
{
    "weather.xxx": {
        "forecast": [
            {
                "datetime": "...",
                "condition": "cloudy",
                "temperature": 18.2,
                "pressure": 1014,
                "wind_speed": 12,
                "precipitation": 0,
                "precipitation_probability": 20,
                "cloud_coverage": 60,
                "humidity": 75
            }
        ]
    }
}
```

L’intégration doit être tolérante : toutes les entités météo ne fournissent pas forcément tous les champs.

Si une donnée est absente, elle ne doit pas faire planter l’intégration. Elle doit être ignorée ou remplacée par une valeur neutre.

---

## Capteur principal

Pour chaque spot configuré, créer :

```text
sensor.<spot>_<fish>_fishing_score
```

Exemple :

```text
sensor.yffiniac_carp_fishing_score
```

État :

```text
0 à 10
```

Attributs attendus :

```yaml
fish: carp
body_type: pond
weather_entity: weather.yffiniac
score_level: good
best_window_start: "2026-05-26T18:00:00+02:00"
best_window_end: "2026-05-26T21:00:00+02:00"
best_window_score: 7.4
forecast:
  - datetime: "2026-05-26T15:00:00+02:00"
    score: 5.8
    temperature: 18.2
    pressure: 1014
    wind_speed: 12
    precipitation: 0
    cloud_coverage: 60
missing_fields: []
```

---

## Capteurs optionnels

Créer aussi, si possible :

```text
sensor.<spot>_<fish>_best_fishing_window
sensor.<spot>_<fish>_fishing_level
sensor.<spot>_<fish>_next_good_window
```

Exemple :

```text
sensor.yffiniac_carp_best_fishing_window
sensor.yffiniac_carp_fishing_level
sensor.yffiniac_carp_next_good_window
```

---

## Barème du score

Le score final doit être compris entre 0 et 10.

Il faut éviter qu’un problème météo donne automatiquement 0, sauf si les données indiquent réellement de mauvaises conditions.

### Pondération générale

Score météo global :

- Température : 30 %
- Pression : 20 %
- Variation / niveau de pression : 10 %
- Vent : 15 %
- Pluie : 10 %
- Couverture nuageuse : 10 %
- Condition météo générale : 5 %

Si certaines données sont absentes, recalculer le score avec les données disponibles au lieu de pénaliser brutalement.

---

## Profils de poissons

Créer un fichier :

```text
custom_components/fishing_score_assistant/fish_profiles.py
```

Chaque poisson doit avoir un profil.

Exemple pour la carpe :

```python
FISH_PROFILES = {
    "carp": {
        "label": "Carpe",
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
    }
}
```

Ajouter au minimum :

- `carp`
- `pike`
- `zander`
- `perch`
- `trout`
- `bream`
- `tench`
- `catfish`
- `bass`
- `generic`

---

## Calcul spécifique pour la carpe

La carpe doit avoir un score favorable quand :

- température douce à chaude
- météo stable ou légèrement couverte
- vent faible à modéré
- pression stable ou légèrement descendante
- pluie faible possible
- absence de conditions extrêmes

La carpe ne doit pas être pénalisée trop fortement uniquement parce qu’il y a des nuages ou une petite pluie.

---

## Gestion des erreurs

L’intégration ne doit jamais afficher `0` sans explication si la météo est indisponible.

Si aucune prévision n’est disponible :

État du capteur :

```text
unavailable
```

Attributs :

```yaml
error: "No forecast data returned by weather entity"
weather_entity: weather.xxx
```

Si certains champs météo manquent :

```yaml
missing_fields:
  - pressure
  - cloud_coverage
```

Mais le score doit quand même être calculé avec les données disponibles.

---

## Architecture du dépôt

Structure HACS attendue :

```text
fishing-score-assistant/
├── README.md
├── hacs.json
├── custom_components/
│   └── fishing_score_assistant/
│       ├── __init__.py
│       ├── manifest.json
│       ├── const.py
│       ├── config_flow.py
│       ├── coordinator.py
│       ├── sensor.py
│       ├── score.py
│       ├── fish_profiles.py
│       ├── strings.json
│       └── translations/
│           ├── en.json
│           └── fr.json
└── .github/
    └── workflows/
        └── validate.yml
```

---

## `hacs.json`

Créer un fichier `hacs.json` à la racine :

```json
{
  "name": "Fishing Score Assistant",
  "render_readme": true,
  "domains": ["sensor"],
  "homeassistant": "2025.1.0"
}
```

---

## `manifest.json`

Créer :

```text
custom_components/fishing_score_assistant/manifest.json
```

Contenu proposé :

```json
{
  "domain": "fishing_score_assistant",
  "name": "Fishing Score Assistant",
  "codeowners": ["@coeyn22"],
  "config_flow": true,
  "documentation": "https://github.com/coeyn22/fishing-score-assistant",
  "issue_tracker": "https://github.com/coeyn22/fishing-score-assistant/issues",
  "iot_class": "local_polling",
  "version": "0.1.0",
  "requirements": []
}
```

Important : `iot_class` doit être `local_polling`, car l’intégration n’appelle pas directement un cloud externe. Elle lit une entité Home Assistant déjà existante.

---

## `const.py`

Créer les constantes :

```python
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
```

---

## `coordinator.py`

Créer un `DataUpdateCoordinator`.

Rôle :

1. Lire la configuration.
2. Appeler `weather.get_forecasts`.
3. Normaliser les données météo.
4. Calculer les scores horaires ou journaliers.
5. Exposer les données aux capteurs.

Pseudo-code :

```python
response = await hass.services.async_call(
    "weather",
    "get_forecasts",
    {
        "entity_id": weather_entity,
        "type": forecast_type,
    },
    blocking=True,
    return_response=True,
)

forecast = response[weather_entity]["forecast"]
```

Attention : vérifier la structure réelle du retour. Elle peut varier légèrement selon les versions Home Assistant et selon l’intégration météo utilisée.

---

## Normalisation météo

Créer une fonction :

```python
normalize_forecast_item(item: dict) -> dict
```

Elle doit retourner :

```python
{
    "datetime": item.get("datetime"),
    "condition": item.get("condition"),
    "temperature": item.get("temperature"),
    "pressure": item.get("pressure"),
    "humidity": item.get("humidity"),
    "wind_speed": item.get("wind_speed"),
    "precipitation": item.get("precipitation"),
    "precipitation_probability": item.get("precipitation_probability"),
    "cloud_coverage": item.get("cloud_coverage"),
}
```

Prévoir aussi des alias :

```python
cloud_coverage = item.get("cloud_coverage") or item.get("cloud_cover")
wind_speed = item.get("wind_speed") or item.get("wind_speed_10m")
```

---

## `score.py`

Créer les fonctions :

```python
calculate_fishing_score(forecast_item: dict, fish: str, body_type: str) -> dict
calculate_temperature_score(...)
calculate_pressure_score(...)
calculate_wind_score(...)
calculate_rain_score(...)
calculate_cloud_score(...)
calculate_condition_score(...)
find_best_window(scored_forecast: list, window_size: int = 3) -> dict
```

La fonction principale doit retourner :

```python
{
    "score": 7.4,
    "level": "good",
    "details": {
        "temperature_score": 8,
        "pressure_score": 7,
        "wind_score": 6,
        "rain_score": 8,
        "cloud_score": 7,
        "condition_score": 6
    },
    "missing_fields": []
}
```

---

## Niveaux lisibles

Créer une fonction :

```python
score_to_level(score: float) -> str
```

Barème :

```text
0 à 2.9   = very_bad
3 à 4.9   = bad
5 à 6.4   = average
6.5 à 7.9 = good
8 à 10    = excellent
```

Traductions françaises :

```text
very_bad  = Très mauvais
bad       = Mauvais
average   = Moyen
good      = Bon
excellent = Excellent
```

---

## Mise à jour des données

Le coordinateur doit mettre à jour les données :

- au démarrage de Home Assistant
- toutes les 3 heures
- quand l’utilisateur recharge l’intégration

Intervalle proposé :

```python
update_interval = timedelta(hours=3)
```

---

## Carte Lovelace Markdown proposée

Le README doit proposer cette carte :

```yaml
type: markdown
content: |
  ## 🎣 Score pêche

  **Score actuel : {{ states('sensor.yffiniac_carp_fishing_score') }}/10**

  Niveau : {{ state_attr('sensor.yffiniac_carp_fishing_score', 'score_level') }}

  Meilleur créneau :
  {{ state_attr('sensor.yffiniac_carp_fishing_score', 'best_window_start') }}
  →
  {{ state_attr('sensor.yffiniac_carp_fishing_score', 'best_window_end') }}

  {% set forecast = state_attr('sensor.yffiniac_carp_fishing_score', 'forecast') %}
  {% if forecast %}
  ### Prévisions
  {% for item in forecast[:8] %}
  - {{ item.datetime }} : {{ item.score }}/10
  {% endfor %}
  {% else %}
  Aucune prévision disponible.
  {% endif %}
```

---

## Carte jauge proposée

```yaml
type: gauge
entity: sensor.yffiniac_carp_fishing_score
name: Score pêche - Carpe
min: 0
max: 10
needle: true
severity:
  green: 7
  yellow: 5
  red: 0
```

---

## README attendu

Le README doit contenir :

1. Présentation du projet
2. Pourquoi cette intégration existe
3. Différence avec Fishing Assistant classique
4. Installation via HACS en dépôt personnalisé
5. Configuration
6. Exemples de cartes Lovelace
7. Explication du score
8. Liste des poissons supportés
9. Dépannage
10. Roadmap

---

## Installation HACS attendue

L’utilisateur devra pouvoir faire :

```text
HACS → Trois points → Custom repositories → ajouter le dépôt GitHub → type Integration
```

Puis :

```text
HACS → Fishing Score Assistant → Download
```

Puis :

```text
Redémarrer Home Assistant
```

Puis :

```text
Paramètres → Appareils et services → Ajouter une intégration → Fishing Score Assistant
```

---

## Roadmap

### Version 0.1.0

- Intégration HACS installable
- Config flow fonctionnel
- Sélection d’une entité météo Home Assistant
- Score pour la carpe
- Capteur principal
- Attribut `forecast`
- Carte Markdown dans le README

### Version 0.2.0

- Ajout des autres poissons
- Meilleur créneau de pêche
- Gestion plus fine des champs météo manquants
- Traductions FR/EN

### Version 0.3.0

- Options modifiables depuis l’interface
- Plusieurs spots de pêche
- Diagnostic dans Home Assistant
- Capteurs séparés pour meilleur créneau et niveau

### Version 1.0.0

- Version stable
- README complet
- Tests unitaires
- Publication propre sur GitHub
- Compatible HACS custom repository

---

## Contraintes importantes

- Ne pas appeler directement Open-Meteo.
- Ne pas utiliser d’API externe.
- Utiliser uniquement les entités météo déjà présentes dans Home Assistant.
- Ne pas mettre le score à 0 si les données météo sont indisponibles.
- Mettre le capteur en `unavailable` si aucune prévision n’est récupérée.
- Logger clairement les erreurs.
- Garder le code simple, lisible et compatible avec Home Assistant récent.
- Prévoir les traductions françaises.

---

# Prompt pour Codex

Tu es mon agent de codage pour créer une intégration HACS Home Assistant.

Lis d’abord le fichier `SPEC.md` à la racine du projet et respecte-le comme cahier des charges principal.

## Objectif

Créer une intégration custom Home Assistant installable via HACS, appelée `Fishing Score Assistant`, dont le domain est :

```text
fishing_score_assistant
```

Contrairement à l’intégration `fishing_assistant` existante, cette intégration ne doit jamais appeler directement Open-Meteo ou une API météo externe.

Elle doit utiliser une entité météo Home Assistant existante choisie par l’utilisateur dans le config flow, puis récupérer les prévisions via le service Home Assistant :

```text
weather.get_forecasts
```

## Priorités de développement

### 1. Créer la structure HACS complète

Créer les fichiers suivants :

```text
hacs.json
README.md
custom_components/fishing_score_assistant/__init__.py
custom_components/fishing_score_assistant/manifest.json
custom_components/fishing_score_assistant/const.py
custom_components/fishing_score_assistant/config_flow.py
custom_components/fishing_score_assistant/coordinator.py
custom_components/fishing_score_assistant/sensor.py
custom_components/fishing_score_assistant/score.py
custom_components/fishing_score_assistant/fish_profiles.py
custom_components/fishing_score_assistant/strings.json
custom_components/fishing_score_assistant/translations/fr.json
custom_components/fishing_score_assistant/translations/en.json
```

### 2. Implémenter un config flow simple

Le config flow doit demander :

- nom du spot
- entité météo Home Assistant
- type de prévision `hourly` ou `daily`
- type de plan d’eau
- poisson ciblé

### 3. Implémenter un `DataUpdateCoordinator`

Le coordinator doit :

- appeler `weather.get_forecasts`
- utiliser `return_response=True`
- récupérer la clé `forecast`
- normaliser les champs météo
- calculer les scores
- gérer les erreurs proprement

### 4. Implémenter le capteur principal

Le capteur principal doit avoir :

- un état numérique de 0 à 10
- des attributs :
  - poisson
  - type d’eau
  - entité météo utilisée
  - niveau du score
  - meilleur créneau
  - forecast
  - champs météo manquants

### 5. Implémenter d’abord correctement le profil `carp`

Le profil carpe doit être prioritaire.

Les autres poissons peuvent être ajoutés avec des profils simples.

### 6. Gérer correctement les erreurs

Ne jamais afficher `0` si aucune donnée météo n’est disponible.

Dans ce cas, le capteur doit être `unavailable` avec un attribut `error`.

### 7. Ajouter un README utile

Le README doit expliquer :

- le projet
- l’installation via HACS custom repository
- la configuration
- les cartes Lovelace
- le calcul du score
- les poissons supportés
- le dépannage

## Contraintes techniques

- Code Python propre et async compatible Home Assistant.
- Aucun appel HTTP externe.
- Aucun package externe si possible.
- Utiliser les APIs Home Assistant standard.
- Ajouter des logs clairs.
- Prévoir une base simple mais maintenable.
- Ne pas surcomplexifier la première version.

## Résultat attendu

Commence par générer tous les fichiers nécessaires pour une version minimale fonctionnelle `0.1.0`.

Après génération, explique-moi :

- quels fichiers ont été créés
- comment installer l’intégration dans Home Assistant
- comment tester le service météo
- comment ajouter la première carte Lovelace