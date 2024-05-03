import logging

from flask import Flask, request
import folium

from .geo import GeoJsonStorageManager

logging.basicConfig()
app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
geo_manager = GeoJsonStorageManager(storage_path="tmp/storage", logger=app.logger)


@app.get("/api/")
def api_get():
    """Returns list of mapped GeoJSON UUIDS."""
    return geo_manager.get_uuids()


@app.post("/api/")
def api_post():
    """Add uploaded GeoJSON file and return the new UUID."""
    geojson = request.files.get("geojson")
    uuid = geo_manager.add(json=geojson.stream.read().decode("utf8"))
    return str(uuid)


@app.get("/api/<uuid:uuid>")
def api_uuid_get(uuid):
    """Returns UUID's GeoJSON."""
    return geo_manager.get_geojson(uuid)


@app.post("/api/<uuid:uuid>")
def api_uuid_post(uuid):
    """Add/Update GeoJSON for UUID."""
    geojson = request.files.get("geojson")
    geo_manager.add(json=geojson.stream.read().decode("utf8"), uuid=uuid)
    return str(uuid)


@app.delete("/api/<uuid:uuid>")
def api_uuid_delete(uuid):
    """Delete GeoJSON UUID."""
    geo_manager.remove(uuid)
    return str(uuid)


@app.get("/ui/<uuid:uuid>")
def ui_uuid_get(uuid):
    """Render map with GeoJSON UUID features."""
    geojson = geo_manager.get_geojson(uuid)
    m = folium.Map()
    folium.GeoJson(geojson).add_to(m)
    return m.get_root().render()
