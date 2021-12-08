"""Module to handle the covid API and CSV file"""
import json
import sched
import time
import logging
from uk_covid19 import Cov19API

#Congiguring logging
FORMAT = '%(levelname)s: %(asctime)s: %(message)s'
logging.basicConfig(filename='program_log.log', format=FORMAT, level=logging.INFO)


queue = []
s = sched.scheduler(time.time, time.sleep)

config_data = {}
with open('config.json', 'r', encoding='utf8') as f:
    config_data = json.load(f)
    config_data = config_data["params"]

def parse_csv_data(csv_filename: str) -> list:
    """Parsing a csv file to return a list of strings for the rows in the
    given filename

    Args:
        csv_filename (str): Filename of file wanting to be parsed

    Returns:
        list: The list of strings for rows in file
    """
    return_list = []
    with open(csv_filename, encoding='utf8') as csv_file:
        for line in csv_file:
            return_list.append(line)
    return return_list

#returns numbers of cases in 7 days, current number of hospital cases, cumulative number of deaths
def process_covid_csv_data(covid_csv_data: list) -> tuple:
    """Returns data from the inputted csv file

    Args:
        covid_csv_data (list): Inputted csv file that data wants to be gathered from

    Returns:
        tuple: The outputted data
    """
    last7days_cases = 0
    current_hospital_cases = 0
    total_deaths = 0

    # Posistion 4 -> Cumulative total deaths
    # Position 5 -> Current hospital cases
    # Position 6 -> Deaths by specimen date

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
        location (string, optional): Location at which the API is getting data for.
        Defaults to config_data["location"].
        location_type ([string], optional): Type of area e.g. region, utla or ltla.
        Defaults to config_data["location_type"].

    Returns:
        dict: [description]
    """
    logging.info('COVID UPDATE')
    return_dict = {}
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
        "cumDailyNsoDeathsByDeathDate": "cumDailyNsoDeathsByDeathDate"
    }

    api = Cov19API(filters=API_filters_local, structure=cases_and_deaths_local)
    data_local = api.get_json()

    for val in data_local['data']:
        if val['areaName'] is not None:
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
        if val['hospitalCases'] is not None:
            return_dict['hospital_cases'] = val['hospitalCases']
            break

    #Total deaths
    for val in data_national['data']:
        if val['cumDailyNsoDeathsByDeathDate'] is not None:
            return_dict['total_deaths'] = val['cumDailyNsoDeathsByDeathDate']
            break

    return_dict["nation"] = "England"
    return return_dict
    