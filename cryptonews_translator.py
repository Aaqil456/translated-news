# Import required libraries
import random
import os
import requests
import json
import time
from datetime import datetime, timedelta

# Function to fetch hot news from CryptoPanic
def fetch_news(api_key, filter_type="hot"):
    url = f"https://cryptopanic.com/api/v1/posts/?auth_token={api_key}&metadata=true&filter={filter_type}"
    response = requests.get(url)
    if response.status_code == 200:
        news_data = response.json()
        news_list = []
        for news in news_data.get("results", []):
            click_url = f"https://cryptopanic.com/news/click/{news['id']}/"
            news_list.append({
                "title": news["title"],
                "url": click_url,
                "description": news.get("description", ""),
                "image": news.get("metadata", {}).get("image", ""),
                "panic_score": news.get("panic_score"),
                "timestamp": datetime.now().isoformat()
            })
        return news_list
    else:
        print(f"Failed to fetch news: {response.status_code}")
        return []

# Function to clean and truncate text
def clean_text(text):
    if not text:
        return ""
    return text.encode("ascii", errors="ignore").decode()

def truncate_text(text, max_length=500):
    return text if len(text) <= max_length else text[:max_length] + "..."

# Function to translate text using Easy Peasy API
def translate_text_easypeasy(api_key, text, retries=3, delay=2):
    if not text:
        return None

    url = "https://bots.easy-peasy.ai/bot/e56f7685-30ed-4361-b6c1-8e17495b7faa/api"
    headers = {
        "content-type": "application/json",
        "x-api-key": api_key
    }
    payload = {
        "message": f"translate this text '{text}' into Malay language. Only return the translated text and don't return anything other than the translated text.",
        "history": [],
        "stream": False
    }

    for attempt in range(1, retries + 1):
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                response_data = response.json()
                translated_text = response_data.get("bot", {}).get("text", None)
                if translated_text:
                    return translated_text
            else:
                print(f"Translation API error: {response.status_code}, {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"Request failed (attempt {attempt}/{retries}): {e}")

        if attempt < retries:
            time.sleep(delay)

    print(f"Translation failed after {retries} attempts for text: {text}")
    return None

# Function to load existing data
def load_existing_data(filename="translated_news.json"):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f).get("all_news", [])
    return []

# Function to remove duplicates
def remove_duplicates(news_list):
    seen_urls = set()
    unique_news = []
    for news in news_list:
        if news["url"] not in seen_urls:
            unique_news.append(news)
            seen_urls.add(news["url"])
    return unique_news

# Function to filter out news older than 3 days
def filter_old_news(news_list, days=3):
    cutoff_time = datetime.now() - timedelta(days=days)
    return [
        news for news in news_list
        if datetime.fromisoformat(news["timestamp"]) >= cutoff_time
    ]

# Function to save news to JSON
def save_to_json(data, filename="translated_news.json"):
    output = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "all_news": data}
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    print(f"Translated hot news saved to {filename}")

# Main function
def main():
    CRYPTOPANIC_API_KEY = os.getenv("CRYPTOPANIC_API_KEY")
    EASY_PEASY_API_KEY = os.getenv("EASY_PEASY_API_KEY")

    if not CRYPTOPANIC_API_KEY or not EASY_PEASY_API_KEY:
        print("API keys are missing! Please set them as environment variables.")
        return

    # Load and filter existing news (keep only news from the last 3 days)
    print("Loading existing news and filtering old news...")
    existing_news = load_existing_data()
    recent_news = filter_old_news(existing_news, days=3)
    print(f"{len(recent_news)} recent news retained.")

    # Fetch and translate latest hot news
    print("Fetching latest hot news from CryptoPanic...")
    hot_news = fetch_news(CRYPTOPANIC_API_KEY)

    print("Translating hot news titles and descriptions...")
    translated_hot_news = []
    for news in hot_news:
        title = clean_text(truncate_text(news["title"]))
        description = clean_text(truncate_text(news["description"]))
        translated_title = translate_text_easypeasy(EASY_PEASY_API_KEY, title)
        translated_description = translate_text_easypeasy(EASY_PEASY_API_KEY, description)
        if translated_title or translated_description:
            news["title"] = translated_title if translated_title else news["title"]
            news["description"] = translated_description if translated_description else news["description"]
            news["is_hot"] = True
            translated_hot_news.append(news)
        else:
            print(f"Translation failed for hot news: {news['title']}")

    # Combine recent news with new hot news
    combined_news = remove_duplicates(recent_news + translated_hot_news)

    # Save combined news
    if combined_news:
        save_to_json(combined_news)
        print(f"\n{len(combined_news)} total news saved.")
    else:
        print("No news to save.")

    # Print latest added hot news
    print("\nLatest Hot News Added:")
    for news in translated_hot_news:
        print(f"Title: {news['title']}\nURL: {news['url']}\nIs Hot: {news['is_hot']}\n")

# Run the main script
if __name__ == "__main__":
    main()
