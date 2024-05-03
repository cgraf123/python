# Python Projects
A collection of example Python projects.

## app
Flask server and utility code for API and UI components.

### app.py
Flask server code. Includes both API and UI endpoints.

#### Endpoints
1. `/api/`
   1. __POST__: Accepts GeoJSON file and binds new UUID
   1. __GET__: Returns list of all UUIDs
1. `/api/{UUID}`
   1. __GET__: Returns GeoJSON for mapped UUID
   1. __POST__: Adds/Updates GeoJSON file for UUID
   1. __DELETE__: Removes GeoJSON UUID
1. `/ui/{UUID}`
   1. Renders Folium/Leaflet map containing UUID GeoJSON features

### geo.py
Utility class for managing GeoJSON data mapping and filesystem persistence.

## scripts

### client.py
Requests CLI client used to interact with API endpoints.

## Requirements
* `Pipfile` requires Python 3.10