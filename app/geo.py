from functools import wraps
from json import JSONDecodeError
import logging
import os
from threading import Lock
from typing import Dict, Optional
from uuid import uuid4, UUID

import geojson

_lock: Lock = Lock()


def synchronize(lock: Lock):
    """Synchronize on  threading lock decorator."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
        return wrapper
    return decorator


class GeoJsonStorageManager:
    """Manages UUID to GeoJSON mapping of objects and filesystem."""

    storage_path: str
    logger: Optional[logging.Logger]
    _uuid_geojson_map: Dict[UUID, geojson.GeoJSON]

    def __init__(self, storage_path: str, logger: Optional[logging.Logger] = None):
        """Storage manager constructor."""
        self.storage_path = storage_path
        if not os.path.exists(storage_path):
            os.makedirs(storage_path)
        self.logger = logger
        self._uuid_geojson_map = {}
        self._update()

    def log(self, level: int, msg: str):
        """Use logger if defined."""
        if self.logger:
            self.logger.log(level=level, msg=msg)

    @synchronize(_lock)
    def _update(self):
        """Looks for UUID GeoJSON files in storage_path and maps them if valid."""
        self._uuid_geojson_map.clear()
        self.log(logging.INFO, f"{self} scanning {self.storage_path} for UUID GeoJSON files.")
        # attempt to load UUID files in storage_path directory
        for name in os.listdir(self.storage_path):
            path = os.path.join(self.storage_path, name)
            if os.path.isfile(path):
                try:
                    uuid = UUID(name)
                    with open(path) as f:
                        _geojson = geojson.load(f)
                        self._uuid_geojson_map[uuid] = _geojson
                        self.log(logging.INFO, f"mapped {path}")
                except JSONDecodeError:
                    self.log(logging.WARN, f"unable to parse GeoJSON: {path}")
                except ValueError:
                    # file name isn't a UUID or
                    pass
                except PermissionError:
                    # no read access
                    pass

    @synchronize(_lock)
    def add(self, json: str, uuid: Optional[UUID] = None) -> UUID:
        """Add/Update UUID->GeoJSON mapping and storage."""
        # parse validate GeoJSON
        _geojson = geojson.loads(json)
        uuid = uuid or uuid4()
        path = os.path.join(self.storage_path, str(uuid))
        with open(path, "w") as f:
            f.write(json)
        self._uuid_geojson_map[uuid] = _geojson
        self.log(logging.INFO, f"wrote: {path}")
        return uuid

    @synchronize(_lock)
    def remove(self, uuid: UUID):
        """Removes UUID GeoJSON mapping and file."""
        del self._uuid_geojson_map[uuid]
        path = os.path.join(self.storage_path, str(uuid))
        os.remove(path)
        self.log(logging.WARN, f"removed: {path}")

    @synchronize(_lock)
    def get_geojson(self, uuid: UUID) -> Dict:
        """Returns GeoJSON from UUID."""
        return self._uuid_geojson_map.get(uuid).copy()

    @synchronize(_lock)
    def get_uuids(self):
        """Returns list of mapped UUIDs."""
        return list(self._uuid_geojson_map.keys())
