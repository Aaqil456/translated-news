import os
import requests
import json
from datetime import datetime, timedelta

# Function to fetch news from CryptoPanic with metadata, Panic Score, and a since filter
def fetch_news(api_key, since_timestamp=None):
    url = f"https://cryptopanic.com/api/v1/posts/?auth_token={api_key}&metadata=true"
    if since_timestamp:
        url += f"&since={since_timestamp}"

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

# Function to remove duplicates
def remove_duplicates(news_list):
    seen_urls = set()
    unique_news = []
    for news in news_list:
        if news["url"] not in seen_urls:
            unique_news.append(news)
            seen_urls.add(news["url"])
    return unique_news

# Function to load existing JSON data
def load_existing_data(filename="translated_news.json"):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f).get("news", [])
    return []

# Function to save translated news to JSON
def save_to_json(data, filename="translated_news.json"):
    output = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "news": data}
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    print(f"Translated news saved to {filename}")

# Main function
def main():
    CRYPTOPANIC_API_KEY = os.getenv("CRYPTOPANIC_API_KEY")

    if not CRYPTOPANIC_API_KEY:
        print("Missing CryptoPanic API key!")
        return

    # Fetch news from the last hour
    last_hour = (datetime.now() - timedelta(hours=1)).isoformat()
    print(f"Fetching news posted since: {last_hour}")
    news_list = fetch_news(CRYPTOPANIC_API_KEY, since_timestamp=last_hour)

    if not news_list:
        print("No new news fetched.")
        return

    # Load existing data and merge with new data
    existing_news = load_existing_data()
    combined_news = existing_news + news_list
    combined_news = remove_duplicates(combined_news)  # Remove duplicates

    # Save to JSON
    save_to_json(combined_news)

# Run the main script
if __name__ == "__main__":
    main()
