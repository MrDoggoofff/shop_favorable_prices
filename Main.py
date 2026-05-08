import requests
from geopy.distance import geodesic

# Координаты пользователя (например, центр Москвы)
user_lat = 55.753630 # Широта
user_lon = 37.620070 # Долгота
user_coords = (user_lat, user_lon)
radius_meters = 1500 # Ищем магазины в радиусе 1.5 км

# Наш словарь цен
BASE_BASKET_PRICE = 1000 
price_multipliers = {
    "азбука вкуса": 1.8,
    "вкусвилл": 1.4,
    "перекресток": 1.2,
    "спар": 1.2,
    "spar": 1.2,
    "пятерочка": 0.9,
    "магнит": 0.9,
    "дикси": 0.85,
    "чижик": 0.7
}
print('Насколько вам лень идти от  1 до 5(чем меньше число, тем сильнее вам лень:)')
n=int(input())
print('Насколько вы богатый от 1 до 5:')
m=int(input())
# 1. Формируем запрос к бесплатному Overpass API
# Мы просим найти "супермаркеты" (shop=supermarket) или "продуктовые" (shop=convenience)
overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = f"""
[out:json];
(
  node["shop"="supermarket"](around:{radius_meters},{user_lat},{user_lon});
  node["shop"="convenience"](around:{radius_meters},{user_lat},{user_lon});
);
out center;
"""

# Важно: Overpass просит указывать, кто делает запрос, чтобы не блокировать роботов
headers = {'User-Agent': 'MyStoreFinderApp/1.0'}

# Отправляем запрос
response = requests.post(overpass_url, data={'data': overpass_query}, headers=headers)

if response.status_code == 200:
    data = response.json()
    found_stores = []
    
    # 2. Разбираем ответ
    for element in data.get('elements', []):
        # В OSM у некоторых ларьков нет названий, проверяем это
        tags = element.get('tags', {})
        original_name = tags.get('name', 'Продуктовый магазин (без названия)')
        lower_name = original_name.lower()
        
        # Координаты из OSM
        store_lat = element['lat']
        store_lon = element['lon']
        
        # Считаем расстояние
        distance_meters = geodesic(user_coords, (store_lat, store_lon)).meters
        
        # Ищем бренд для цены
        current_multiplier = 1.0
        for brand, multiplier in price_multipliers.items():
            if brand in lower_name:
                current_multiplier = multiplier
                break
                
        estimated_price = BASE_BASKET_PRICE * current_multiplier
        
        found_stores.append({
            "name": original_name,
            "distance": distance_meters,
            "estimated_price": estimated_price
        })

    # 3. Обрабатываем результаты
    if found_stores:
        # Сортируем список по расстоянию (от самых близких к самым дальним)
        found_stores = sorted(found_stores, key=lambda x: x['distance'])
        
        # Оставляем только 5 ближайших
        top_5_stores = found_stores[:5]
        
        # Находим самый дальний магазин ИЗ ЭТИХ ПЯТИ для вашей формулы
        max_distance = top_5_stores[-1]['distance']
        max_price = top_5_stores[-1]['estimated_price']
        
        print(f"--- Найдено {len(found_stores)} магазинов, взяли 5 ближайших ---")
        print(f"Дистанция до самого дальнего из них: {int(max_distance)} м.\n")
        
        for store in top_5_stores:
            dist = store["distance"]
            price = store["estimated_price"]
            
            # ВАША ФОРМУЛА
            score = (dist *n) / max_distance + ((price*m)/max_price)
            
            
            print(f"🏪 {store['name']}")
            print(f"Расстояние: {int(dist)} м.")
            print(f"Примерная цена корзины: {int(price)} руб.")
            print(f"Результат формулы: {score:.2f}")
            print("-" * 25)
    
            
    else:
        print("В заданном радиусе магазинов не найдено.")
else:
    print(f"Ошибка. Код: {response.status_code}")


# где:
#    P (Distance)     - расстояние
#    C (Price)        - средний чек
#    n (Mobility)     - весовой коэффициент подвижности
#    m (Solvency)     - весовой коэффициент платежеспособности

