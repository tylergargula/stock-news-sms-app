import requests
from newsapi import NewsApiClient
from twilio.rest import Client
import os

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

# News API credentials
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
STOCK_API = os.environ["STOCK_API_KEY"]
NEWS_API_KEY = os.environ["NEWS_API_KEY"]

# Twilio API credentials
TWILIO_SID = os.environ["TWILIO_SID"]
TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH"]
TWILIO_VIRTUAL_NUMBER = os.environ["TWILIO_VIRTUAL_NUMBER"]
MY_PHONE_NUMBER = os.environ["PHONE_NUMBER"]

stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "interval": "60min",
    "apikey": STOCK_API
}

response = requests.get(STOCK_ENDPOINT, params=stock_params)
response.raise_for_status()
stock_data = response.json()
daily_data = stock_data["Time Series (Daily)"]
data_list = [value for (key, value) in daily_data.items()]
yesterday_data = float(data_list[0]['4. close'])
day_before_data = float(data_list[1]['4. close'])

difference = yesterday_data - day_before_data

up_down = None
if difference > 0:
    up_down = "🔺"
else:
    up_down = "🔻"


percent_difference = (yesterday_data - day_before_data) / day_before_data * 100
rounded_percent = abs(round(percent_difference, 3))
print(rounded_percent)

if rounded_percent > 0:
    newsapi = NewsApiClient(api_key=NEWS_API_KEY)

    top_headlines = newsapi.get_top_headlines(q='tesla',
                                              category='business',
                                              language='en',
                                              country='us'
                                              )

    headline_articles = top_headlines["articles"][:2]
    formatted_articles = [f"Headline: {article['title']}. \nBrief: {article['content']}" for article in
                          headline_articles]

    print(formatted_articles)

    for article in formatted_articles:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"{STOCK_NAME}: {up_down}{rounded_percent}%\n\n{article}",
            from_=TWILIO_VIRTUAL_NUMBER,
            to=MY_PHONE_NUMBER
        )

        print(message.sid)
