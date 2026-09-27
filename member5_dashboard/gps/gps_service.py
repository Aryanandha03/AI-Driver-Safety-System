"""Location provider with deterministic mock mode and graceful failure."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import os
from typing import Protocol


@dataclass
class Location:
    latitude: float
    longitude: float
    timestamp: str
    source: str


class LocationProvider(Protocol):
    def get_location(self) -> Location: ...


class MockGPS:
    def __init__(self, latitude: float = 37.4219999, longitude: float = -122.0840575):
        self.latitude, self.longitude = latitude, longitude

    def get_location(self) -> Location:
        return Location(self.latitude, self.longitude,
                        datetime.now(timezone.utc).isoformat(timespec="seconds"), "mock")


class GPSService:
    """Uses MOCK by default. A real provider can be injected by a host application."""
    def __init__(self, provider: LocationProvider | None = None, mode: str | None = None):
        self.mode = (mode or os.getenv("GPS_MODE", "MOCK")).upper()
        self.provider = provider or MockGPS()
        self.last_error: str | None = None
        self.latest_location: Location | None = None

    def get_current_location(self) -> Location | None:
        try:
            location = self.provider.get_location()
            if not (-90 <= location.latitude <= 90 and -180 <= location.longitude <= 180):
                raise ValueError("provider returned invalid coordinates")
            self.latest_location, self.last_error = location, None
            return location
        except Exception as exc:  # Provider errors must never crash the safety UI.
            self.last_error = str(exc)
            return self.latest_location

    def latest(self) -> dict | None:
        loc = self.latest_location
        return asdict(loc) if loc else None
