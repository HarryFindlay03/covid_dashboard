from main import schedule_update
from main import schedule_covid_updates
from main import schedule_news_updates
from main import sort_updates
from main import get_covid
from main import get_news

# def test_schedule_update():
#     update = {"original_time": "13:45", "title": "test schedule update"}
#     test = schedule_update(update, 'test')
#     assert test == True

def test_schedule_covid_update():
    schedule_covid_updates(update_interval=10, update_name='update test')

def test_schedule_news_update():
    schedule_news_updates(update_interval=15, update_name='test news scheduler')

def test_sort_updates():
    update = {"seconds_to_go": 1234}
    assert sort_updates(update) == 1234

def test_get_covid():
    get_covid()

def test_get_news():
    get_news()
