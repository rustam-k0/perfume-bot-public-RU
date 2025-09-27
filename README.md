# Perfume Bot MVP

A Telegram bot designed to find perfumes and their popular dupes (clones), calculating the potential savings.

---

## 📂 Project Structure

```

perfume-bot/
│
├── data/
│   └── perfumes.db
│
├── web.py         \# Bot startup and Telegram handlers, including request logging.
├── database.py    \# SQLite handling and table initialization.
├── search.py      \# Core logic for flexible/fuzzy searching (brand/name, fuzzy match).
├── formatter.py   \# Assembles the formatted text response.
├── followup.py    \# Logic for the "Wanna try again?" follow-up message.
├── utils.py       \# Text normalization and Cyrillic transliteration.
├── i18n.py        \# Centralized file for all localized strings 
├── requirements.txt
├── .env
└── README.md

````

---

## 🗄️ Database Structure (SQLite)

The database consists of **three** main tables:

### 1. `UserMessages` Table

Stores the history of all user queries for analytics and error tracking.

| Column        | Data Type | Description 

| `id`          | INTEGER | Unique ID (Primary Key) 
| `user_id`     | INTEGER | Telegram user ID 
| `timestamp`   | INTEGER | UNIX timestamp of the message 
| `message`     | TEXT    | User's raw text message 
| `status`      | TEXT    | Query result status (e.g., `success`, `fail`, `start_command`) 
| `notes`       | TEXT    | Additional notes (e.g., fuzzy match warning, error details) 

### 2. `OriginalPerfume` Table

Stores information about the original, expensive perfumes.

| Column      | Data Type      | Description             |
| :---        | :---           | :---                    |
| `id`        | TEXT           | Unique ID (Primary Key) |
| `brand`     | TEXT           | Original perfume brand  |
| `name`      | TEXT           | Original perfume name   |
| `price_eur` | REAL           | Original price in Euros |
| `url`       | TEXT           | Link to the original product page |

### 3. `CopyPerfume` Table

Stores information about perfume dupes (clones) linked to an original.

| Column         | Data Type | Description |
| :---           | :--- | :--- |
| `id`           | TEXT | Unique ID (Primary Key) |
| `original_id`  | TEXT | Reference to `id` in `OriginalPerfume` (Foreign Key) |
| `brand`        | TEXT | Dupe/clone brand |
| `name`         | TEXT | Dupe/clone name |
| `price_eur`    | REAL | Dupe/clone price in Euros |
| `url`          | TEXT | Link to the dupe/clone product page |
| `notes`        | TEXT | Notes about the dupe |
| `saved_amount` | REAL | Savings percentage: `(orig_price_eur - dupe_price_eur) / orig_price_eur * 100` |

---

## 🚀 Project Setup

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Create a file named `.env` in the root directory and specify your bot token, webhook URL, and the desired language:
    ```
    BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN_HERE"
    WEBHOOK_URL="YOUR_WEBHOOK_URL"
    # Optional: Set the bot's default language (ru or en). Defaults to 'ru'.
    BOT_LANG="en" 
    ```
3.  Run the bot (typically using a web server or hosting service like Heroku/Render):
    ```bash
    python web.py
    ```
    *Note: The bot uses a Flask web server to handle Telegram webhooks.*
````