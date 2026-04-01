"""
products.py — Catalogue complet des produits High's Cream CBD

Structure d'un produit :
  id       : identifiant unique
  cat      : catégorie parente (clé dans CATEGORIES)
  name     : nom affiché
  description : description courte
  variants : dict {label: prix_en_euros}
  emoji    : émoji affiché dans les menus

⚠️  Pour modifier les prix ou ajouter des produits, éditez ce fichier.
"""

# ── Catégories ────────────────────────────────────────────────────────────────
CATEGORIES: dict = {
    "fleur_cbd": {
        "name": "🌿 Fleur CBD",
        "description": "Fleurs de CBD cultivées avec soin, riches en cannabidiol naturel",
    },
    "resine_cbd": {
        "name": "🍯 Résine CBD",
        "description": "Hash et résines CBD artisanaux aux arômes intenses",
    },
    "vape_cbd": {
        "name": "💨 Vape CBD",
        "description": "Cartouches et pens CBD pour une expérience vapeur douce",
    },
    "mol_fleur": {
        "name": "🔬 Fleur Molécules",
        "description": "Fleurs enrichies en molécules alternatives (HHC, H4CBD, HHCPO…)",
    },
    "mol_resine": {
        "name": "🔬 Résine Molécules",
        "description": "Résines et hash aux molécules alternatives, effets prononcés",
    },
    "mol_vape": {
        "name": "🔬 Vape Molécules",
        "description": "Cartouches et pens aux molécules pour vapeur intense",
    },
    "edibles": {
        "name": "🍪 Edibles",
        "description": "Gâteaux et bonbons CBD, CBN et THC — fait maison",
    },
}

# ── Produits ──────────────────────────────────────────────────────────────────
PRODUCTS: dict = {

    # ── FLEUR CBD ──────────────────────────────────────────────────────────────
    "fl_og": {
        "cat": "fleur_cbd",
        "name": "OG Kush CBD",
        "description": "Saveurs terreuses et épicées. Relaxation profonde, idéal pour le soir.",
        "variants": {"2g": 9, "5g": 18, "10g": 32},
        "emoji": "🌿",
    },
    "fl_amnesia": {
        "cat": "fleur_cbd",
        "name": "Amnesia Haze CBD",
        "description": "Notes citronnées fraîches. Légèrement tonique et créatif.",
        "variants": {"2g": 9, "5g": 18, "10g": 32},
        "emoji": "🌿",
    },
    "fl_gelato": {
        "cat": "fleur_cbd",
        "name": "Gelato CBD",
        "description": "Saveurs sucrées et fruitées. Effet équilibré corps et esprit.",
        "variants": {"2g": 10, "5g": 20, "10g": 36},
        "emoji": "🌿",
    },
    "fl_zkittlez": {
        "cat": "fleur_cbd",
        "name": "Zkittlez CBD",
        "description": "Parfum fruité intense, notes de raisin et de tropical. Relaxant.",
        "variants": {"2g": 10, "5g": 20, "10g": 36},
        "emoji": "🌿",
    },
    "fl_purple": {
        "cat": "fleur_cbd",
        "name": "Purple Haze CBD",
        "description": "Notes de baies et de terre. Relaxation profonde sans somnolence excessive.",
        "variants": {"2g": 11, "5g": 22, "10g": 40},
        "emoji": "🌿",
    },
    "fl_wedding": {
        "cat": "fleur_cbd",
        "name": "Wedding Cake CBD",
        "description": "Arômes vanillés et épicés. Très apprécié pour la détente musculaire.",
        "variants": {"2g": 11, "5g": 22, "10g": 40},
        "emoji": "🌿",
    },

    # ── RÉSINE CBD ─────────────────────────────────────────────────────────────
    "rs_maroc": {
        "cat": "resine_cbd",
        "name": "Hash Maroc CBD",
        "description": "Hash traditionnel marocain, texture souple. Arômes épicés et doux.",
        "variants": {"2g": 12, "5g": 24, "10g": 44},
        "emoji": "🍯",
    },
    "rs_charas": {
        "cat": "resine_cbd",
        "name": "Charas CBD",
        "description": "Résine himalayenne artisanale. Arômes terreux, boisés et profonds.",
        "variants": {"2g": 13, "5g": 26, "10g": 48},
        "emoji": "🍯",
    },
    "rs_pollen": {
        "cat": "resine_cbd",
        "name": "Pollen Blonde CBD",
        "description": "Pollen pressé à texture granuleuse. Goût fin et délicat.",
        "variants": {"2g": 11, "5g": 22, "10g": 40},
        "emoji": "🍯",
    },
    "rs_afghan": {
        "cat": "resine_cbd",
        "name": "Hash Afghan CBD",
        "description": "Hash afghan traditionnel. Très aromatique, texture ferme.",
        "variants": {"2g": 13, "5g": 26, "10g": 48},
        "emoji": "🍯",
    },

    # ── VAPE CBD ───────────────────────────────────────────────────────────────
    "vp_cart_og": {
        "cat": "vape_cbd",
        "name": "Cartouche OG Kush CBD",
        "description": "Compatible batterie 510. Concentré CBD pur. Goût OG authentique.",
        "variants": {"0.5ml": 22, "1ml": 38},
        "emoji": "💨",
    },
    "vp_cart_gelato": {
        "cat": "vape_cbd",
        "name": "Cartouche Gelato CBD",
        "description": "Compatible batterie 510. Saveur sucrée et crémeuse.",
        "variants": {"0.5ml": 22, "1ml": 38},
        "emoji": "💨",
    },
    "vp_pen_fruit": {
        "cat": "vape_cbd",
        "name": "Pen Jetable Fruit Mix CBD",
        "description": "Prêt à l'emploi, sans batterie. Mélange fruité tropical. ~300 puffs.",
        "variants": {"1 pen": 25},
        "emoji": "💨",
    },
    "vp_pen_mint": {
        "cat": "vape_cbd",
        "name": "Pen Jetable Ice Mint CBD",
        "description": "Fraîcheur mentholée intense. Prêt à l'emploi. ~300 puffs.",
        "variants": {"1 pen": 25},
        "emoji": "💨",
    },
    "vp_liquid": {
        "cat": "vape_cbd",
        "name": "E-liquide CBD 10ml",
        "description": "Pour cigarette électronique standard. CBD 5%. Plusieurs saveurs disponibles.",
        "variants": {"10ml": 18, "2×10ml": 32},
        "emoji": "💨",
    },

    # ── FLEUR MOLÉCULES ────────────────────────────────────────────────────────
    "mf_hhc": {
        "cat": "mol_fleur",
        "name": "Fleur HHC",
        "description": "Hexahydrocannabinol. Effet euphorisant et relaxant plus prononcé que le CBD.",
        "variants": {"2g": 14, "5g": 28, "10g": 50},
        "emoji": "🔬",
    },
    "mf_h4cbd": {
        "cat": "mol_fleur",
        "name": "Fleur H4CBD",
        "description": "Tétrahydrocannabidiol. Très relaxant, agit fortement sur le corps.",
        "variants": {"2g": 14, "5g": 28, "10g": 50},
        "emoji": "🔬",
    },
    "mf_hhcpo": {
        "cat": "mol_fleur",
        "name": "Fleur HHCPO",
        "description": "HHC-O Acétate. Effet intense et durable, plus puissant que le HHC.",
        "variants": {"2g": 16, "5g": 32, "10g": 58},
        "emoji": "🔬",
    },
    "mf_thcp": {
        "cat": "mol_fleur",
        "name": "Fleur THCP CBD",
        "description": "Enrichie en THCP trace. Effet relaxant très profond.",
        "variants": {"2g": 18, "5g": 35, "10g": 64},
        "emoji": "🔬",
    },

    # ── RÉSINE MOLÉCULES ───────────────────────────────────────────────────────
    "mr_hhc": {
        "cat": "mol_resine",
        "name": "Hash HHC",
        "description": "Résine artisanale enrichie en HHC. Arômes terreux intenses.",
        "variants": {"2g": 16, "5g": 32, "10g": 58},
        "emoji": "🔬",
    },
    "mr_h4cbd": {
        "cat": "mol_resine",
        "name": "Hash H4CBD",
        "description": "Résine H4CBD. Texture souple, arômes épicés, effet puissant.",
        "variants": {"2g": 16, "5g": 32, "10g": 58},
        "emoji": "🔬",
    },
    "mr_hhcpo": {
        "cat": "mol_resine",
        "name": "Hash HHCPO",
        "description": "Hash au HHC-O Acétate. Pour les amateurs d'effets intenses.",
        "variants": {"2g": 18, "5g": 35, "10g": 64},
        "emoji": "🔬",
    },

    # ── VAPE MOLÉCULES ─────────────────────────────────────────────────────────
    "mv_hhc": {
        "cat": "mol_vape",
        "name": "Cartouche HHC",
        "description": "Compatible batterie 510. Concentré HHC premium. Saveurs variées.",
        "variants": {"0.5ml": 28, "1ml": 50},
        "emoji": "🔬",
    },
    "mv_h4cbd": {
        "cat": "mol_vape",
        "name": "Pen Jetable H4CBD",
        "description": "Prêt à l'emploi. 1ml de concentré H4CBD. ~300 puffs.",
        "variants": {"1 pen": 32},
        "emoji": "🔬",
    },
    "mv_hhcpo": {
        "cat": "mol_vape",
        "name": "Cartouche HHCPO",
        "description": "Compatible batterie 510. HHC-O Acétate premium — effet intense.",
        "variants": {"0.5ml": 30, "1ml": 55},
        "emoji": "🔬",
    },

    # ── EDIBLES ────────────────────────────────────────────────────────────────
    "ed_brownie_cbd": {
        "cat": "edibles",
        "name": "Brownie CBD 25mg",
        "description": "Brownie artisanal au chocolat noir. 25mg CBD par pièce. Fait maison.",
        "variants": {"1 pièce": 8, "4 pièces": 28},
        "emoji": "🍪",
    },
    "ed_cookie": {
        "cat": "edibles",
        "name": "Cookie CBD / THC",
        "description": "Cookie artisanal. Mélange CBD + THC (traces légales). Gourmand et relaxant.",
        "variants": {"1 pièce": 10, "4 pièces": 36},
        "emoji": "🍪",
    },
    "ed_gummies_cbd": {
        "cat": "edibles",
        "name": "Gummies CBD 10mg",
        "description": "Bonbons gélifiés fruités. 10mg CBD/pièce. Sans sucre ajouté.",
        "variants": {"pack 10": 15, "pack 20": 26},
        "emoji": "🍬",
    },
    "ed_gummies_cbn": {
        "cat": "edibles",
        "name": "Gummies CBN Sommeil",
        "description": "Bonbons au CBN spécial sommeil. 5mg/pièce. Relaxant naturel profond.",
        "variants": {"pack 10": 18, "pack 20": 30},
        "emoji": "🍬",
    },
    "ed_gummies_thc": {
        "cat": "edibles",
        "name": "Gummies THC / CBD",
        "description": "Bonbons équilibrés THC + CBD. Effet relaxant corps et esprit.",
        "variants": {"pack 5": 20, "pack 10": 35},
        "emoji": "🍬",
    },
    "ed_chocolat": {
        "cat": "edibles",
        "name": "Chocolat CBD 50mg",
        "description": "Tablette de chocolat noir artisanale. 50mg CBD. Goût intense.",
        "variants": {"1 tablette": 12, "3 tablettes": 32},
        "emoji": "🍫",
    },
    "ed_caramel": {
        "cat": "edibles",
        "name": "Caramels CBN / CBD",
        "description": "Caramels fondants artisanaux. Mélange CBN + CBD pour la détente.",
        "variants": {"pack 5": 14, "pack 10": 25},
        "emoji": "🍬",
    },
}


# ── Helpers ───────────────────────────────────────────────────────────────────
def get_products_by_category(cat_id: str) -> list:
    """Retourne la liste des produits d'une catégorie donnée."""
    return [
        {"id": pid, **prod}
        for pid, prod in PRODUCTS.items()
        if prod["cat"] == cat_id
    ]


def get_product(prod_id: str):
    """Retourne un produit par son ID ou None si introuvable."""
    prod = PRODUCTS.get(prod_id)
    if prod:
        return {"id": prod_id, **prod}
    return None


def get_variant_by_index(prod_id: str, idx: int):
    """Retourne (label_variant, prix) pour l'index donné, ou None."""
    prod = PRODUCTS.get(prod_id)
    if not prod:
        return None
    variants = list(prod["variants"].items())
    if 0 <= idx < len(variants):
        return variants[idx]
    return None
