import datetime as dt
import json
import requests
from flask import Flask, jsonify, request

API_TOKEN = "***"
RSA_KEY = ""
GEMINI_KEY = ""

app = Flask(__name__)

class InvalidUsage(Exception):
    status_code = 400
    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv

def get_weather_data(location: str, date: str):
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}/{date}?unitGroup=metric&key={RSA_KEY}&contentType=json"
    
    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        return response.json()
    else:
        raise InvalidUsage(response.text, status_code=response.status_code)

def get_evening_plan(temp, wind, precip, precip_prob):
    precip_desc = f"precip: {precip} mm, probability: {precip_prob}%"
    
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    headers = {"Content-Type": "application/json"}

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"Current weather: {temp}°C, wind {wind} kph, {precip_desc}. "
                                f"Suggest one creative evening activity (max 30 words). "
                                f"Don't limit yourself to specific options, suggest anything relevant to the weather."
                    }
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError):
            return "Enjoy your evening regardless of the weather!"
    elif response.status_code == 429:
        return "AI is busy (API limit reached). Please wait a minute."
    else:
        return f"AI Error {response.status_code}"

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route("/")
def home_page():
    return "<h2>HW1: Weather SaaS with AI.</h2>"

@app.route("/content/api/v1/integration/generate", methods=["POST"])
def weather_endpoint():
    json_data = request.get_json()

    if not json_data or json_data.get("token") != API_TOKEN:
        raise InvalidUsage("Invalid or missing API token", status_code=403)

    location = json_data.get("location")
    date = json_data.get("date")
    requester_name = json_data.get("requester_name")

    weather_raw = get_weather_data(location, date)
    day_data = weather_raw['days'][0]

    temp = day_data.get("temp")
    wind = day_data.get("windspeed")
    precip = day_data.get("precip", 0)
    precip_prob = day_data.get("precipprob", 0)

    ai_plan = get_evening_plan(temp, wind, precip, precip_prob)

    result = {
        "requester_name": requester_name,
        "timestamp": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "location": location,
        "date": date,
        "weather": {
            "temp_c": temp,
            "wind_kph": wind,
            "precip_mm": precip,
            "precip_prob_percent": precip_prob,
            "pressure_mb": day_data.get("pressure"),
            "humidity": day_data.get("humidity")
        },
        "ai_evening_plan": ai_plan
    }

    return jsonify(result)
