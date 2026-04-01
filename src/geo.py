"""
geo.py — Géocodage et calcul de distance pour la zone de livraison
"""
import math
import logging
import aiohttp

logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_HEADERS = {
    "User-Agent": "HighsCreamCBD-TelegramBot/1.0"
}


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcule la distance en km entre deux coordonnées GPS (formule de Haversine).
    """
    R = 6371.0  # Rayon terrestre en km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


async def geocode_address(address: str) -> tuple[float, float] | None:
    """
    Géocode une adresse textuelle via l'API Nominatim (OpenStreetMap).
    Retourne (latitude, longitude) ou None si non trouvé.
    """
    params = {
        "q": address,
        "format": "json",
        "limit": 1,
        "countrycodes": "fr",
        "addressdetails": 1,
    }

    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(
                NOMINATIM_URL,
                params=params,
                headers=NOMINATIM_HEADERS,
            ) as resp:
                if resp.status != 200:
                    logger.warning(f"Nominatim returned HTTP {resp.status}")
                    return None

                data = await resp.json()
                if not data:
                    logger.info(f"Adresse non trouvée : {address!r}")
                    return None

                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                logger.info(f"Adresse '{address}' → ({lat:.4f}, {lon:.4f})")
                return lat, lon

    except aiohttp.ClientError as e:
        logger.error(f"Erreur réseau Nominatim : {e}")
        return None
    except Exception as e:
        logger.error(f"Erreur inattendue géocodage : {e}")
        return None


async def reverse_geocode(lat: float, lon: float) -> str:
    """
    Géocodage inverse : coordonnées → adresse textuelle approximative.
    Retourne une chaîne lisible ou une position GPS brute en cas d'échec.
    """
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
    }

    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params, headers=NOMINATIM_HEADERS) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("display_name", f"({lat:.4f}, {lon:.4f})")
    except Exception as e:
        logger.error(f"Erreur géocodage inverse : {e}")

    return f"Position GPS ({lat:.4f}, {lon:.4f})"
