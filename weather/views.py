from django.shortcuts import render
import requests

def get_city_coordinates(city_name):
    """
    دریافت مختصات یک شهر با Open-Meteo Geocoding
    """
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1"
    try:
        response = requests.get(geo_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if not data.get("results"):
            return None, None, None
        city_info = data["results"][0]
        return city_info["latitude"], city_info["longitude"], city_info["name"]
    except:
        return None, None, None

def home(request):
    city = request.GET.get("city", "").strip()
    
    if not city:
        return render(request, "weather/home.html", {"error": "لطفاً نام شهر را وارد کنید."})
    
    lat, lon, display_name = get_city_coordinates(city)

    if lat is None or lon is None:
        return render(request, "weather/home.html", {"error": "متاسفانه شهر پیدا نشد."})

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        current = data.get("current_weather")
        if not current:
            return render(request, "weather/home.html", {"error": "متاسفانه اطلاعات هواشناسی پیدا نشد."})

        weather_data = {
            "city": display_name,
            "temperature": current.get("temperature", "N/A"),
            "windspeed": current.get("windspeed", "N/A"),
            "winddirection": current.get("winddirection", "N/A"),
            "weathercode": current.get("weathercode", "N/A"),
        }
        return render(request, "weather/home.html", {"weather": weather_data})

    except:
        return render(request, "weather/home.html", {"error": "متاسفانه دریافت اطلاعات هواشناسی با مشکل مواجه شد."})
