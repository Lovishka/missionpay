import os
import requests
from math import radians, sin, cos, sqrt, atan2


TICKETMASTER_URL = "https://app.ticketmaster.com/discovery/v2/events.json"


def calculate_distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
):
    earth_radius = 6371

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return earth_radius * c


def get_nearby_events(
    latitude: float,
    longitude: float,
    radius_km: int = 10,
    limit: int = 10
):
    api_key = os.getenv("TICKETMASTER_API_KEY")

    if not api_key:
        raise RuntimeError(
            "TICKETMASTER_API_KEY is not configured"
        )

    params = {
        "apikey": api_key,
        "latlong": f"{latitude},{longitude}",
        "radius": radius_km,
        "unit": "km",
        "size": limit,
        "sort": "date,asc"
    }

    response = requests.get(
        TICKETMASTER_URL,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    events = []

    for event in data.get("_embedded", {}).get("events", []):

        venue = (
            event.get("_embedded", {})
            .get("venues", [{}])[0]
        )

        location = venue.get("location", {})

        event_lat = location.get("latitude")
        event_lon = location.get("longitude")

        distance = None

        if event_lat and event_lon:
            distance = calculate_distance_km(
                latitude,
                longitude,
                float(event_lat),
                float(event_lon)
            )

        dates = event.get("dates", {}).get("start", {})

        events.append({
            "event_id": event.get("id"),
            "name": event.get("name"),

            "category": (
                event.get("classifications", [{}])[0]
                .get("segment", {})
                .get("name")
            ),

            "date": dates.get("localDate"),
            "time": dates.get("localTime"),

            "venue": venue.get("name"),
            "city": venue.get("city", {}).get("name"),

            "latitude": event_lat,
            "longitude": event_lon,

            "distance_km": (
                round(distance, 2)
                if distance is not None
                else None
            ),

            "url": event.get("url")
        })

    return events