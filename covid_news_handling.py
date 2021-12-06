import json
import requests
from datetime import datetime
from time_difference import time_to_go

'''
#Congiguring logging
FORMAT = '%(levelname)s: %(asctime)s: %(message)s'
logging.basicConfig(filename='program_log.log', format=FORMAT, level=logging.INFO)
'''

with open('config.json') as f:
    data = json.load(f)

API_KEY = '&apiKey=' + data["keys"]["news"]

queue = []

def news_API_request(covid_terms="Covid COVID-19 coronavirus"):
    #logging.info('PROGRAM LOG: NEWS UPDATE')
    print("NEWS UPDATE COMMENCING")
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

def update_news(testing='false'):
    if testing == 'false':
        articles = news_API_request()
        return articles
    elif testing == 'test':
        pass
