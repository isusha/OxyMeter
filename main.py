from fastapi import FastAPI
import requests, os

app = FastAPI()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

@app.get("/air_quality")
def get_air_quality(city: str):
    # Получаем координаты города
    geo = requests.get(f"https://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}").json()
    if not geo:
        return {"error": "City not found"}
    lat, lon = geo[0]["lat"], geo[0]["lon"]

    # Получаем AQI
    aqi_data = requests.get(f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}").json()
    pm25 = aqi_data["list"][0]["components"]["pm2_5"]
    pm10 = aqi_data["list"][0]["components"]["pm10"]

    # Получаем температуру
    temp_data = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric").json()
    temp = temp_data["main"]["temp"]

    # Простейшая оценка AQI
    aqi = max(int(pm25 / 12 * 50), int(pm10 / 50 * 50))
    status = "Хорошо" if aqi <= 50 else "Умеренно" if aqi <= 100 else "Вредно"

    return {"city": city, "AQI": aqi, "PM2.5": pm25, "PM10": pm10, "Temp": temp, "Status": status}
