# Import required libraries
import os
import requests
import json
from datetime import datetime
from openai import OpenAI  # Use the OpenAI SDK to interact with DeepSeek API

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

# Function to translate text using DeepSeek API
def translate_text_deepseek(api_key, text):
    if not text:
        return ""
    
    # Initialize the OpenAI client with DeepSeek API configuration
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    
    try:
        # Make the API call to DeepSeek
        response = client.chat.completions.create(
            model="deepseek-chat",  # Use the DeepSeek-V3 model
            messages=[
                {"role": "system", "content": "You are a helpful translator. Translate the following text into Malay."},
                {"role": "user", "content": text},
            ],
            stream=False  # Disable streaming for simplicity
        )
        
        # Extract the translated text from the response
        translated_text = response.choices[0].message.content
        return translated_text
    except Exception as e:
        print(f"DeepSeek API error: {e}")
        return "Translation failed"

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
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

    if not CRYPTOPANIC_API_KEY or not DEEPSEEK_API_KEY:
        print("API keys are missing! Please set them as environment variables.")
        return

    # Fetch all news and hot news
    print("Fetching all news from CryptoPanic...")
    all_news = fetch_news(CRYPTOPANIC_API_KEY)

    print("Fetching hot news from CryptoPanic...")
    hot_news = fetch_news(CRYPTOPANIC_API_KEY, filter_type="hot")

    # Translate all news
    print("Translating all news titles and descriptions...")
    for news in all_news:
        news["title"] = translate_text_deepseek(DEEPSEEK_API_KEY, news["title"])
        news["description"] = translate_text_deepseek(DEEPSEEK_API_KEY, news["description"])
        news["is_hot"] = False  # Default value

    # Translate hot news and mark them
    print("Translating hot news titles and descriptions...")
    for news in hot_news:
        news["title"] = translate_text_deepseek(DEEPSEEK_API_KEY, news["title"])
        news["description"] = translate_text_deepseek(DEEPSEEK_API_KEY, news["description"])
        news["is_hot"] = True

    # Combine all news and hot news, ensuring hot news is part of all news
    combined_news = hot_news + all_news  # Hot news first
    combined_news = remove_duplicates(combined_news)

    # Load existing data and merge
    existing_data = load_existing_data()
    final_news_list = remove_duplicates(combined_news + existing_data.get("all_news", []))

    # Save combined data to JSON
    save_to_json(final_news_list)

    # Print newly added news
    print("\nNewly Added News:")
    new_news = [news for news in final_news_list if news not in existing_data.get("all_news", [])]
    for news in new_news:
        print(f"Title: {news['title']}\nURL: {news['url']}\nIs Hot: {news['is_hot']}\n")

# Run the main script
if __name__ == "__main__":
    main()
