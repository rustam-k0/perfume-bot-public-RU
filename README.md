# Perfume Bot MVP

Бот для поиска парфюмов и их популярных клонов с расчетом экономии.


## 📂 Структура проекта

```

perfume-bot/
│
├── data/
│   └── perfumes.db
│
├── web.py         # только запуск и обработчики телеграма
├── database.py    # работа с SQLite 
├── search.py      # логика парсинга и поиска (бренд/название, fuzzy)
├── formatter.py   # сборка красивого текста ответа
├── followup.py    # логика "Ура! 🎉..." (отправка 1 раз)
├── utils.py       # нормализация текста, транслитерация
├── requirements.txt
├── .env
└── README.md
```

---

## 🗄️ Структура базы данных (SQLite)

База данных состоит из двух основных таблиц:

### 1. Таблица `OriginalPerfume`
Хранит информацию об оригинальных парфюмах.

| Колонка          | Тип данных | Описание      
|------------------|------------|-----------------------------
| `id`             | TEXT       | Уникальный id (Primary Key) |
| `brand`          | TEXT       | Бренд оригинала             |
| `name`           | TEXT       | Название оригинала          |
| `price_eur`      | REAL       | Цена оригинала в евро       |
| `url`            | TEXT       | Ссылка на страницу оригинала|

### 2. Таблица `CopyPerfume`
Хранит информацию о копиях парфюмов, связанных с оригиналом.

| Колонка          | Тип данных | Описание  
|------------------|------------|-----------
| `id`             | TEXT       |Уникальный id (Primary Key)
| `original_id`    | TEXT       | Ссылка на `id` из таблицы `OriginalPerfume` (Foreign Key) |
| `brand`          | TEXT       | Бренд клона                     |
| `name`           | TEXT       | Название клона                  |
| `price_eur`      | REAL       | Цена клона в евро               |
| `url`            | TEXT       | Ссылка на клон                  |
| `notes`          | TEXT       | Примечания к аромату            |
| `saved_amount`   | REAL       | Экономия в %: `(orig_price_eur - dupe_price_eur) / orig_price_eur * 100` |

BOT_TOKEN="ВАШ_ТОКЕН_ЗДЕСЬ"
python database.py

pip install -r requirements.txt
python bot.py