import nltk
import numpy as np
import random
import json
import pickle
import re
import wikipedia
import sqlite3
import pandas as pd    
import csv
from keras.models import load_model
from nltk.stem import WordNetLemmatizer
from utils import get_weather, eval_expression, extract_number, extract_city, search_wikipedia
from utils import summarize_with_local_model
import webbrowser

nltk.download('punkt', quiet=True)
lemmatizer = WordNetLemmatizer()

model = load_model('chatbot_simplelearnmodel.h5')
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))

with open("intents.json") as file:
    intents_data = json.load(file)

city_corrections = {
    "dehi": "delhi", "dehli": "delhi", "mumabi": "mumbai", "chenai": "chennai", "punw": "pune"
}

last_prompted = {"type": None}
uploaded_file_text = ""
uploaded_csv_df = None

# === File Upload Setters ===

def set_uploaded_text(text):
    global uploaded_file_text
    uploaded_file_text = text

def set_uploaded_csv(file_path):
    global uploaded_csv_df
    try:
        uploaded_csv_df = pd.read_csv(file_path, encoding='utf-8')
        print("✅ CSV loaded with columns:", uploaded_csv_df.columns.tolist())
    except Exception as e:
        uploaded_csv_df = None
        print(f"❌ Error loading CSV: {e}")


# === CSV Search Handler ===

def search_uploaded_csv(query):
    global uploaded_csv_df
    if uploaded_csv_df is None or uploaded_csv_df.empty:
        return "📂 No CSV file uploaded yet."

    query = query.lower()

    condition_keywords = {
        "diabetes": "MedicalCondition",
        "hypertension": "MedicalCondition",
        "asthma": "MedicalCondition",
        "no medical condition": "MedicalCondition",
        "age": "Age",
        "gender": "Gender",
    }

    # Search exact conditions
    for keyword, column in condition_keywords.items():
        if keyword in query and column in uploaded_csv_df.columns:
            matches = uploaded_csv_df[uploaded_csv_df[column].astype(str).str.lower().str.contains(keyword)]
            if not matches.empty:
                return "🔎 Top Results:\n" + matches.head(3).to_string(index=False)

    # Fallback: fuzzy search all text
    try:
        matches = uploaded_csv_df.applymap(str).apply(
            lambda row: query in ' '.join(row).lower(), axis=1
        )
        results = uploaded_csv_df[matches]
        if not results.empty:
            return "🔎 Top Results:\n" + results.head(3).to_string(index=False)
        else:
            return "🔍 Sorry, I couldn't find anything relevant in the uploaded CSV."
    except Exception as e:
        return f"❌ Error searching CSV: {e}"

# === DB Search Handler ===

def fetch_healthcare_response(user_input):
    user_input = user_input.lower().strip()
    if "calculate" in user_input:
        return "🧮 Please enter a math expression like '2 + 2'."
    elif "weather" in user_input:
        return "🌦 Please enter your city name for weather details."
    elif "summarize" in user_input:
        return "📄 Please upload a file and type 'summarize file' again."
    elif "tell me about" in user_input:
        return "📚 Please enter a specific topic to search."

    try:
        conn = sqlite3.connect("healthcare.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT answer FROM healthcare
            WHERE LOWER(question) LIKE ?
            LIMIT 1
        """, ('%' + user_input + '%',))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]
        else:
            return "Sorry, I don't have an answer for that question."
    except Exception as e:
        return f"❌ Database error: {e}"

# === NLP Model Handlers ===

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    return [lemmatizer.lemmatize(word.lower()) for word in sentence_words]

def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, word in enumerate(words):
            if word == s:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]), verbose=0)[0]
    results = [{"intent": classes[i], "probability": float(prob)} for i, prob in enumerate(res) if prob > 0.75]
    results.sort(key=lambda x: x["probability"], reverse=True)
    return results

# === Main Response Generator ===



def open_website(query):
    import webbrowser

    query_lower = query.lower().strip()
    url = ""

    # Remove extra words like "dot com"
    query_lower = query_lower.replace(" dot com", "").replace(".com", "").strip()

    # Known websites mapping
    known_sites = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "wikipedia": "https://www.wikipedia.org",
        "amazon": "https://www.amazon.com",
        "facebook": "https://www.facebook.com",
        "twitter": "https://x.com",
        "github": "https://github.com",
        "stackoverflow": "https://stackoverflow.com"
    }

    for keyword, site_url in known_sites.items():
        if keyword in query_lower:
            url = site_url
            break


    if not url:
        if "." not in query_lower:
            query_lower = query_lower.replace(" ", "")
            url = f"https://www.{query_lower}.com"
        else:
            url = f"https://{query_lower}"

    try:
        webbrowser.open_new_tab(url)
        return f"🌐 Opening **{query}** in your browser.\nURL: {url}"
    except Exception as e:
        return f"❌ Couldn't open the site. Error: {e}"



def generate_response(message):
    global last_prompted, uploaded_file_text
    message = message.lower().strip()

    
    if any(x in message for x in ["hi", "hello", "hey"]):
        for intent_data in intents_data['intents']:
            if intent_data['tag'] == "greeting":
                return random.choice(intent_data['responses'])

    
    if "summarize file" in message or "summarize document" in message:
        if uploaded_file_text and uploaded_file_text.strip():
            return summarize_with_local_model(uploaded_file_text)
        else:
            return "📂 Please upload a file first to summarize."

    
    if last_prompted["type"] == "weather":
        last_prompted["type"] = None
        city = extract_city(message)
        city = city_corrections.get(city, city)
        return get_weather(city)

    if last_prompted["type"] == "calculate":
        last_prompted["type"] = None
        result = eval_expression(message)
        return f"The result is {result}" if result is not None else "Sorry, I couldn't understand the calculation."

    if last_prompted["type"] == "wikipedia":
        last_prompted["type"] = None
        return search_wikipedia(message)

    
    if message == "get weather":
        last_prompted["type"] = "weather"
        return "Which city's weather do you want to know?"

    elif message == "do a calculation":
        last_prompted["type"] = "calculate"
        return "What would you like me to calculate?"

    elif message == "tell me about":
        last_prompted["type"] = "wikipedia"
        return "What topic should I search on Wikipedia?"

    
    if "weather" in message:
        city = extract_city(message)
        city = city_corrections.get(city, city)
        return get_weather(city)

    elif any(op in message for op in ["+", "-", "*", "/", "^"]):
        result = eval_expression(message)
        return f"The result is {result}" if result is not None else "Sorry, I couldn't understand the calculation."

    elif any(x in message for x in ["who is", "what is", "tell me about"]):
        return search_wikipedia(message)

    
    if any(keyword in message for keyword in ["open", "launch", "go to", "visit", "take me to"]):
        for trigger in ["open", "launch", "go to", "visit", "take me to"]:
            if message.startswith(trigger):
                site_query = message.replace(trigger, "").strip()
                if site_query:
                    return open_website(site_query)


    
    csv_result = search_uploaded_csv(message)
    if "📂 No CSV file" not in csv_result and "couldn't find" not in csv_result:
        return csv_result

    db_answer = fetch_healthcare_response(message)
    if db_answer and "don't have an answer" not in db_answer:
        return db_answer

    predictions = predict_class(message)
    if predictions:
        top_intent = predictions[0]["intent"]
        for intent_data in intents_data['intents']:
            if intent_data['tag'] == top_intent:
                if top_intent == "website_open":
                    
                    site_name = message.replace("open", "").replace("go to", "").replace("launch", "").strip()
                    response = open_website(site_name)
                    bot_text = random.choice(intent_data['responses']).replace("{{site_name}}", site_name)
                    return f"{bot_text}\n{response}"
                return random.choice(intent_data['responses'])



    for intent_data in intents_data['intents']:
        if intent_data['tag'] == "fallback":
            return random.choice(intent_data['responses'])

    return "Sorry, I didn't understand that."