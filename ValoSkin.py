import requests
import os
import re
import json
from typing import List, Optional, Dict
from bs4 import BeautifulSoup

class ValoSkin:
    """
    Класс для работы со скинами из Valorant с сайта The Valo Hub.
    Возможности:
    - Скачивание HTML-страниц с информацией о скинах
    - Парсинг информации о скинах
    - Сохранение данных в JSON-файлы
    """
    
    def __init__(self, output_dir: str = "valohub_weapons"):
        self.weapons = [
            "odin", "ares", "knife", "classic", "shorty", "frenzy",
            "ghost", "sheriff", "stinger", "spectre", "bucky", "judge",
            "bulldog", "guardian", "phantom", "vandal", "marshal", "operator"
        ]
        self.output_dir = output_dir
        self.html_dir = os.path.join(output_dir, "html")
        self.json_dir = os.path.join(output_dir, "json")
        
        # Создаем необходимые директории
        os.makedirs(self.html_dir, exist_ok=True)
        os.makedirs(self.json_dir, exist_ok=True)
    
    def _download_skin_page(self, weapon: str) -> Optional[str]:
        """Скачивает HTML-страницу для конкретного оружия"""
        url = f"https://www.thevalohub.com/gun/{weapon}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            filename = os.path.join(self.html_dir, f"{weapon}.html")
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(response.text)
            
            return filename
            
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при загрузке {weapon}: {e}")
            return None
    
    def download_all_skins(self) -> List[str]:
        """Скачивает HTML-страницы для всех оружий"""
        downloaded_files = []
        
        for weapon in self.weapons:
            filename = self._download_skin_page(weapon)
            if filename:
                downloaded_files.append(filename)
                print(f"Успешно сохранено: {filename}")
            else:
                print(f"Не удалось скачать: {weapon}")
        
        print(f"\nЗавершено! Сохранено файлов: {len(downloaded_files)}/{len(self.weapons)}")
        return downloaded_files
    
    @staticmethod
    def calculate_vp_cost(vp_amount: int) -> tuple[float, list[tuple[int, float]]]:
        """
        Рассчитывает оптимальную стоимость и комбинацию пакетов VP для заданного количества.
        
        Возвращает:
        - total_cost: общая стоимость в USD (округлено до 2 знаков)
        - packs: список кортежей (vp_amount, cost) рекомендуемых пакетов
        
        :param vp_amount: Требуемое количество Valorant Points
        :return: (total_cost, purchased_packs)
        """
        # Таблица пакетов VP: (количество VP, стоимость в USD)
        # Отсортировано по убыванию для жадного алгоритма
        VP_PRICE_TABLE = [
            (11000, 99.99),
            (5350, 49.99),
            (3650, 34.99),
            (2050, 19.99),
            (1000, 9.99),
            (475, 4.99)
        ]
        
        total_cost = 0.0
        purchased_packs = []
        remaining_vp = vp_amount
        
        # Жадный алгоритм - берем самые большие пакеты сначала
        for vp, cost in VP_PRICE_TABLE:
            while remaining_vp >= vp:
                remaining_vp -= vp
                total_cost += cost
                purchased_packs.append((vp, cost))
        
        # Если остался остаток - добавляем наиболее подходящий пакет
        if remaining_vp > 0:
            # Находим минимальный пакет, покрывающий остаток
            for vp, cost in reversed(VP_PRICE_TABLE):
                if vp >= remaining_vp:
                    total_cost += cost
                    purchased_packs.append((vp, cost))
                    remaining_vp = 0
                    break
        
        # Проверяем, не выгоднее ли взять другой набор пакетов
        # (Оптимизация для случаев, когда лучше взять больше меньших пакетов)
        if len(purchased_packs) > 1:
            alternative_cost = sum(cost for vp, cost in purchased_packs[:-1])
            alternative_cost += VP_PRICE_TABLE[-1][1]
            
            if alternative_cost < total_cost:
                new_packs = purchased_packs[:-1] + [(VP_PRICE_TABLE[-1][0], VP_PRICE_TABLE[-1][1])]
                return round(alternative_cost, 2), new_packs
        
        return round(total_cost, 2), purchased_packs
    
    def parse_skin_data(self, weapon: str) -> Optional[Dict]:
        """Парсит данные о скинах, включая оптимальные пакеты VP для покупки"""
        html_file = os.path.join(self.html_dir, f"{weapon}.html")
        
        if not os.path.exists(html_file):
            print(f"HTML-файл для {weapon} не найден")
            return None
        
        try:
            with open(html_file, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            
            skins_data = []
            previous_image_url = None
            cards = soup.find_all("div", class_=lambda x: x and "MuiCard-root" in x)
            
            for card in cards:
                try:
                    # Название скина (обязательное поле)
                    name_element = card.find("span", class_=lambda x: x and "MuiCardHeader-title" in x)
                    name = name_element.text.strip() if name_element else None
                    
                    # Пропускаем карточки без названия или с "Unknown"
                    if not name or name.lower() == "unknown":
                        continue
                    
                    # Редкость (обязательное поле)
                    rarity_div = card.find("div", class_=lambda x: x and "MuiAvatar-root" in x)
                    rarity_img = rarity_div.find("img") if rarity_div else None
                    rarity = rarity_img["alt"] if rarity_img else None
                    
                    # Цена (может быть Battle Pass)
                    price_span = card.find("span", class_=lambda x: x and "MuiTypography-circular" in x)
                    price = price_span.text.strip() if price_span else None
                    
                    # Изображение (проверяем, что это новый URL)
                    image_url = None
                    image_div = card.find("div", attrs={"role": "img"})
                    if image_div and 'style' in image_div.attrs:
                        match = re.search(r'url\(["\']?(https?://[^"\')]+)', image_div['style'])
                        if match:
                            new_url = match.group(1)
                            if new_url != previous_image_url:
                                image_url = new_url
                                previous_image_url = new_url
                    
                    # Создаем запись только если есть обязательные данные
                    if name and rarity:
                        price_usd = None
                        optimal_packs = []
                        
                        if price and price.isdigit():
                            price_int = int(price)
                            price_usd, optimal_packs = self.calculate_vp_cost(price_int)
                            
                            # Форматируем пакеты для удобного отображения
                            formatted_packs = [
                                f"{vp} VP (${cost})" 
                                for vp, cost in optimal_packs
                            ]
                        
                        skins_data.append({
                            "name": name,
                            "rarity": rarity,
                            "price_vp": price if price else "Battle Pass",
                            "price_usd": price_usd,
                            "optimal_vp_packs": formatted_packs if price and price.isdigit() else [],
                            "image_url": image_url
                        })
                    
                except Exception as e:
                    print(f"Ошибка при обработке карточки {weapon}: {str(e)}")
                    continue
            
            # Дополнительная фильтрация дубликатов
            unique_skins = []
            seen_names = set()
            
            for skin in skins_data:
                if skin["name"] not in seen_names:
                    unique_skins.append(skin)
                    seen_names.add(skin["name"])
            
            return {
                "weapon": weapon,
                "skins": unique_skins
            }
            
        except Exception as e:
            print(f"Ошибка при парсинге {weapon}: {str(e)}")
            return None
    
    def save_to_json(self, weapon: str, data: Dict) -> Optional[str]:
        """Сохраняет данные о скинах в JSON-файл"""
        if not data:
            return None
            
        filename = os.path.join(self.json_dir, f"{weapon}.json")
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return filename
        except Exception as e:
            print(f"Ошибка при сохранении {filename}: {e}")
            return None
    
    def parse_and_save_all(self) -> List[str]:
        """Парсит и сохраняет данные для всех оружий"""
        saved_files = []
        
        for weapon in self.weapons:
            data = self.parse_skin_data(weapon)
            if data:
                filename = self.save_to_json(weapon, data)
                if filename:
                    saved_files.append(filename)
                    print(f"Успешно сохранено: {filename}")
        
        print(f"\nЗавершено! Сохранено JSON-файлов: {len(saved_files)}/{len(self.weapons)}")
        return saved_files