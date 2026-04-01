"""
handlers.py — Toute la logique de conversation du bot High's Cream CBD

Flux :
  /start → MAIN_MENU → CATEGORY_VIEW → PRODUCT_VIEW
                     ↘ CART_VIEW → CHECKOUT_NAME → CHECKOUT_PHONE
                                 → CHECKOUT_ADDRESS → CHECKOUT_SLOT
                                 → CHECKOUT_CONFIRM → END
"""
import logging
import uuid
from datetime import datetime, timedelta

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from config import (
    ADMIN_CHAT_ID,
    CHARTRES_LAT,
    CHARTRES_LON,
    MAX_DISTANCE_KM,
    MIN_ORDER_EUR,
    SHOP_NAME,
    SLOT_EMOJIS,
    TIME_SLOTS,
)
from geo import geocode_address, haversine_distance, reverse_geocode
from products import CATEGORIES, get_product, get_products_by_category, get_variant_by_index
from sheets import save_order

logger = logging.getLogger(__name__)

# ── États de la conversation ──────────────────────────────────────────────────
(
    MAIN_MENU,
    CATEGORY_VIEW,
    PRODUCT_VIEW,
    CART_VIEW,
    CHECKOUT_NAME,
    CHECKOUT_PHONE,
    CHECKOUT_ADDRESS,
    CHECKOUT_SLOT,
    CHECKOUT_CONFIRM,
) = range(9)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS PANIER
# ─────────────────────────────────────────────────────────────────────────────

def _cart(ctx: ContextTypes.DEFAULT_TYPE) -> dict:
    if "cart" not in ctx.user_data:
        ctx.user_data["cart"] = {}
    return ctx.user_data["cart"]


def _cart_total(cart: dict) -> int:
    return sum(item["price"] * item["qty"] for item in cart.values())


def _format_cart(cart: dict) -> str:
    if not cart:
        return "🛒 Votre panier est vide."

    lines = ["🛒 *Votre panier :*\n"]
    for item in cart.values():
        subtotal = item["price"] * item["qty"]
        lines.append(
            f"• {item['emoji']} {item['name']} _({item['variant']})_"
            f" ×{item['qty']} — *{subtotal}€*"
        )

    total = _cart_total(cart)
    lines.append(f"\n💰 *Total : {total}€*")

    if total < MIN_ORDER_EUR:
        remaining = MIN_ORDER_EUR - total
        lines.append(
            f"⚠️ _Minimum {MIN_ORDER_EUR}€ pour passer commande. Il vous manque {remaining}€._"
        )
    else:
        lines.append("✅ _Minimum atteint — vous pouvez commander !_")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS TRADUCTION DATE
# ─────────────────────────────────────────────────────────────────────────────

_DAYS_FR = {
    "Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi",
    "Thursday": "Jeudi", "Friday": "Vendredi",
    "Saturday": "Samedi", "Sunday": "Dimanche",
}
_MONTHS_FR = {
    "January": "janvier", "February": "février", "March": "mars",
    "April": "avril", "May": "mai", "June": "juin",
    "July": "juillet", "August": "août", "September": "septembre",
    "October": "octobre", "November": "novembre", "December": "décembre",
}


def _date_fr(dt: datetime) -> str:
    s = dt.strftime("%A %d %B %Y")
    for en, fr in {**_DAYS_FR, **_MONTHS_FR}.items():
        s = s.replace(en, fr)
    return s


# ─────────────────────────────────────────────────────────────────────────────
# KEYBOARDS
# ─────────────────────────────────────────────────────────────────────────────

def _main_menu_kb() -> InlineKeyboardMarkup:
    cats = list(CATEGORIES.items())
    keyboard = []
    for i in range(0, len(cats), 2):
        row = [
            InlineKeyboardButton(cat["name"], callback_data=f"cat_{cid}")
            for cid, cat in cats[i : i + 2]
        ]
        keyboard.append(row)
    keyboard.append(
        [InlineKeyboardButton("🛒 Mon panier", callback_data="cart")]
    )
    return InlineKeyboardMarkup(keyboard)


def _back_row(back_cb: str, cart_label: str = "") -> list:
    row = [InlineKeyboardButton("🔙 Retour", callback_data=back_cb)]
    if cart_label:
        row.append(InlineKeyboardButton(f"🛒 {cart_label}", callback_data="cart"))
    return row


# ─────────────────────────────────────────────────────────────────────────────
# 1. ACCUEIL / MENU PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Point d'entrée — affiche le menu des catégories."""
    # Réinitialiser seulement les données de checkout, pas le panier
    for key in ["checkout_name", "checkout_phone", "checkout_address",
                "checkout_lat", "checkout_lon", "checkout_distance",
                "checkout_slot", "delivery_date", "delivery_date_raw",
                "current_cat", "current_prod"]:
        ctx.user_data.pop(key, None)

    cart = _cart(ctx)
    total = _cart_total(cart)
    cart_badge = f" | 🛒 {total}€" if total > 0 else ""

    text = (
        f"🌿 *Bienvenue chez {SHOP_NAME} !*\n\n"
        "Votre boutique CBD à Chartres, livrée à domicile 🚚\n\n"
        f"📦 Commande minimum : *{MIN_ORDER_EUR}€*\n"
        f"📍 Zone : *{MAX_DISTANCE_KM}km autour de Chartres*\n"
        "🕐 Livraison *le lendemain*, créneau au choix\n"
        "💳 Paiement *à la livraison*\n\n"
        f"Choisissez une catégorie{cart_badge} :"
    )

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text, reply_markup=_main_menu_kb(), parse_mode=ParseMode.MARKDOWN_V2
        )
    else:
        await update.message.reply_text(
            text, reply_markup=_main_menu_kb(), parse_mode=ParseMode.MARKDOWN_V2
        )

    return MAIN_MENU


async def handle_main_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    return await start(update, ctx)


# ─────────────────────────────────────────────────────────────────────────────
# 2. CATÉGORIE
# ─────────────────────────────────────────────────────────────────────────────

async def _show_category(cat_id: str, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    ctx.user_data["current_cat"] = cat_id
    cat = CATEGORIES[cat_id]
    products = get_products_by_category(cat_id)

    keyboard = [
        [InlineKeyboardButton(f"{p['emoji']} {p['name']}", callback_data=f"prod_{p['id']}")]
        for p in products
    ]

    cart = _cart(ctx)
    total = _cart_total(cart)
    cart_label = f"{total}€" if total > 0 else ""

    keyboard.append(_back_row("back_main", cart_label))

    text = (
        f"*{_escape(cat['name'])}*\n"
        f"_{_escape(cat['description'])}_\n\n"
        "Choisissez un produit :"
    )

    q = update.callback_query
    await q.answer()
    await q.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN_V2
    )
    return CATEGORY_VIEW


async def handle_category(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    cat_id = update.callback_query.data.removeprefix("cat_")
    return await _show_category(cat_id, update, ctx)


async def handle_back_to_category(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    cat_id = update.callback_query.data.removeprefix("back_cat_")
    return await _show_category(cat_id, update, ctx)


# ─────────────────────────────────────────────────────────────────────────────
# 3. PRODUIT
# ─────────────────────────────────────────────────────────────────────────────

async def _show_product(prod_id: str, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    ctx.user_data["current_prod"] = prod_id
    prod = get_product(prod_id)
    if not prod:
        await update.callback_query.answer("Produit introuvable.", show_alert=True)
        return CATEGORY_VIEW

    variants = list(prod["variants"].items())
    keyboard = [
        [InlineKeyboardButton(
            f"➕ {label} — {price}€",
            callback_data=f"add_{prod_id}_{i}"
        )]
        for i, (label, price) in enumerate(variants)
    ]

    cat_id = prod["cat"]
    cart = _cart(ctx)
    total = _cart_total(cart)
    cart_label = f"{total}€" if total > 0 else ""
    keyboard.append(_back_row(f"back_cat_{cat_id}", cart_label))

    text = (
        f"{prod['emoji']} *{_escape(prod['name'])}*\n\n"
        f"{_escape(prod['description'])}\n\n"
        "*Choisissez votre format :*"
    )

    q = update.callback_query
    await q.answer()
    await q.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN_V2
    )
    return PRODUCT_VIEW


async def handle_product(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    prod_id = update.callback_query.data.removeprefix("prod_")
    return await _show_product(prod_id, update, ctx)


async def handle_add_to_cart(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query

    # Format callback : add_{prod_id}_{variant_idx}
    # prod_id peut contenir des underscores (ex: fl_og) → on prend le dernier segment comme idx
    parts = q.data.split("_")
    variant_idx = int(parts[-1])
    prod_id = "_".join(parts[1:-1])

    result = get_variant_by_index(prod_id, variant_idx)
    if not result:
        await q.answer("Erreur produit.", show_alert=True)
        return PRODUCT_VIEW

    variant_label, price = result
    prod = get_product(prod_id)

    cart = _cart(ctx)
    cart_key = f"{prod_id}_{variant_idx}"

    if cart_key in cart:
        cart[cart_key]["qty"] += 1
    else:
        cart[cart_key] = {
            "product_id": prod_id,
            "name": prod["name"],
            "variant": variant_label,
            "price": price,
            "qty": 1,
            "emoji": prod["emoji"],
        }

    total = _cart_total(cart)
    await q.answer(
        f"✅ {prod['name']} ({variant_label}) ajouté !\nTotal panier : {total}€",
        show_alert=False,
    )

    # Revenir sur la fiche produit (rafraîchi)
    return await _show_product(prod_id, update, ctx)


# ─────────────────────────────────────────────────────────────────────────────
# 4. PANIER
# ─────────────────────────────────────────────────────────────────────────────

async def _show_cart(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    cart = _cart(ctx)
    total = _cart_total(cart)
    text = _format_cart(cart)

    keyboard = []

    # Bouton "retirer" par article
    for key, item in cart.items():
        keyboard.append([
            InlineKeyboardButton(
                f"➖ {item['name']} ({item['variant']})",
                callback_data=f"remove_{key}",
            )
        ])

    bottom = [InlineKeyboardButton("🛍️ Continuer les achats", callback_data="back_main")]
    if cart:
        bottom.append(InlineKeyboardButton("🗑️ Vider", callback_data="clear_cart"))
    keyboard.append(bottom)

    if total >= MIN_ORDER_EUR:
        keyboard.append(
            [InlineKeyboardButton("✅ Commander →", callback_data="checkout")]
        )

    markup = InlineKeyboardMarkup(keyboard)

    q = update.callback_query
    if q:
        await q.answer()
        await q.edit_message_text(text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN_V2)
    else:
        await update.message.reply_text(text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN_V2)

    return CART_VIEW


async def handle_cart(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    return await _show_cart(update, ctx)


async def handle_remove_item(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    key = update.callback_query.data.removeprefix("remove_")
    cart = _cart(ctx)

    if key in cart:
        item = cart[key]
        if item["qty"] > 1:
            cart[key]["qty"] -= 1
        else:
            del cart[key]

    return await _show_cart(update, ctx)


async def handle_clear_cart(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    ctx.user_data["cart"] = {}
    return await _show_cart(update, ctx)


# ─────────────────────────────────────────────────────────────────────────────
# 5. CHECKOUT — Nom
# ─────────────────────────────────────────────────────────────────────────────

async def handle_checkout_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    cart = _cart(ctx)
    total = _cart_total(cart)

    if total < MIN_ORDER_EUR:
        await q.answer(
            f"Minimum {MIN_ORDER_EUR}€ requis. Total actuel : {total}€", show_alert=True
        )
        return CART_VIEW

    await q.answer()
    await q.edit_message_text(
        "📝 *Passons à la commande\\!*\n\n"
        "Votre *prénom et nom* :\n"
        "_\\(Ex : Jean Dupont\\)_",
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    return CHECKOUT_NAME


async def handle_name(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.message.text.strip()
    if len(name) < 2:
        await update.message.reply_text("⚠️ Veuillez entrer un nom valide.")
        return CHECKOUT_NAME

    ctx.user_data["checkout_name"] = name
    await update.message.reply_text(
        f"👋 Bonjour *{_escape(name)}* \\!\n\n"
        "📱 Votre *numéro de téléphone* :\n"
        "_\\(Ex : 06 12 34 56 78\\)_",
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    return CHECKOUT_PHONE


# ─────────────────────────────────────────────────────────────────────────────
# 6. CHECKOUT — Téléphone
# ─────────────────────────────────────────────────────────────────────────────

async def handle_phone(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    raw = update.message.text.strip()
    cleaned = raw.replace(" ", "").replace(".", "").replace("-", "").replace("/", "")

    valid = (
        cleaned.startswith(("06", "07", "+336", "+337", "0033"))
        and 10 <= len(cleaned) <= 13
    )

    if not valid:
        await update.message.reply_text(
            "⚠️ Numéro invalide\\. Entrez un numéro mobile français\\.\n"
            "_\\(Ex : 06 12 34 56 78\\)_",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return CHECKOUT_PHONE

    ctx.user_data["checkout_phone"] = raw
    await update.message.reply_text(
        "📍 *Votre adresse de livraison* :\n\n"
        "Tapez votre adresse complète ou *partagez votre position* 📌\n"
        "_\\(Ex : 15 rue de la Paix, Chartres 28000\\)_\n\n"
        f"⚠️ _Livraison uniquement dans un rayon de {MAX_DISTANCE_KM}km autour de Chartres\\._",
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    return CHECKOUT_ADDRESS


# ─────────────────────────────────────────────────────────────────────────────
# 7. CHECKOUT — Adresse
# ─────────────────────────────────────────────────────────────────────────────

async def handle_address(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """L'utilisateur tape son adresse en texte."""
    address_text = update.message.text.strip()

    await update.message.reply_text("🔍 Vérification de votre adresse…")

    coords = await geocode_address(address_text)

    if not coords:
        await update.message.reply_text(
            "❌ Adresse introuvable\\. Précisez davantage :\n"
            "_\\(Ex : 15 rue Victor Hugo, Chartres 28000\\)_",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return CHECKOUT_ADDRESS

    lat, lon = coords
    distance = haversine_distance(lat, lon, CHARTRES_LAT, CHARTRES_LON)

    if distance > MAX_DISTANCE_KM:
        await update.message.reply_text(
            f"❌ *Zone hors livraison*\n\n"
            f"Votre adresse est à *{distance:.1f}km* de Chartres\\.\n"
            f"Nous livrons uniquement dans un rayon de *{MAX_DISTANCE_KM}km*\\.\n\n"
            "Essayez une autre adresse ou contactez\\-nous directement\\.",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return CHECKOUT_ADDRESS

    ctx.user_data.update({
        "checkout_address": address_text,
        "checkout_lat": lat,
        "checkout_lon": lon,
        "checkout_distance": distance,
    })

    return await _show_time_slots(update, ctx, distance)


async def handle_location(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """L'utilisateur partage sa position GPS."""
    loc = update.message.location
    lat, lon = loc.latitude, loc.longitude

    distance = haversine_distance(lat, lon, CHARTRES_LAT, CHARTRES_LON)

    if distance > MAX_DISTANCE_KM:
        await update.message.reply_text(
            f"❌ *Zone hors livraison*\n\n"
            f"Votre position est à *{distance:.1f}km* de Chartres\\.\n"
            f"Nous livrons dans un rayon de *{MAX_DISTANCE_KM}km* maximum\\.",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return CHECKOUT_ADDRESS

    # Géocodage inverse pour avoir une adresse lisible
    address = await reverse_geocode(lat, lon)

    ctx.user_data.update({
        "checkout_address": address,
        "checkout_lat": lat,
        "checkout_lon": lon,
        "checkout_distance": distance,
    })

    return await _show_time_slots(update, ctx, distance)


# ─────────────────────────────────────────────────────────────────────────────
# 8. CHECKOUT — Créneau horaire
# ─────────────────────────────────────────────────────────────────────────────

async def _show_time_slots(
    update: Update, ctx: ContextTypes.DEFAULT_TYPE, distance: float
) -> int:
    tomorrow = datetime.now() + timedelta(days=1)
    date_str = _date_fr(tomorrow)

    ctx.user_data["delivery_date"] = date_str
    ctx.user_data["delivery_date_raw"] = tomorrow.strftime("%Y-%m-%d")

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"{SLOT_EMOJIS[i]} {slot}", callback_data=f"slot_{i}")]
        for i, slot in enumerate(TIME_SLOTS)
    ])

    text = (
        f"✅ Adresse validée \\! _{_escape(f'({distance:.1f}km de Chartres)')}_\n\n"
        f"📅 *Choisissez votre créneau de livraison*\n"
        f"Livraison prévue le : *{_escape(date_str)}*"
    )

    msg = update.message or (update.callback_query and update.callback_query.message)
    if update.message:
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN_V2)
    else:
        await update.callback_query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN_V2)

    return CHECKOUT_SLOT


async def handle_slot(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()

    slot_idx = int(q.data.removeprefix("slot_"))
    slot = TIME_SLOTS[slot_idx]
    ctx.user_data["checkout_slot"] = slot

    return await _show_order_summary(update, ctx)


# ─────────────────────────────────────────────────────────────────────────────
# 9. CHECKOUT — Récapitulatif & confirmation
# ─────────────────────────────────────────────────────────────────────────────

async def _show_order_summary(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    ud = ctx.user_data
    cart = _cart(ctx)
    total = _cart_total(cart)

    items_text = "\n".join(
        f"  • {item['emoji']} {item['name']} \\({_escape(item['variant'])}\\)"
        f" ×{item['qty']} \\= {item['price'] * item['qty']}€"
        for item in cart.values()
    )

    text = (
        "📋 *Récapitulatif de votre commande*\n\n"
        f"👤 *Nom :* {_escape(ud['checkout_name'])}\n"
        f"📱 *Tél :* {_escape(ud['checkout_phone'])}\n"
        f"📍 *Adresse :* {_escape(ud['checkout_address'])}\n"
        f"📅 *Livraison :* {_escape(ud['delivery_date'])}\n"
        f"🕐 *Créneau :* {_escape(ud['checkout_slot'])}\n"
        f"💳 *Paiement :* À la livraison\n\n"
        f"🛍️ *Articles :*\n{items_text}\n\n"
        f"💰 *TOTAL : {total}€*\n\n"
        "Confirmez\\-vous votre commande ?"
    )

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Confirmer", callback_data="confirm"),
        InlineKeyboardButton("❌ Annuler", callback_data="cancel"),
    ]])

    q = update.callback_query
    if q:
        await q.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN_V2)
    else:
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN_V2)

    return CHECKOUT_CONFIRM


async def handle_confirm_order(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()

    ud = ctx.user_data
    cart = _cart(ctx)
    total = _cart_total(cart)

    order_id = f"HCC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"

    order = {
        "order_id": order_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "name": ud.get("checkout_name", ""),
        "phone": ud.get("checkout_phone", ""),
        "address": ud.get("checkout_address", ""),
        "distance": ud.get("checkout_distance", 0.0),
        "date": ud.get("delivery_date", ""),
        "slot": ud.get("checkout_slot", ""),
        "items": [
            {
                "name": item["name"],
                "variant": item["variant"],
                "qty": item["qty"],
                "price": item["price"],
                "total": item["price"] * item["qty"],
                "emoji": item["emoji"],
            }
            for item in cart.values()
        ],
        "total": total,
    }

    # Sauvegarde Google Sheets (non bloquant si erreur)
    try:
        save_order(order)
    except Exception as e:
        logger.error(f"Sheets error: {e}")

    # Notification admin Telegram
    try:
        await _notify_admin(ctx, order)
    except Exception as e:
        logger.error(f"Admin notify error: {e}")

    # Message de confirmation client
    name_escaped = _escape(ud.get("checkout_name", ""))
    await q.edit_message_text(
        f"🎉 *Commande confirmée \\!*\n\n"
        f"Merci {name_escaped} \\! 🌿\n\n"
        f"🔖 *N° de commande :* `{order_id}`\n"
        f"📅 *Livraison :* {_escape(ud.get('delivery_date', ''))}\n"
        f"🕐 *Créneau :* {_escape(ud.get('checkout_slot', ''))}\n"
        f"💰 *Total à régler :* *{total}€* \\(à la livraison\\)\n\n"
        "Notre équipe vous contactera pour confirmer\\.\n"
        "À très bientôt chez High's Cream CBD 🌿",
        parse_mode=ParseMode.MARKDOWN_V2,
    )

    ctx.user_data["cart"] = {}
    return ConversationHandler.END


async def _notify_admin(ctx: ContextTypes.DEFAULT_TYPE, order: dict) -> None:
    """Envoie un récapitulatif de commande à l'admin via Telegram."""
    if not ADMIN_CHAT_ID:
        return

    items_text = "\n".join(
        f"  • {item['emoji']} {item['name']} ({item['variant']}) ×{item['qty']} = {item['total']}€"
        for item in order["items"]
    )

    msg = (
        f"🔔 *NOUVELLE COMMANDE* `{order['order_id']}`\n\n"
        f"👤 *Client :* {order['name']}\n"
        f"📱 *Tél :* {order['phone']}\n"
        f"📍 *Adresse :* {order['address']} _({order['distance']:.1f}km)_\n"
        f"📅 *Livraison :* {order['date']}\n"
        f"🕐 *Créneau :* {order['slot']}\n\n"
        f"🛍️ *Articles :*\n{items_text}\n\n"
        f"💰 *TOTAL : {order['total']}€*\n"
        f"💳 *Paiement :* À la livraison\n\n"
        f"🕓 *Commande passée le :* {order['timestamp']}"
    )

    await ctx.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=msg,
        parse_mode=ParseMode.MARKDOWN_V2,
    )


async def handle_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Annule la commande en cours."""
    q = update.callback_query
    if q:
        await q.answer("Commande annulée")
        await q.edit_message_text(
            "❌ Commande annulée\\.\n\n"
            "Tapez /menu pour revenir au catalogue\\.",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    else:
        await update.message.reply_text(
            "❌ Commande annulée\\. Tapez /menu pour recommencer\\.",
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    return ConversationHandler.END


# ─────────────────────────────────────────────────────────────────────────────
# COMMANDE /commandes (admin)
# ─────────────────────────────────────────────────────────────────────────────

async def cmd_commandes(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Commande admin pour vérifier le bon fonctionnement."""
    if update.effective_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ Accès réservé à l'administrateur\\.", parse_mode=ParseMode.MARKDOWN_V2)
        return
    await update.message.reply_text(
        "📊 Les commandes sont sauvegardées dans votre Google Sheet\\.\n"
        "Utilisez le lien dans vos variables d'environnement pour y accéder\\.",
        parse_mode=ParseMode.MARKDOWN_V2,
    )


# ─────────────────────────────────────────────────────────────────────────────
# ESCAPE Markdown V2
# ─────────────────────────────────────────────────────────────────────────────

def _escape(text: str) -> str:
    """Échappe les caractères spéciaux MarkdownV2 de Telegram."""
    special = r"\_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{c}" if c in special else c for c in str(text))
