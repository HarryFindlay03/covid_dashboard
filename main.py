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

#TODO: Look at update_news function -> not really sure what this actually wants
#TODO: Fix adding events with repeats as when cancelled it messes up the program
#TODO: Fix time to go being 00 on 59 minutes when repeating update in 24 hours
#TODO: When deleting tasks with same name and time, make sure it deletes the correct task

app = Flask(__name__)   

s = sched.scheduler(time.time, time.sleep)

@app.route('/')
def home():
    """Main flask function that renders the index.html webpage supplied on ELE

    Returns:
        [type]: return render_template
    """
    s.run(blocking=False)
    return render_template('index.html',
                            title= 'Covid Dashboard',
                            image = 'covid_image.jpg',
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
            temp["covid_data"] = Markup("<br> Covid Data Update")
            temp["content"] += temp["covid_data"]

        if request.args.get('news'):
            news = True
            temp["news"] = Markup("<br>News Update")
            temp["content"] += temp["news"]

        #On button click -> updates list is updated
        if add == True:
            if covid == True or news == True:
                update_list.append(temp)
                if covid == True and news == True:
                    queue_covid = schedule_covid_updates(time, label)
                    append_sched(queue_covid)
                    queue_news = schedule_news_updates(time, label)
                    append_sched(queue_news)
                elif covid == True:
                    queue_covid = schedule_covid_updates(time, label)
                    append_sched(queue_covid)
                elif news == True:
                    queue_news = schedule_news_updates(time, label)
                    append_sched(queue_news)
            else:
                print("NOT VALID UPDATE PARAMETERS (PLEASE CHOOSE ATLEAT COVID OR NEWS UPDATE!")
                return redirect('/index', code=302)
            return redirect('/index', code=302)
        return home()

    return home()
    #redirect('/', code=302)
    
def append_sched(queue):
    update_num = len(queue) - 1
    elem = queue[update_num]
    e = s.enter(elem[0], elem[1], elem[2], elem[3])
    events.append(e)
    print(s.queue)

def sort_updates(update: dict):
    return update["seconds_to_go"]

def sort_events(event):
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
