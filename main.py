"""Module that runs the flask code and drives the dashboard"""
import sched
import time
import logging
from flask import Flask, render_template, Markup, request, redirect
from covid_data_handler import covid_API_request
from covid_news_handling import news_API_request, update_news
from time_difference import time_to_go

#Congiguring logging
FORMAT = '%(levelname)s: %(asctime)s: %(message)s'
logging.basicConfig(filename='program_log.log', format=FORMAT, level=logging.INFO)

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
    """Main update function that is ran when the /index function is reached

    Returns:
        string: Retunring home function that re renders the index.html
        Respone: Rerunning this function when a new update is needed again
    """
    s.run(blocking=False)
    #Updating times in update notifs
    for update in update_list:
        new_time = time_to_go(update["original_time"])
        update["content"] = update["content"].replace(update["time_to_go"], f"(Time until update: {new_time[0]})")
        update["time_to_go"] = f"(Time until update: {new_time[0]})"
        update["seconds_to_go"] = new_time[1]

    update_list.sort(key=sort_updates)

    #Removing events and checking whether they are repeating
    #If events are repeating then re add them
    while len(update_list) > len(s.queue):
        #Pop the first value and due to lists mutability save this popped value to update
        update = update_list.pop(0)
        #Checking whether this update should be repeated
        #IF it should be repeated THEN re add it to the update_list and the scheduler
        if update["repeat"] == True:
            logging.info('UPDATE REPEATING IN 24 HOURS')
            update_list.append(update)
            schedule_update(update)
            #returning to /index makes the code infinetly repeat this for some reason, why does this happen?
            #Some sort of check schedule function to see whether the event has completed? 
            return home()
        logging.info('UPDATE COMPLETED AND REMOVED')


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

            #Removing event from schedule and then events dictionairy
            logging.info('UPDATE REMOVED')
            s.cancel(events[title])
            del events[title]

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
            same_name = False
            if covid == True or news == True:
                #Not allowing 2 updates with the same name
                for update in update_list:
                    if update["title"] == temp["title"]:
                        logging.warning('SAME NAME ENTERED, REDIRECTING BACK!')
                        same_name = True
                if same_name == False:
                    update_list.append(temp)
                    if covid == True and news == True:
                        temp["update"] = 'both'
                    schedule_update(temp)
                    return redirect('/index', code=302)
                else:
                    return redirect('/index', code=302)
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
        logging.info('COVID EVENT QUEUED')
        covid_event = schedule_covid_updates(update_interval, title)
        events.update(covid_event)
    if update_func == 'news' or update_func == 'both':
        logging.info('NEWS EVENT QUEUED')
        news_event = schedule_news_updates(update_interval, title)
        events.update(news_event)

def schedule_covid_updates(update_interval:int, update_name:str) -> str:
    """Schedule a covid update event and re run the covid API request

    Args:
        update_interval (int): The time delta in seconds between the current time and the time the update is required
        update_name (str): The name of the update, what is shown in the update title on the front end

    Returns:
        sched.Event: A scheduler event, an event is added to the scheduler
    """
    temp = {}
    add_event = s.enter(update_interval, 1, get_covid, ())
    temp[update_name] = add_event
    return temp

def schedule_news_updates(update_interval:int, update_name:str) -> str:
    """Schedule a news update event and re run the news API request
    Args:
        update_interval (int): The time delta in seconds between the current time and the time that the update is required
        update_name (str): The name of the update, what is shown in the update title on the front end
    Returns:
        sched.Event: A scheduler event, an event is added to the scheduler
    """
    temp = {}
    add_event = s.enter(update_interval, 1, get_news, ())
    temp[update_name] = add_event
    return temp


def get_covid():
    """Function that runs the covid API request that is called by the scheduler.

    Returns:
        Response: Redirect the user to the index page, so that the relevant updates can take place
    """
    values = covid_API_request()
    return redirect('/index', code=302)

def get_news():
    """Function that runs the news API request via the update_news() function from covid_news_handling, 
    this function is called by the scheduler.

    Returns:
        Response: Redirect the user to the index page, so that the relevant updates can take place
    """
    #Uses update_news function from covid_news_handling as per CA spec
    articles = update_news()
    return redirect('/index', code=302)


def sort_updates(update: dict) -> int:
    """Return the seconds to go to pass to the python .sort() function

    Args:   
        update (dict): Pass in the update dictionary that is filled with the required information
        
    Returns:
        int: The time delta in seconds that is stored in the update dictionary
    """
    return update["seconds_to_go"]

if __name__ == "__main__":
    logging.info('APP STARTING!')
    values = covid_API_request()
    articles = news_API_request()

    update_list = []
    events = {}

    for article in articles:
        article["content"] += Markup(f"<a href={article['url']}> Read more...</a>")

    app.run()
