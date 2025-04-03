# 🎯 Valorant Skins API

## 📌 Описание проекта
Проект представляет собой **RESTful API** для получения актуальной информации о скинах из игры *Valorant*. Данные парсятся с сайта **The Valo Hub** ([thevalohub.com](https://www.thevalohub.com)), обрабатываются и сохраняются в **JSON-формате**. 

🔹 **Возможности API:**
- 📜 Получать список всех оружий и их скинов.
- 🔍 Просматривать детализацию по каждому скину (название, редкость, стоимость в VP и USD).
- 🔄 Обновлять данные вручную через специальный эндпоинт.

---

## 🏗️ Архитектура проекта
Проект реализован по **клиент-серверной архитектуре** и включает в себя:

🔹 **Backend (Flask API):**
- Получает запросы от клиента.
- Отдает данные из локальных JSON-файлов или запускает парсинг.

🔹 **Парсер (ValoSkin):**
- Скачивает HTML-страницы с The Valo Hub.
- Извлекает данные о скинах с помощью **BeautifulSoup**.
- Сохраняет их в структурированном виде (JSON).

📊 **Схема работы:**
```
Client → Flask API → (JSON-данные / Запрос на обновление) → ValoSkin → The Valo Hub (HTML)
```

---

## 🛠️ Технологии и зависимости
- **Python 3.12.6**
- **Основные библиотеки:**
  - 🚀 `Flask` – веб-фреймворк для API.
  - 🔗 `requests` – HTTP-запросы к The Valo Hub.
  - 📜 `BeautifulSoup4` – парсинг HTML.
- **Дополнительно:**
  - 🔄 `threading` – для фонового обновления данных.
  - 📂 `json` – работа с JSON-файлами.
  - 📁 `os` – управление файловой системой.

---

## 📂 Структура проекта
```
ValoSkin/
├── main.py                    # Основное Flask-приложение
├── ValoSkin.py               # Класс для парсинга и сохранения данных
├── templates/                # HTML-шаблоны
│   └── index.html            # Документация API
├── static/                   # Статические файлы (CSS, JS)
│   └── style.css             # Стили для документации
└── valohub_weapons/          # Локальная "база данных"
    ├── html/                 # Скачанные HTML-страницы
    └── json/                 # Обработанные данные в JSON
```

---

## 🚀 Основные функции
| Функция | Описание |
|---------|----------|
| `ValoSkin.download_all_skins()` | 📥 Скачивает HTML для всех оружий. |
| `ValoSkin.parse_and_save_all()` | 📊 Парсит данные и сохраняет в JSON. |
| `@app.route('/weapons')` | 🔫 Возвращает список оружий. |
| `@app.route('/update')` | 🔄 Запускает обновление данных. |

---

## 📡 Примеры запросов к API
### 🔫 1. Получить список оружий
```bash
GET /weapons
```
📥 **Ответ:**
```json
{"weapons": ["vandal", "phantom", "operator", ...]}
```

### 🎨 2. Получить скины для Vandal
```bash
GET /weapons/vandal
```
📥 **Ответ:**
```json
{
  "weapon": "vandal",
  "skins": [
    {
      "image_url": null,
      "name": "Immortalized Vandal",
      "optimal_vp_packs": [],
      "price_usd": null,
      "price_vp": "Battle Pass",
      "rarity": "Select Edition"
    },
    {
      "image_url": "https://cdn.thevalohub.com/skin_image/4e435234-49a2-1444-4640-908692c855b8.webp",
      "name": "RGX 11z Pro Vandal",
      "optimal_vp_packs": [
        "2050 VP ($19.99)",
        "475 VP ($4.99)"
      ],
      "price_usd": 24.98,
      "price_vp": "2175",
      "rarity": "Deluxe Edition"
    },
    ...
  ]
}
```

### 🔄 3. Обновить данные
```bash
GET /update
```
📥 **Ответ:**
```json
{"status": "started", "message": "Обновление данных начато"}
```

---

## ▶️ Как запустить?
1. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Запустите сервер:**
   ```bash
   python main.py
   ```
3. **Откройте в браузере:**
   ```
   http://localhost:5000
   ```

---