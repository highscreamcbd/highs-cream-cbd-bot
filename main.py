"""
main.py — Point d'entrée du bot High's Cream CBD
"""
import logging
import sys
import os

# Ajouter le dossier src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN
from handlers import (
    CART_VIEW,
    CATEGORY_VIEW,
    CHECKOUT_ADDRESS,
    CHECKOUT_CONFIRM,
    CHECKOUT_NAME,
    CHECKOUT_PHONE,
    CHECKOUT_SLOT,
    MAIN_MENU,
    PRODUCT_VIEW,
    cmd_commandes,
    handle_add_to_cart,
    handle_back_to_category,
    handle_cancel,
    handle_cart,
    handle_category,
    handle_checkout_start,
    handle_clear_cart,
    handle_confirm_order,
    handle_location,
    handle_address,
    handle_main_menu,
    handle_name,
    handle_phone,
    handle_product,
    handle_remove_item,
    handle_slot,
    start,
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def build_app() -> Application:
    if not BOT_TOKEN:
        logger.critical("BOT_TOKEN manquant ! Ajoutez-le dans vos variables d'environnement.")
        sys.exit(1)

    app = Application.builder().token(BOT_TOKEN).build()

    # ── ConversationHandler principal ──────────────────────────────────────────
    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("menu", start),
        ],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(handle_category, pattern=r"^cat_"),
                CallbackQueryHandler(handle_cart, pattern=r"^cart$"),
            ],
            CATEGORY_VIEW: [
                CallbackQueryHandler(handle_product, pattern=r"^prod_"),
                CallbackQueryHandler(handle_cart, pattern=r"^cart$"),
                CallbackQueryHandler(handle_main_menu, pattern=r"^back_main$"),
            ],
            PRODUCT_VIEW: [
                CallbackQueryHandler(handle_add_to_cart, pattern=r"^add_"),
                CallbackQueryHandler(handle_back_to_category, pattern=r"^back_cat_"),
                CallbackQueryHandler(handle_cart, pattern=r"^cart$"),
            ],
            CART_VIEW: [
                CallbackQueryHandler(handle_checkout_start, pattern=r"^checkout$"),
                CallbackQueryHandler(handle_remove_item, pattern=r"^remove_"),
                CallbackQueryHandler(handle_clear_cart, pattern=r"^clear_cart$"),
                CallbackQueryHandler(handle_main_menu, pattern=r"^back_main$"),
            ],
            CHECKOUT_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name),
            ],
            CHECKOUT_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone),
            ],
            CHECKOUT_ADDRESS: [
                MessageHandler(filters.LOCATION, handle_location),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_address),
            ],
            CHECKOUT_SLOT: [
                CallbackQueryHandler(handle_slot, pattern=r"^slot_\d+$"),
            ],
            CHECKOUT_CONFIRM: [
                CallbackQueryHandler(handle_confirm_order, pattern=r"^confirm$"),
                CallbackQueryHandler(handle_cancel, pattern=r"^cancel$"),
            ],
        },
        fallbacks=[
            CommandHandler("start", start),
            CommandHandler("menu", start),
            CommandHandler("annuler", handle_cancel),
        ],
        allow_reentry=True,
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("commandes", cmd_commandes))

    logger.info("✅ Bot High's Cream CBD démarré !")
    return app


def main() -> None:
    app = build_app()
    app.run_polling(
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
