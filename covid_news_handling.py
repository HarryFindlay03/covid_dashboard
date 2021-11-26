import json
import requests

with open('config.json') as f:
    data = json.load(f)

API_KEY = '&apiKey=' + data["keys"]["news"]

def news_API_request(covid_terms="Covid COVID-19 coronavirus"):
    articles = []
    keywords = covid_terms.split()
    query = ''
    for word in keywords:
        query = 'q=' + word.lower() + '&' + query

    base_url = 'https://newsapi.org/v2/everything?'
    final_url = base_url + query + 'language=en' + API_KEY

    r = requests.get(final_url)
    data = r.json()

    for article in data["articles"]:
        temp = {}
        temp["title"] = article["title"]
        temp["content"] = article["description"]
        temp["url"] = article["url"]
        articles.append(temp)

    return articles
