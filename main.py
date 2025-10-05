from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# Разрешаем запросы с фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "45f91dd588554787f92896cb61747e96"

@app.get("/air_quality")
def air_quality(city: str):
    # 1. Получаем координаты города
    geo_url = f"https://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
    geo_res = requests.get(geo_url).json()
    if len(geo_res) == 0:
        return {"error": "Город не найден"}
    lat = geo_res[0]["lat"]
    lon = geo_res[0]["lon"]

    # 2. Получаем данные о загрязнении воздуха
    air_url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    air_res = requests.get(air_url).json()
    components = air_res["list"][0]["components"]
    pm25 = components["pm2_5"]
    pm10 = components["pm10"]

    # Вычисляем AQI аналогично Android
    aqiPM25 = int((pm25 / 12.0) * 50)
    aqiPM10 = int((pm10 / 50.0) * 50)
    aqi = max(aqiPM25, aqiPM10)

    # 3. Получаем температуру
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    temp_res = requests.get(weather_url).json()
    temp = temp_res.get("main", {}).get("temp", 0)

    # 4. Определяем статус
    if aqi <= 100: status = "Умеренный"
    elif aqi <= 150: status = "Вредный для чувствительных"
    elif aqi <= 200: status = "Вредный"
    else: status = "Очень вредный"

    # 5. Прогноз ухудшения AQI
    warning = ""
    if pm25 > 30 and temp > 30:
        warning = "⚠ Возможное ухудшение качества воздуха!"
    else:
        warning = "Качество воздуха нормальное"

    return {
        "city": city,
        "aqi": aqi,
        "status": status,
        "pm25": pm25,
        "pm10": pm10,
        "temperature": temp,
        "warning": warning
    }
