"""
config.py — Configuration centrale du bot High's Cream CBD
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Telegram ──────────────────────────────────────────────────────────────────
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
ADMIN_CHAT_ID: int = int(os.getenv("ADMIN_CHAT_ID", "0"))

# ── Google Sheets ─────────────────────────────────────────────────────────────
GOOGLE_SHEETS_ID: str = os.getenv("GOOGLE_SHEETS_ID", "")
GOOGLE_CREDENTIALS_JSON: str = os.getenv("GOOGLE_CREDENTIALS_JSON", "")

# ── Livraison ─────────────────────────────────────────────────────────────────
CHARTRES_LAT: float = 48.4469      # Latitude de Chartres
CHARTRES_LON: float = 1.4876       # Longitude de Chartres
MAX_DISTANCE_KM: float = 10.0      # Rayon de livraison en km
MIN_ORDER_EUR: int = 100           # Commande minimum en euros

# ── Créneaux horaires de livraison ────────────────────────────────────────────
TIME_SLOTS: list[str] = [
    "09h00 – 12h00",
    "12h00 – 15h00",
    "15h00 – 18h00",
    "18h00 – 21h00",
]

SLOT_EMOJIS: list[str] = ["🕘", "☀️", "🌅", "🌆"]

# ── Boutique ──────────────────────────────────────────────────────────────────
SHOP_NAME: str = "High's Cream CBD"
SHOP_CITY: str = "Chartres"
