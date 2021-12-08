"""Function that gets the news API request and updates the news."""
import json
import logging
import requests

#Congiguring logging
FORMAT = '%(levelname)s: %(asctime)s: %(message)s'
logging.basicConfig(filename='program_log.log', format=FORMAT, level=logging.INFO)

with open('config.json', 'r', encoding="utf8") as f:
    data = json.load(f)

API_KEY = '&apiKey=' + data["keys"]["news"]

queue = []

def news_API_request(covid_terms="Covid COVID-19 coronavirus") -> list:
    """newsapi request that returns a list of articles got from the constructed URL
    in the function

    Args:
        covid_terms (str, optional): The keyword terms that are added into the URL.
        Defaults to "Covid COVID-19 coronavirus".

    Returns:
        list: List of articles returned from the request
    """
    logging.info('NEWS UPDATE')
    articles = []
    keywords = covid_terms.split()
    query = ''
    for word in keywords:
        query = 'q=' + word.lower() + '&' + query

    base_url = 'https://newsapi.org/v2/everything?'
    final_url = base_url + query + 'language=en' + API_KEY

    req = requests.get(final_url)
    articles_json = req.json()

    for article in articles_json["articles"]:
        temp = {}
        temp["title"] = article["title"]
        temp["content"] = article["description"]
        temp["url"] = article["url"]
        articles.append(temp)

    return articles

def update_news(testing='false') -> list:
    """Function that re runs the news API request

    Args:
        testing (str, optional): check whether to run the API request or not.
        Defaults to 'false'.

    Returns:
        list: List of news articles
    """
    if testing == 'test':
        test_article = {}
        test_articles = []
        test_article["title"] = "COOL NEWS"
        test_article["content"] = "COVID IS BAD"
        test_articles.append(test_article)
        return test_article
    articles = news_API_request()
    return articles
