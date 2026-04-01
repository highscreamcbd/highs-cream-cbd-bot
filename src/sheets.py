"""
sheets.py — Sauvegarde des commandes dans Google Sheets via gspread
"""
import json
import logging
import os

import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

HEADERS = [
    "N° Commande",
    "Date / Heure",
    "Nom client",
    "Téléphone",
    "Adresse livraison",
    "Distance (km)",
    "Date livraison",
    "Créneau",
    "Articles",
    "Total (€)",
    "Statut",
]


def _get_worksheet():
    """Ouvre le Google Sheet et retourne la première feuille."""
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON", "")
    sheet_id = os.getenv("GOOGLE_SHEETS_ID", "")

    if not creds_json or not sheet_id:
        logger.warning("Google Sheets non configuré — commande non sauvegardée.")
        return None

    try:
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.sheet1

        # Ajouter les en-têtes si la feuille est vide
        existing = worksheet.row_values(1)
        if not existing or existing[0] != HEADERS[0]:
            worksheet.insert_row(HEADERS, index=1)

        return worksheet

    except json.JSONDecodeError as e:
        logger.error(f"GOOGLE_CREDENTIALS_JSON invalide : {e}")
        return None
    except Exception as e:
        logger.error(f"Erreur connexion Google Sheets : {e}")
        return None


def save_order(order: dict) -> bool:
    """
    Enregistre une commande dans Google Sheets.

    Format attendu du dict `order` :
      order_id, timestamp, name, phone, address, distance,
      date (str lisible), slot, items (list de dicts), total
    """
    try:
        worksheet = _get_worksheet()
        if worksheet is None:
            return False

        # Formater les articles en une ligne lisible
        items_str = " | ".join(
            f"{item['name']} {item['variant']} ×{item['qty']} ({item['total']}€)"
            for item in order.get("items", [])
        )

        row = [
            order.get("order_id", ""),
            order.get("timestamp", ""),
            order.get("name", ""),
            order.get("phone", ""),
            order.get("address", ""),
            f"{order.get('distance', 0):.1f}",
            order.get("date", ""),
            order.get("slot", ""),
            items_str,
            f"{order.get('total', 0)}",
            "En attente",
        ]

        worksheet.append_row(row)
        logger.info(f"Commande {order.get('order_id')} enregistrée dans Google Sheets.")
        return True

    except Exception as e:
        logger.error(f"Erreur sauvegarde Google Sheets : {e}")
        return False
