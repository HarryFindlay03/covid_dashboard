import json
import time
import sched, time
from datetime import datetime, timedelta
from flask import Flask, render_template, Markup, request, redirect
from covid_data_handler import parse_csv_data, process_covid_csv_data, covid_API_request, schedule_covid_updates
from covid_news_handling import news_API_request

#TODO: Add scheduling, at the moment this is not working at all
#TODO: Look at update_news function -> not really sure what this actually wants
#TODO: Add proper formatting and styling to update notifications using request.Markup()

app = Flask(__name__)

s = sched.scheduler(time.time, time.sleep)


@app.route('/')
def main():
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
    #Upadating times in update notifs
    #NOT WORKING -> only works for one refresh
    for update in update_list:
        new_time = time_to_go(update["original_time"])
        update["content"] = update["content"].replace(update["time_to_go"], f"(Time until update: {new_time})")
        update["time_to_go"] = f"(Time until update: {new_time})"

    if request.method == 'GET':
        temp ={}
        add = False
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

            return main()

        if request.args.get('update'):
            time = request.args.get('update') + ':00'
            temp["time_to_go"] = "(Time until update: {})".format(time_to_go(time))
            temp["original_time"] = time
            temp["content"] = temp["time_to_go"]
            temp["content"] += Markup(f"<br> Update Time: {time}")

        if request.args.get('two'):
            add = True
            label = request.args.get('two')
            temp["title"] = label

        if request.args.get('repeat'):
            #Add logic to keep adding to schedule
            temp["repeat"] = Markup("<br> Repeating Update")
            temp["content"] += temp["repeat"]

        if request.args.get('covid-data'):
            temp["covid_data"] = Markup("<br> Covid Data Update")
            temp["content"] += temp["covid_data"]

        if request.args.get('news'):
            temp["news"] = Markup("<br>News Update")
            temp["content"] += temp["news"]

        #On button click -> updates list is updated
        if add == True:
            update_list.append(temp)
            #schedule_covid_updates(time, label)
            return redirect('/index', code=302)
        return main()

    return main()
    #redirect('/', code=302)


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

def time_to_go(input_time:str) -> str:
    """Function to compute time delta betweeen time of update and current time
       It will find the difference in seconds, then convert this value to hours:minutes:seconds

    Args:
        input_time ([string]): String taken from front end html submit box with type="time"

    Returns:
        string: To be outputed into the updates notifications on the front end in format
        (hours:minutes:seconds)
    """
    input_time_list = input_time.split(':')
    input_hours, input_minutes, input_seconds = int(input_time_list[0]), int(input_time_list[1]), int(input_time_list[2])

    current_datetime = datetime.now()
    current_year = current_datetime.year
    current_month = current_datetime.month
    current_day = current_datetime.day

    if input_hours < current_datetime.hour:
        current_day += 1
    elif input_hours == current_datetime.hour and input_minutes < current_datetime.minute:
        current_day += 1

    try:
        input_time_obj = datetime(current_year, current_month, current_day, input_hours, input_minutes, input_seconds)
    except ValueError:
        #Increasing the month by one if the increased day is over how many days are in that month
        input_time_obj = datetime(current_year, current_month+1, 1, input_hours, input_minutes, input_seconds)
    except ValueError:
        #If month increases out of range due to being the last day of year (31/12 -> 32/12?) 
        #then increase the year by 1 and set the date to 1st of Jan (1st month)
        input_time_obj = datetime(current_year+1, 1, 1, input_hours, input_minutes, input_seconds)

    #Temp variable to store time difference before formatting
    c = input_time_obj - current_datetime

    total_seconds = c.total_seconds()

    #CONVERT SECONDS TO HOURS:MINUTES:SECONDS
    time_diff_hours = total_seconds / 60 / 60
    time_diff_minutes = (time_diff_hours * 60) % 60
    time_diff_seconds = (time_diff_hours * 3600) % 60

    return str("{}:{}:{}".format(int(time_diff_hours), int(time_diff_minutes), int(time_diff_seconds)))


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

    for article in articles:
        article["content"] += Markup(f"<a href={article['url']}> Read more...</a>")

    app.run()
