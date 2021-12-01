import json
import time
import sched, time
from datetime import datetime
from flask import Flask, render_template, Markup, request, redirect
from werkzeug.datastructures import UpdateDictMixin
from covid_data_handler import parse_csv_data, process_covid_csv_data, covid_API_request, schedule_covid_updates
from covid_news_handling import news_API_request, schedule_news_updates
from time_difference import time_to_go

#TODO: Scheduling is running at minutes and not to nearest minute -> will have to add  threading
#TODO: Look at update_news function -> not really sure what this actually wants
#TODO: ADD checking user inputs are correct and not accepting them if they are not

app = Flask(__name__)

s = sched.scheduler(time.time, time.sleep)

@app.route('/')
def home():
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
        update = update_list.pop(0)
        if update["repeat"] == True:
            print("Repeating this update!")
            update_list.append(update)
            queue = schedule_covid_updates(update["original_time"], update["title"])
            append_sched(queue)
            return home()


    if request.method == 'GET':
        temp ={}
        add = False
        covid = False
        news = False
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
            del events[pos_of_update]
            return home()

        if request.args.get('update'):
            #time = request.args.get('update') + ':' + str(datetime.now().second)
            time = request.args.get('update') + ':00'
            temp_time = time_to_go(time)
            temp["time_to_go"] = "(Time until update: {})".format(temp_time[0])
            temp["seconds_to_go"] = temp_time[1]
            temp["original_time"] = time
            temp["content"] = temp["time_to_go"]
            temp["content"] += Markup(f"<br> Update Time: {time[:-3]}")

        if request.args.get('two'):
            add = True
            label = request.args.get('two')
            temp["title"] = label

        if request.args.get('repeat'):
            #Add logic to keep adding to schedule
            #TODO: Get repeating function working
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
            update_list.append(temp)
            if covid == True and news == True:
                queue_covid = schedule_covid_updates(time, label)
                append_sched(queue_covid)
                #RUN news update 1 second after covid update to stop conflict
                #TODO: NOT WORKING -> IF SECOND IS LESS THAN 10 THIS WON'T work , need to pad 0s
                time = time[:len(time)-2] + str(datetime.now().second + 1) 
                queue_news = schedule_news_updates(time, label)
                append_sched(queue_news)
            elif covid == True:
                queue_covid = schedule_covid_updates(time, label)
                append_sched(queue_covid)
            elif news == True:
                queue_news = schedule_news_updates(time, label)
                append_sched(queue_news)
            else:
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

def sort_updates(update: dict):
    return update["seconds_to_go"]

def sort_events(event):
    return event.time

def test_parse_csv_data():
    data = parse_csv_data('nation_2021-10-28.csv')
    assert len (data) == 639

def test_process_covid_csv_data():
    last7days_cases, current_hospital_cases, total_deaths = process_covid_csv_data(parse_csv_data('nation_2021-10-28.csv'))
    assert last7days_cases == 240299
    assert current_hospital_cases == 7019
    assert total_deaths == 141544

#test_parse_csv_data()
#test_process_covid_csv_data()

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
