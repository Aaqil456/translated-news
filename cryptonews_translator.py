# Import required libraries
import random  # Import random module for shuffling
import os
import requests
import json
import time
from datetime import datetime

# Function to fetch news from CryptoPanic with metadata and optional filters
def fetch_news(api_key, filter_type=None):
    url = f"https://cryptopanic.com/api/v1/posts/?auth_token={api_key}&metadata=true"
    if filter_type:
        url += f"&filter={filter_type}"
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

# Function to translate text using Easy Peasy API with proper response handling
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
            print(f"Request Payload: {json.dumps(payload, indent=2)}")
            print(f"Response Status: {response.status_code}")
            print(f"Response Body: {response.text}")

            if response.status_code == 200:
                response_data = response.json()
                translated_text = response_data.get("bot", {}).get("text", None)
                if translated_text:  # Ensure the translation exists
                    return translated_text
                else:
                    print("Translation text is missing in the API response.")
            else:
                print(f"Translation API error: {response.status_code}, {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"Request failed (attempt {attempt}/{retries}): {e}")

        # Wait before retrying
        if attempt < retries:
            time.sleep(delay)

    print(f"Translation failed after {retries} attempts for text: {text}")
    return None

# Function to load existing data
def load_existing_data(filename="translated_news.json"):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"all_news": []}

# Function to remove duplicates
def remove_duplicates(news_list):
    seen_urls = set()
    unique_news = []
    for news in news_list:
        if news["url"] not in seen_urls:
            unique_news.append(news)
            seen_urls.add(news["url"])
    return unique_news

# Function to save news to JSON
def save_to_json(data, filename="translated_news.json"):
    output = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "all_news": data}
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    print(f"Translated news saved to {filename}")

# Main function
def main():
    CRYPTOPANIC_API_KEY = os.getenv("CRYPTOPANIC_API_KEY")
    EASY_PEASY_API_KEY = os.getenv("EASY_PEASY_API_KEY")

    if not CRYPTOPANIC_API_KEY or not EASY_PEASY_API_KEY:
        print("API keys are missing! Please set them as environment variables.")
        return

    # Fetch all news and hot news
    print("Fetching all news from CryptoPanic...")
    all_news = fetch_news(CRYPTOPANIC_API_KEY)

    print("Fetching hot news from CryptoPanic...")
    hot_news = fetch_news(CRYPTOPANIC_API_KEY, filter_type="hot")

    # Translate all news
    print("Translating all news titles and descriptions...")
    translated_all_news = []
    for news in all_news:
        title = clean_text(truncate_text(news["title"]))
        description = clean_text(truncate_text(news["description"]))
        translated_title = translate_text_easypeasy(EASY_PEASY_API_KEY, title)
        translated_description = translate_text_easypeasy(EASY_PEASY_API_KEY, description)
        if translated_title or translated_description:
            news["title"] = translated_title if translated_title else news["title"]
            news["description"] = translated_description if translated_description else news["description"]
            news["is_hot"] = False  # Default value
            translated_all_news.append(news)
        else:
            print(f"Translation failed for news: {news['title']}")

    # Translate hot news and mark them
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

    # Combine all news and hot news, ensuring hot news is part of all news
    combined_news = translated_hot_news + translated_all_news  # Hot news first
    combined_news = remove_duplicates(combined_news)

    # Load existing data and merge
    existing_data = load_existing_data()
    final_news_list = remove_duplicates(combined_news + existing_data.get("all_news", []))

    # Save combined data to JSON
    if final_news_list:
        save_to_json(final_news_list)

    # Print newly added news
    print("\nNewly Added News:")
    new_news = [news for news in final_news_list if news not in existing_data.get("all_news", [])]
    if new_news:
        for news in new_news:
            print(f"Title: {news['title']}\nURL: {news['url']}\nIs Hot: {news['is_hot']}\n")
    else:
        print("No new news was added.")

# Run the main script
if __name__ == "__main__":
    main()
