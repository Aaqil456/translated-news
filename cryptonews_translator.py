# Import required libraries
import os
import requests
import json
from datetime import datetime

# Function to fetch news from CryptoPanic with metadata and Panic Score
def fetch_news(api_key):
    url = f"https://cryptopanic.com/api/v1/posts/?auth_token={api_key}&metadata=true"
    response = requests.get(url)
    if response.status_code == 200:
        news_data = response.json()
        # Extract relevant metadata and construct "click" URLs
        news_list = []
        for news in news_data.get("results", []):
            # Construct the "click" URL
            click_url = f"https://cryptopanic.com/news/click/{news['id']}/"
            news_list.append({
                "title": news["title"],
                "url": click_url,
                "description": news.get("description", ""),
                "image": news.get("metadata", {}).get("image", ""),
                "panic_score": news.get("panic_score"),  # Fetch Panic Score if available
                "timestamp": datetime.now().isoformat()  # Add current timestamp
            })
        return news_list
    else:
        print(f"Failed to fetch news: {response.status_code}")
        return []

# Function to translate text using Easy Peasy API
def translate_text_easypeasy(api_key, text):
    """
    Translate text using Easy Peasy API.
    """
    if not text:
        return ""  # Return empty if the text is missing
    url = "https://bots.easy-peasy.ai/bot/e56f7685-30ed-4361-b6c1-8e17495b7faa/api"
    headers = {
        "content-type": "application/json",
        "x-api-key": api_key
    }
    payload = {
        "message": f"translate this text '{text}' into Malay language. Your job is just to translate this text into Malay.",
        "history": [],
        "stream": False
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        return response_data.get("bot", {}).get("text", "Translation failed")
    else:
        print(f"Translation API error: {response.status_code}, {response.text}")
        return "Translation failed"

# Function to load existing JSON data
def load_existing_data(filename="translated_news.json"):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f).get("news", [])
    return []

# Function to save translated news to JSON
def save_to_json(data, filename="translated_news.json"):
    """
    Save the translated news to a JSON file.
    """
    output = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "news": data}
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    print(f"Translated news saved to {filename}")

# Main script
def main():
    # Fetch API keys from environment variables
    CRYPTOPANIC_API_KEY = os.getenv("CRYPTOPANIC_API_KEY")
    EASY_PEASY_API_KEY = os.getenv("EASY_PEASY_API_KEY")

    # Ensure API keys are available
    if not CRYPTOPANIC_API_KEY or not EASY_PEASY_API_KEY:
        print("API keys are missing! Please set them as environment variables.")
        return

    # Step 1: Fetch news with Panic Score
    print("Fetching news from CryptoPanic...")
    news_list = fetch_news(CRYPTOPANIC_API_KEY)

    if not news_list:
        print("No news fetched. Exiting.")
        return

    # Step 2: Translate news titles and descriptions
    print("Translating news titles and descriptions...")
    translated_news = []
    for news in news_list:
        malay_title = translate_text_easypeasy(EASY_PEASY_API_KEY, news["title"])
        malay_description = translate_text_easypeasy(EASY_PEASY_API_KEY, news["description"])
        news["title"] = malay_title
        news["description"] = malay_description
        translated_news.append(news)

    # Step 3: Load existing data and merge
    existing_news = load_existing_data()
    combined_news = existing_news + translated_news  # Append new data to existing data

    # Step 4: Save combined news to JSON
    save_to_json(combined_news)

    # Step 5: Print translated news (Optional for debugging/logging)
    print("\nTranslated News:")
    for news in combined_news:
        print(f"Title: {news['title']}\nDescription: {news['description']}\nURL: {news['url']}\nImage: {news['image']}\nPanic Score: {news['panic_score']}\nTimestamp: {news['timestamp']}\n")

# Run the main script
if __name__ == "__main__":
    main()
