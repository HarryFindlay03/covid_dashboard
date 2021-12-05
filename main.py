import json
from threading import Thread
import threading
import time
import sched, time
from datetime import datetime
from flask import Flask, render_template, Markup, request, redirect
from covid_data_handler import covid_API_request, schedule_covid_updates
from covid_news_handling import news_API_request, schedule_news_updates
from time_difference import time_to_go

#TODO: Add being able to delete events from the schedule!!!!!! 
#TODO: Fix time to go being 00 on 59 minutes when repeating update in 24 hours
#TODO: When deleting tasks with same name and time, make sure it deletes the correct task

app = Flask(__name__)   

s = sched.scheduler(time.time, time.sleep)

@app.route('/')
def home():
    """Main flask function that renders the index.html webpage supplied on ELE

    Returns:
        [str]: Renders the index.html supplied on ele that is the front end for all the data that is 
        supplied by the APIs used. 
    """
    s.run(blocking=False)
    return render_template('index.html',
                            title= 'Covid Dashboard',
                            image = 'covid_image.jpg',
                            favicon = 'static/images/favicon-16x16.png',
                            location=values["area_name"],
                            nation_location=values["nation"],
                            news_articles = articles[0:4],
                            updates = update_list,
                            local_7day_infections = values["seven_days_local"],
                            national_7day_infections = values["seven_days_national"],
                            hospital_cases = 'Hospital Cases: ' + str(values["hospital_cases"]),
                            deaths_total = 'Total Deaths: ' + str(values["total_deaths"]))


@app.route('/index', methods=['GET'])
def update():
    s.run(blocking=False)
    #Updating times in update notifs
    for update in update_list:
        new_time = time_to_go(update["original_time"])
        update["content"] = update["content"].replace(update["time_to_go"], f"(Time until update: {new_time[0]})")
        update["time_to_go"] = f"(Time until update: {new_time[0]})"
        update["seconds_to_go"] = new_time[1]

    update_list.sort(key=sort_updates)
    events.sort(key=sort_events)

    #Removing events and checking whether they are repeating
    #If events are repeating then re add them
    while len(update_list) > len(s.queue):
        '''
        update = update_list.pop(0)
        try:
            if update["repeat"] == True:
                print("Repeating this update!")
                update_list.append(update)
                queue = schedule_covid_updates(update["original_time"], update["title"])
                append_sched(queue)
                print(s.queue)
                return home()
        except KeyError:
            return home()
        '''
        #Pop the first value and due to lists mutability save this popped value to update
        update = update_list.pop(0)
        '''
        if update["repeat"] == True:
            print("Repeating update!")
            #When refresh runs time will be updated by for loop above
            update_list.append(update)
            print("Original time: " + update["original_time"])
            #Add the new event to the scheduler, #Checking for covid or news updates
            queue = schedule_covid_updates(update["original_time"], update["title"])
            append_sched(queue)
            #Sort both the update and events queues so that the repeating update is in the right place
            update_list.sort(key=sort_updates)
            events.sort(key=sort_events)
            return home()
        '''
    if request.method == 'GET':
        temp ={}
        add = False
        covid = False
        news = False
        temp["repeat"] = False
        time = 0
        label = ''

        if request.args.get('notif'):
            title = request.args.get('notif')

            pos_of_article = 0
            for pos, article in enumerate(articles):
                if article['title'] == title:
                    pos_of_article = pos

            del articles[pos_of_article]

            return redirect('/index', code=302)

        if request.args.get('update_item'):
            title = request.args.get('update_item')

            pos_of_update = 0
            for pos, update in enumerate(update_list):
                if update['title'] == title:
                    pos_of_update = pos

            del update_list[pos_of_update]

            #Removing event from schedule queue
            s.cancel(events[pos_of_update])
            print(s.queue)
            del events[pos_of_update]
            return home()

        if request.args.get('update'):
            #time = request.args.get('update') + ':' + str(datetime.now().second)
            time = request.args.get('update')
            temp_time = time_to_go(time)
            temp["time_to_go"] = "(Time until update: {})".format(temp_time[0])
            temp["seconds_to_go"] = temp_time[1]
            temp["original_time"] = time
            temp["content"] = temp["time_to_go"]
            temp["content"] += Markup(f"<br> Update Time: {time}")

        if request.args.get('two'):
            add = True
            label = request.args.get('two')
            temp["title"] = label

        if request.args.get('repeat'):
            temp["repeat"] = True
            temp["content"] += Markup("<br> Repeating Update")

        if request.args.get('covid-data'):
            covid = True
            temp["update"] = 'covid'
            temp["covid_data"] = Markup("<br> Covid Data Update")
            temp["content"] += temp["covid_data"]

        if request.args.get('news'):
            news = True
            temp["update"] = 'news'
            temp["news"] = Markup("<br>News Update")
            temp["content"] += temp["news"]

        #On button click -> updates list is updated
        if add == True:
            if covid == True or news == True:
                update_list.append(temp)
                if covid == True and news == True:
                    temp["update"] = 'both'
                schedule_update(temp)
            else:
                return redirect('/index', code=302)
        return home()

    return home()

def schedule_update(update:dict):
    """Function to check which update is needed and then run the respective scheduling function
    either covid update or news

    Args:
        update (dict): The dictionairy that is filled with the update information that is gathered from the website
    """
    update_func = update["update"]
    update_interval = time_to_go(update["original_time"])[1]
    title = update["title"]
    if update_func == 'covid' or update_func == 'both':
        schedule_covid_updates(update_interval, title)
    if update_func == 'news' or update_func == 'both':
        schedule_news_updates(update_interval, title)

def schedule_covid_updates(update_interval:int, update_name:str) -> sched.Event:
    """Schedule a covid update event and re run the covid API request

    Args:
        update_interval (int): The time delta in seconds between the current time and the time the update is required
        update_name (str): The name of the update, what is shown in the update title on the front end

    Returns:
        sched.Event: A scheduler event, an event is added to the scheduler
    """
    return s.enter(update_interval, 1, covid_update, ())

def schedule_news_updates(update_interval:int, update_name:str) -> sched.Event:
    """Schedule a news update event and re run the news API request

    Args:
        update_interval (int): The time delta in seconds between the current time and the time that the update is required
        update_name (str): The name of the update, what is shown in the update title on the front end

    Returns:
        sched.Event: A scheduler event, an event is added to the scheduler
    """
    return s.enter(update_interval, 1, news_update, ())


def covid_update():
    """Function that runs the covid API request that is called by the scheduler

    Returns:
        str: Returns the home function that will rerender the html template now with the new covid data
    """
    values = covid_API_request()
    return home()

def news_update():
    """Function that runs the news API request, this function is called by the scheduler

    Returns:
        str: Returns the home function that will rerender the html template now with the new news articles
    """
    articles = news_API_request()
    return home()

def sort_updates(update: dict) -> int:
    """Return the seconds to go to pass to the python .sort() function

    Args:   
        update (dict): Pass in the update dictionary that is filled with the required information

    Returns:
        int: The time delta in seconds that is stored in the update dictionary
    """
    return update["seconds_to_go"]

def sort_events(event):
    """Returns the time of the event

    Args:
        event ([sched.Event]): An event in the scheduler

    Returns:
        [Sched.Event.time]: The time value that is scored in the Sched.Event type
    """
    return event.time

if __name__ == "__main__":
    #parse_csv_data('nation_2021-10-28.csv')
    #data = covid_API_request()
    #print(json.dumps(data, indent=4))
    #schedule_covid_updates(time.time()+5, "test London")
    #schedule_covid_updates(time.time()+10, "test Exeter")
    #run_app()

    values = covid_API_request()
    articles = news_API_request()

    update_list = []
    events = []

    for article in articles:
        article["content"] += Markup(f"<a href={article['url']}> Read more...</a>")

    app.run()
