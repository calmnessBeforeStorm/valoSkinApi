from flask import Flask, jsonify, render_template, request
import os
import json
import threading
from time import sleep
from ValoSkin import ValoSkin

app = Flask(__name__, static_folder='static', template_folder='templates')

# Инициализация
DATA_DIR = "valohub_weapons/json"
valo = ValoSkin()
is_updating = False

def load_weapon_data(weapon: str) -> dict:
    """Загружает данные оружия из JSON-файла"""
    file_path = os.path.join(DATA_DIR, f"{weapon}.json")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"error": "Weapon not found"}, 404

def update_data():
    """Функция для обновления данных в фоновом режиме"""
    global is_updating
    is_updating = True
    try:
        valo.download_all_skins()
        valo.parse_and_save_all()
    finally:
        is_updating = False

@app.route('/weapons', methods=['GET'])
def get_all_weapons():
    """Возвращает список всех доступных оружий"""
    weapons = []
    for file in os.listdir(DATA_DIR):
        if file.endswith('.json'):
            weapons.append(file.replace('.json', ''))
    return jsonify({"weapons": weapons})

@app.route('/weapons/<weapon>', methods=['GET'])
def get_weapon(weapon):
    """Возвращает данные по конкретному оружию"""
    data = load_weapon_data(weapon)
    return jsonify(data)

@app.route('/update', methods=['GET'])
def update():
    """Запускает процесс обновления данных"""
    global is_updating
    
    if is_updating:
        return jsonify({"status": "already updating", "message": "Обновление данных уже выполняется"})
    
    # Запускаем обновление в отдельном потоке
    thread = threading.Thread(target=update_data)
    thread.start()
    
    return jsonify({
        "status": "started",
        "message": "Начато обновление данных. Пожалуйста, подождите..."
    })

@app.route('/update/status', methods=['GET'])
def update_status():
    """Показывает статус обновления"""
    if is_updating:
        return jsonify({
            "status": "updating",
            "message": "Загрузка данных..."
        })
    else:
        return jsonify({
            "status": "ready",
            "message": "Загрузка данных закончилась и данные обновились"
        })

@app.route('/')
def index():
    """Главная страница с документацией API"""
    # Получаем список всех доступных оружий
    weapons = []
    json_dir = os.path.join('valohub_weapons', 'json')
    if os.path.exists(json_dir):
        weapons = [f.replace('.json', '') for f in os.listdir(json_dir) if f.endswith('.json')]
    
    return render_template('index.html', weapons=weapons)

if __name__ == '__main__':
    # Проверяем, есть ли данные при запуске
    if not os.listdir(DATA_DIR):
        print("Первоначальная загрузка данных...")
        update_data()
    
    #app.run(debug=True) #для теста и т.п.
    app.run(host='0.0.0.0', port=80) #для прода
