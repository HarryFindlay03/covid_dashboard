import json
import time
import sched, time
from flask import Flask, render_template, request, redirect
from covid_data_handler import parse_csv_data, process_covid_csv_data, covid_API_request, schedule_covid_updates
from covid_news_handling import news_API_request

app = Flask(__name__)

s = sched.scheduler(time.time, time.sleep)

values = covid_API_request()
articles = news_API_request()

update_list = []

del_articles = []
del_updates = []



@app.route('/')
def main():
    s.run(blocking=False)
    return render_template('index.html',
                            title= 'Covid Dash-Board',
                            image = 'covid_image.jpg',
                            location=values["area_name"],
                            nation_location=values["nation"],
                            news_articles = articles,
                            updates = update_list,
                            local_7day_infections = values["seven_days_local"],
                            national_7day_infections = values["seven_days_national"],
                            hospital_cases = 'Hospital Cases: ' + str(values["hospital_cases"]),
                            deaths_total = 'Total Deaths: ' + str(values["total_deaths"]))


@app.route('/index', methods=['GET'])
def update():
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

            del_articles.append(pos_of_article)
            del articles[pos_of_article]

            return main()

        if request.args.get('update_item'):
            title = request.args.get('update_item')

            pos_of_update = 0
            for pos, update in enumerate(update_list):
                if update['title'] == title:
                    pos_of_update = pos

            del_updates.append(pos_of_update)
            del update_list[pos_of_update]

            return main()

        if request.args.get('update'):
            time = request.args.get('update')
            temp["content"] = "Time: {0}\n".format(time)
            add = True
            print(time)

        if request.args.get('two'):
            label = request.args.get('two')
            temp["title"] = label

        if request.args.get('covid-data'):
            temp["content"] += "Covid Data Update\n"

        if request.args.get('news'):
            temp["content"] += "News Update\n"

        #Iterate through articles, check which ones have been deleted
        #so that they are not gathered again


        #Going to give articles again, deleted list of articles is needed

        #On button click -> updates list is updated
        if add == True:
            update_list.append(temp)
            schedule_covid_updates(time, label)
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

    app.run()
