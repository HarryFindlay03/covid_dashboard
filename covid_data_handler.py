import json
import sched, time
import logging
from uk_covid19 import Cov19API
from time_difference import time_to_go
from datetime import datetime

#Congiguring logging
FORMAT = '%(levelname)s:%(asctime)s:%(message)s'
logging.basicConfig(filename='program_log.log', format=FORMAT, level=logging.INFO)

queue = []
s = sched.scheduler(time.time, time.sleep)

config_data = {}
with open('config.json') as f:
    config_data = json.load(f)
    config_data = config_data["params"]

#Returns a list of strings for the rows in the file given by csv_filename
def parse_csv_data(csv_filename) -> list:
    """Function that puts the data in an inputted csv and returns it in a list"""
    return_list = []
    with open(csv_filename) as f:
        for line in f:
            return_list.append(line)
    return return_list

#returns numbers of cases in 7 days, current number of hospital cases, cumulative number of deaths
def process_covid_csv_data(covid_csv_data):
    """Function that returns the different covid data values from inputted file"""
    last7days_cases = 0
    current_hospital_cases = 0
    total_deaths = 0

    '''
    Posistion 4 -> Cumulative total deaths
    Position 5 -> Current hospital cases
    Position 6 -> Deaths by specimen date

    Last 7 days is gathered by summing the previous 7 days, starting from 2
    days down as the first entry with a value is not truly reliable

    Current hospital cases is gathered by getting the value from the first
    row in the csv

    total deaths is gathered by going through the rows until a value is found
    in the total deaths column
    '''
    #Last 7 days
    for i in range(3, 10):
        data = covid_csv_data[i].split(',')
        last7days_cases += int(data[6])

    #Current hospital cases
    current_hospital_cases = covid_csv_data[1].split(',')[5]

    #While loop used as not knowing how many times I should iterate
    #Starting from 1 as first line is the information from the file
    i = 1
    while i < len(covid_csv_data):
        data = covid_csv_data[i].split(',')
        if data[4] != '':
            total_deaths = data[4]
            break
        i += 1

    return last7days_cases, int(current_hospital_cases), int(total_deaths)

def covid_API_request(location=config_data["location"], location_type=config_data["location_type"]) -> dict:
    """Function to return live data from the uk-covid19 API

    Args:
        location (string, optional): Location at which the API is getting data for. Defaults to config_data["location"].
        location_type ([string], optional): Type of area e.g. region, utla or ltla. Defaults to config_data["location_type"].

    Returns:
        dict: [description]
    """
    logging.info('PROGRAM LOG: COVID UPDATE')
    return_dict = dict()
    return_dict["seven_days_local"] = 0
    return_dict["seven_days_national"] = 0

    API_filters_local = [
        f'areaName={location}',
        f'areaType={location_type}',
    ]

    cases_and_deaths_local = {
        "date": "date",
        "areaName": "areaName",
        "newCasesBySpecimenDate": "newCasesBySpecimenDate",

        #"hospitalCases": "hospitalCases",
        #"cumDeathsByPublishDate": "cumDeathsByPublishDate"
    }

    API_filters_national = [
        'areaType=nation'
    ]

    cases_and_deaths_national = {
        "date": "date",
        "hospitalCases": "hospitalCases",
        "newCasesByPublishDate": "newCasesByPublishDate",
        "cumDeaths28DaysByPublishDate": "cumDeaths28DaysByPublishDate"
    }

    api = Cov19API(filters=API_filters_local, structure=cases_and_deaths_local)
    data_local = api.get_json()

    for val in data_local['data']:
        if val['areaName'] != None:
            return_dict['area_name'] = val['areaName']
            break

    #7 day cases local
    for pos, val in enumerate(data_local['data']):
        if pos > 6:
            break
        return_dict["seven_days_local"] += val["newCasesBySpecimenDate"]

    #National data like hospital cases, 7 day national count and total deaths
    api = Cov19API(filters=API_filters_national, structure=cases_and_deaths_national)
    data_national = api.get_json()

    #7 day national count
    for pos, val in enumerate(data_national['data']):
        if pos > 6:
            break
        return_dict["seven_days_national"] += val["newCasesByPublishDate"]

    #Hospital cases
    for val in data_national['data']:
        if val['hospitalCases'] != None:
            return_dict['hospital_cases'] = val['hospitalCases']
            break

    #Total deaths
    for val in data_national['data']:
        if val['cumDeaths28DaysByPublishDate'] != None:
            return_dict['total_deaths'] = val['cumDeaths28DaysByPublishDate']
            break

    return_dict["nation"] = "England"
    return return_dict


def schedule_covid_updates(update_interval, update_name, location=config_data["location"], location_type=config_data["location_type"]):
    """Function to add updates to a queue to then perform then"""
    #Finding the time difference in seconds
    time_delay = time_to_go(update_interval)[1]
    print("Adding event to queue! Event happening in: {} seconds".format(time_delay))
    queue.append([time_delay, 1, covid_API_request, (location, location_type)])
    return queue

