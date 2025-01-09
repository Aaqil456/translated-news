# -*- coding: utf-8 -*-
"""CryptoNews_Translator"""

# Import required libraries
import requests
import json
from datetime import datetime

# Function to fetch news from CryptoPanic
def fetch_news(api_key):
    url = f"https://cryptopanic.com/api/v1/posts/?auth_token={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        news_data = response.json()
        # Extract relevant headlines and construct "click" URLs
        news_list = []
        for news in news_data.get("results", []):
            # Construct the "click" URL
            click_url = f"https://cryptopanic.com/news/click/{news['id']}/"
            news_list.append({"title": news["title"], "url": click_url})
        return news_list
    else:
        print(f"Failed to fetch news: {response.status_code}")
        return []

# Function to translate text using Easy Peasy API
def translate_text_easypeasy(api_key, text, target_lang="ms"):
    """
    Translate text using Easy Peasy API.
    """
    url = "https://api.easypeasy.ai/translate"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "target_lang": target_lang
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get("translated_text", "Translation failed")
    else:
        print(f"Translation API error: {response.status_code}, {response.text}")
        return "Translation failed"

# Function to save translated news to JSON
def save_to_json(data, filename="translated_news.json"):
    """
    Save the translated news to a JSON file.
    """
    # Add a timestamp for uniqueness
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output = {"timestamp": timestamp, "news": data}

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    print(f"Translated news saved to {filename}")

# Main script
def main():
    # Set your CryptoPanic API Key
    CRYPTOPANIC_API_KEY = "b07d7003878406ba6c40ccd64b044855e2e96c8b"

    # Set your Easy Peasy API Key
    EASY_PEASY_API_KEY = "a4cc18de-8311-429d-9948-ed0045cf7b45"

    # Step 1: Fetch news
    print("Fetching news from CryptoPanic...")
    news_list = fetch_news(CRYPTOPANIC_API_KEY)

    if not news_list:
        print("No news fetched. Exiting.")
        return

    # Step 2: Translate news titles and prepare the final list
    print("Translating news titles...")
    translated_news = []
    for news in news_list:
        malay_title = translate_text_easypeasy(EASY_PEASY_API_KEY, news["title"])
        translated_news.append({"title": malay_title, "url": news["url"]})

    # Step 3: Save translated news to JSON
    save_to_json(translated_news)

    # Step 4: Print translated news (Optional for debugging/logging)
    print("\nTranslated News:")
    for news in translated_news:
        print(f"Title: {news['title']}\nURL: {news['url']}\n")

# Run the main script
if __name__ == "__main__":
    main()
