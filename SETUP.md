# Guide de déploiement — Bot Telegram High's Cream CBD

## Vue d'ensemble

Le bot est écrit en Python 3.11 et utilise :
- **python-telegram-bot** v20 pour l'interface Telegram
- **gspread** pour enregistrer les commandes dans Google Sheets
- **aiohttp** pour le géocodage d'adresses (gratuit, sans clé API)

---

## Étape 1 — Créer le bot Telegram

1. Ouvrez Telegram et cherchez **@BotFather**
2. Envoyez `/newbot`
3. Donnez un **nom** au bot : `High's Cream CBD`
4. Donnez un **nom d'utilisateur** (doit finir par `bot`) : ex. `HighsCreamCBD_bot`
5. BotFather vous donne un **token** — copiez-le, c'est votre `BOT_TOKEN`

---

## Étape 2 — Obtenir votre ADMIN_CHAT_ID

1. Cherchez **@userinfobot** sur Telegram
2. Envoyez `/start`
3. Il vous répond avec votre **ID** (ex : `123456789`)
4. C'est votre `ADMIN_CHAT_ID`

---

## Étape 3 — Configurer Google Sheets

### 3a. Créer un Google Sheet

1. Allez sur [sheets.google.com](https://sheets.google.com) et créez un nouveau tableur
2. Nommez-le **Commandes High's Cream CBD**
3. Copiez l'**ID** dans l'URL :
   `https://docs.google.com/spreadsheets/d/`**`VOTRE_ID`**`/edit`
4. C'est votre `GOOGLE_SHEETS_ID`

### 3b. Créer un compte de service Google

1. Allez sur [console.cloud.google.com](https://console.cloud.google.com)
2. Créez un projet (ou utilisez un existant)
3. Activez l'API **Google Sheets** et **Google Drive**
4. Dans "Identifiants" → "Créer des identifiants" → "Compte de service"
5. Nommez-le `highs-cream-bot`
6. Téléchargez le fichier JSON des clés
7. Ouvrez ce fichier JSON et copiez **tout le contenu** — c'est votre `GOOGLE_CREDENTIALS_JSON`

### 3c. Partager le Google Sheet avec le compte de service

1. Ouvrez votre Google Sheet
2. Cliquez "Partager"
3. Ajoutez l'adresse email du compte de service (format : `xxx@yyy.iam.gserviceaccount.com`)
4. Donnez-lui l'accès **Éditeur**

---

## Étape 4 — Déployer sur Railway

1. Créez un compte sur [railway.app](https://railway.app) (gratuit)
2. Cliquez "New Project" → "Deploy from GitHub"
3. Importez votre dépôt GitHub contenant les fichiers du bot
4. Dans l'onglet "Variables", ajoutez :

| Variable | Valeur |
|---|---|
| `BOT_TOKEN` | Le token de @BotFather |
| `ADMIN_CHAT_ID` | Votre ID Telegram |
| `GOOGLE_SHEETS_ID` | L'ID du Google Sheet |
| `GOOGLE_CREDENTIALS_JSON` | Le JSON complet du compte de service (une ligne) |

5. Dans l'onglet "Settings" → "Start Command", entrez : `python main.py`
6. Cliquez "Deploy"

> **Alternative : Render.com**
> Même procédure, choisissez "Background Worker" comme type de service.

---

## Étape 5 — Tester le bot

1. Cherchez votre bot sur Telegram (ex. `@HighsCreamCBD_bot`)
2. Envoyez `/start`
3. Naviguez dans le catalogue, ajoutez des produits, passez une commande test
4. Vérifiez que vous recevez bien la notification admin
5. Vérifiez que la commande apparaît dans votre Google Sheet

---

## Structure des fichiers

```
Bot telegram CBD/
├── main.py               ← Point d'entrée, lancez ce fichier
├── requirements.txt      ← Dépendances Python
├── Procfile              ← Configuration Railway/Heroku
├── runtime.txt           ← Version Python
├── .env.example          ← Modèle de variables d'environnement
├── SETUP.md              ← Ce guide
├── tasks/
│   ├── todo.md
│   └── lessons.md
└── src/
    ├── config.py         ← Constantes et config
    ├── products.py       ← Catalogue produits (à éditer pour modifier les prix)
    ├── geo.py            ← Géocodage et distance
    ├── sheets.py         ← Google Sheets
    └── handlers.py       ← Toute la logique du bot
```

---

## Modifier le catalogue produits

Ouvrez `src/products.py` et modifiez le dictionnaire `PRODUCTS`.

Chaque produit a la structure suivante :
```python
"identifiant_unique": {
    "cat": "nom_categorie",        # fleur_cbd, resine_cbd, vape_cbd, mol_fleur, mol_resine, mol_vape, edibles
    "name": "Nom du produit",
    "description": "Description",
    "variants": {"2g": 9, "5g": 18, "10g": 32},   # format: {"label": prix_en_euros}
    "emoji": "🌿",
},
```

---

## Commandes du bot

| Commande | Description |
|---|---|
| `/start` | Affiche le menu principal |
| `/menu` | Même que /start |
| `/annuler` | Annule la commande en cours |
| `/commandes` | (Admin uniquement) Rappel du lien Google Sheets |

---

## Zone de livraison

La zone est définie par `MAX_DISTANCE_KM = 10` dans `src/config.py`.
Les coordonnées de Chartres sont `CHARTRES_LAT = 48.4469`, `CHARTRES_LON = 1.4876`.

Pour modifier la zone ou le centre, éditez ces valeurs dans `src/config.py`.

---

## Support

En cas de problème, vérifiez :
1. Les logs Railway/Render (onglet "Logs")
2. Que toutes les variables d'environnement sont bien renseignées
3. Que le compte de service a bien accès au Google Sheet
