import requests
from geopy.distance import geodesic
apishka = "917a5354-e971-4034-b36f-8050917f1059"
BASE_BASKET_PRICE = 1000
user_lon=55.589012
user_lat=37.650409
user_coords_for_math = (user_lat, user_lon)
search_query = "продуктовый магазин"
url = "https://search-maps.yandex.ru/v1/"
params = {
    "apikey": apishka,
    "text": search_query,
    "lang": "ru_RU",
    "ll": f"{user_lon},{user_lat}", # Центр поиска (координаты пользователя)
    "spn": "0.02,0.02", # Радиус поиска (примерно 1 км)
    "rspn": 1, # Искать строго внутри этого радиуса
    "results": 5, # Сколько результатов вернуть (нам нужен 1 самый близкий)
    "type": "biz" # Ищем организации (бизнес)
}
response = requests.get(url, params=params)
print('Насколько вам лень идти от  1 до 5(чем меньше число, тем сильнее вам лень:)')
n=int(input())
if response.status_code == 200:
     data = response.json()
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

if response.status_code == 200:
    data = response.json() # Превращаем ответ Яндекса в удобный словарь Python
    found_stores = []
    for item in data.get("features", []):
        # Получаем оригинальное название из Яндекса (например "Магазин Пятерочка")
        original_name = item["properties"]["CompanyMetaData"]["name"]
        
        # Переводим название в нижний регистр для удобного поиска ("магазин пятерочка")
        lower_name = original_name.lower()
        
        # Ищем бренд. По умолчанию ставим обычную цену (множитель 1.0)
        current_multiplier = 1.0 
        
        # Проверяем, есть ли бренд из нашего словаря в названии, которое вернул Яндекс
        for brand, multiplier in price_multipliers.items():
            if brand in lower_name:
                current_multiplier = multiplier
                break # Бренд найден, останавливаем поиск
                
        # Вычисляем примерную стоимость корзины для этого конкретного магазина
        estimated_price = BASE_BASKET_PRICE * current_multiplier
    for item in data.get("features", []):
        name = item["properties"]["CompanyMetaData"]["name"]
        store_lon = item["geometry"]["coordinates"][0]
        store_lat = item["geometry"]["coordinates"][1]
        store_coords_for_math = (store_lat, store_lon)
        distance_meters = geodesic(user_coords_for_math, store_coords_for_math).meter
    found_stores.append({
        "name": name,
        "distance": distance_meters,
        "estimated_price": estimated_price
        })
    if len(data["features"]) > 0:
        max_distance = max(store["distance"] for store in found_stores)
        
        print(f"--- Найдено магазинов: {len(found_stores)} ---")
        print(f"Самый дальний из них находится в {int(max_distance)} метрах.\n")
        for store in found_stores:
            dist = store["distance"]
            score = (((dist * n) / max_distance)+ ())    
    else:
        print("Рядом ничего не найдено.")
else:
    print(f"Ошибка при обращении к API. Код: {response.status_code}")
    print(f"Ответ Яндекса: {response.text}")
# print('Насколько вы богатый от 1 до 5:')
# m=int(input())

# C=[c1,c2,c3,c4,c5]=input().split()# тут тоже ток ради примера 
# numbers1 = [int(i) for i in C]
# C_max=max(numbers1)

# print('Насколько вы богатый от 1 до 5:')
# m=int(input())
# I1 = (numbers[0] * n / P_max) + (numbers1[0] * m / C_max)
# I2 = (numbers[1] * n / P_max) + (numbers1[1] * m / C_max)
# I3 = (numbers[2] * n / P_max) + (numbers1[2] * m / C_max)
# I4 = (numbers[3] * n / P_max) + (numbers1[3] * m / C_max)
# I5 = (numbers[4] * n / P_max) + (numbers1[4] * m / C_max)
# I_max=max(I1,I2,I3,I4,I5)#потом типа учитывая лучший варик мы пишем пользователю название растояние и цену чека 
# print(I_max,f'Лучший вариант:"название магазина"\n"адресс:"\n"цена чека:')
# где:
#    P (Distance)     - расстояние
#    C (Price)        - средний чек
#    n (Mobility)     - весовой коэффициент подвижности
#    m (Solvency)     - весовой коэффициент платежеспособности

