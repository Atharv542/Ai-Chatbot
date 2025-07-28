import requests
import re
import wikipedia
from transformers import pipeline

# Load once (you can move this to global scope to avoid repeated loading)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


import requests

API_KEY = "8f72c5c0031647e19e261127250107"

def get_weather(city):
    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}"
        response = requests.get(url)
        data = response.json()

        if "error" in data:
            return f"❌ Couldn't find weather for '{city.title()}'. Please check the city name."

        location = data['location']['name']
        region = data['location']['region']
        country = data['location']['country']
        condition = data['current']['condition']['text']
        temp_c = data['current']['temp_c']
        feels_like = data['current']['feelslike_c']
        humidity = data['current']['humidity']
        wind_kph = data['current']['wind_kph']

        return (
            f"🌤 Weather in {location}, {region}, {country}:\n"
            f"Condition: {condition}\n"
            f"Temperature: {temp_c}°C\n"
            f"Feels Like: {feels_like}°C\n"
            f"Humidity: {humidity}%\n"
            f"Wind Speed: {wind_kph} km/h"
        )

    except Exception as e:
        return f"⚠️ Sorry, I couldn't fetch the weather data due to: {str(e)}"


def extract_city(message):
    match = re.search(r'(?:in|of)\s+([a-zA-Z\s]+)', message.lower())
    if match:
        return match.group(1).strip()
    return message.strip().split()[-1]

def extract_city(message):
    match = re.search(r'(?:in|of)\s+([a-zA-Z\s]+)', message.lower())
    if match:
        return match.group(1).strip()
    return message.strip().split()[-1]

def eval_expression(message):
    try:
        expression = re.findall(r'[\d\.\+\-\*/\(\)\^ ]+', message)[0]
        result = eval(expression.replace('^', '**'))
        return round(result, 2)
    except:
        return None

def extract_number(message):
    match = re.search(r'\d+', message)
    return int(match.group()) if match else None

def search_wikipedia(message):
    try:
        query = message.replace("tell me about", "").replace("who is", "").replace("what is", "").strip()
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except:
        return "Sorry, I couldn't find information on that topic."


def summarize_with_local_model(text):
    if len(text.strip()) < 50:
        return "Text is too short to summarize."
    try:
        summary = summarizer(text[:1024], max_length=130, min_length=30, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        return f"Error generating summary: {str(e)}"



    




