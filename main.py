import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

STOCK_API_KEY = os.getenv("STOCK_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# --- STEP 1: Fetch Stock Data ---
stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": STOCK_API_KEY,
}

response = requests.get(STOCK_ENDPOINT, params=stock_params)
data = response.json()

# Safely check if API returned time series data (handles rate limit / key errors)
if "Time Series (Daily)" not in data:
    print("API Error or Rate Limit Reached!")
    print(data)
else:
    time_series = data["Time Series (Daily)"]
    data_list = [value for (key, value) in time_series.items()]
    
    yesterday_closing_price = float(data_list[0]["4. close"])
    day_before_yesterday_closing_price = float(data_list[1]["4. close"])

    # Calculate price difference and direction
    difference = yesterday_closing_price - day_before_yesterday_closing_price
    up_down = "🔺" if difference > 0 else "🔻"
    
    # Calculate percentage change based on the original starting price
    diff_percent = round((difference / day_before_yesterday_closing_price) * 100)

    print(f"Yesterday Close: ${yesterday_closing_price}")
    print(f"Day Before Yesterday Close: ${day_before_yesterday_closing_price}")
    print(f"Movement: {up_down} {abs(diff_percent)}%\n")

    # --- STEP 2 & 3: Fetch News & Print Unique Results ---
    if abs(diff_percent) > 1:
        news_params = {
            "apiKey": NEWS_API_KEY,
            "qInTitle": COMPANY_NAME,
            "language": "en",
        }

        news_response = requests.get(NEWS_ENDPOINT, params=news_params)
        all_articles = news_response.json().get("articles", [])

        # Deduplicate articles to prevent duplicate news prints
        seen_titles = set()
        unique_articles = []
        for article in all_articles:
            if article["title"] not in seen_titles:
                seen_titles.add(article["title"])
                unique_articles.append(article)

        # Take the top 3 unique articles
        three_articles = unique_articles[:3]

        formatted_articles = [
            f"{STOCK_NAME}: {up_down}{abs(diff_percent)}%\nHeadline: {article['title']}\nBrief: {article['description']}" 
            for article in three_articles
        ]

        print("--- LATEST NEWS NOTIFICATIONS ---")
        for article in formatted_articles:
            print(article)
            print("-" * 40)