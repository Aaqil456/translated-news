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

# Function to translate text using Easy Peasy API
def translate_text_easypeasy(api_key, text):
    if not text:
        return ""
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

# Function to load existing data
def load_existing_data(filename="translated_news.json"):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f).get("news", [])
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

# Function to save news to JSON
def save_to_json(data, filename="translated_news.json"):
    output = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "news": data}
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

    # Fetch new news
    print("Fetching news from CryptoPanic...")
    new_news = fetch_news(CRYPTOPANIC_API_KEY)

    if not new_news:
        print("No new news fetched.")
        return

    # Translate news titles and descriptions
    print("Translating news titles and descriptions...")
    translated_news = []
    for news in new_news:
        malay_title = translate_text_easypeasy(EASY_PEASY_API_KEY, news["title"])
        malay_description = translate_text_easypeasy(EASY_PEASY_API_KEY, news["description"])
        news["title"] = malay_title
        news["description"] = malay_description
        translated_news.append(news)

    # Load existing data
    existing_news = load_existing_data()

    # Identify and print only new news
    existing_urls = {news["url"] for news in existing_news}
    newly_added_news = [news for news in translated_news if news["url"] not in existing_urls]

    print("\nNewly Added News:")
    for news in newly_added_news:
        print(f"Title: {news['title']}\nDescription: {news['description']}\nURL: {news['url']}\nImage: {news['image']}\nPanic Score: {news['panic_score']}\nTimestamp: {news['timestamp']}\n")

    # Merge and deduplicate data
    combined_news = newly_added_news + existing_news  # Add new news at the top
    combined_news = remove_duplicates(combined_news)  # Remove duplicates

    # Save combined news to JSON
    save_to_json(combined_news)

    print(f"Total news items: {len(combined_news)}")

# Run the main script
if __name__ == "__main__":
    main()
