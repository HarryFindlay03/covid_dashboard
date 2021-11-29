import json
import time
import sched, time
from datetime import datetime
from flask import Flask, render_template, Markup, request, redirect
from covid_data_handler import parse_csv_data, process_covid_csv_data, covid_API_request, schedule_covid_updates, test_sched
from covid_news_handling import news_API_request
from time_difference import time_to_go

#TODO: Add scheduling, at the moment this is not working at all
#TODO: Look at update_news function -> not really sure what this actually wants
#TODO: Add proper formatting and styling to update notifications using request.Markup()

app = Flask(__name__)

s = sched.scheduler(time.time, time.sleep)


@app.route('/')
def main():
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
        new_time = time_to_go(update["original_time"])[0]
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
            temp["time_to_go"] = "(Time until update: {})".format(time_to_go(time)[0])
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
            e1 = schedule_covid_updates(time, label)
            s.enter(e1[0], e1[1], e1[2], e1[3])
            print(s.queue)
            s.run()
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
