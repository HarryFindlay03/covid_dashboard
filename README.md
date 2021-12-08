# covid_dashboard

## Introduction
2021 CA for ECM1400 where we are tasked with building a covid dashboard that displays information pulled from the uk-covid19 api and the newsapi. 

## Prerequisites
Python Version: 3.9.9

## Installation (MACOS)
```
pip3 install -r requirements.txt
```

If this fails, these are the dependencies needed:
```
pip3 install flask
pip3 install uk-covid19
pip3 install pytest
pip3 install pylint
```

## Getting Started Tutorial
In a terminal cd to the root directory of the project.

Running the pwd command here should end in a */covid_dashboard*

To run the project:
1. Make sure you have installed the dependencies (pip3 install -r requirements.txt)
2. Once this have finished running type the following in the terminal:
```
python3 main.py
```
3. This will launch the flask application
4. Open web browser of choice and navigate to *127.0.0.1:5000*
5. You should see the covid dashboard!

### To use the dashboard:
1. Enter a time in the time box
2. Enter a name for the update to be called
3. Tick which options you want: repeat update, covid update, news update
4. Click submit

After clicking submit you will see a new update pop up on the left hand side of the webpage.

## Testing
The zip file will include a covid_dashboard.egg-ingo folder.

This contains all of the relevant of the information needed for pytest to work so running tests should be easy...

Make sure you are in the root folder of the project in the terminal(*/covid_dashboard*)

Type:
```
pytest
```

This will run all of the supplied tests!

## Developer Documentation

## Details
Github Link: https://github.com/HarryFindlay03/covid_dashboard

# FOR GITHUB USERS
Once the covid_dashboard.zip is extracted you will see a config_EXAMPLE.json file

![Image showing config_EXAMPLE.json](https://user-images.githubusercontent.com/46387503/143605914-9ffb4a3e-c676-4370-a0a4-d214c6324ac1.png)

Before this code will work we have to do a few things...

1. Navigate to https://newsapi.org, the webpage should look something like this

![newsapi website example image](https://user-images.githubusercontent.com/46387503/143606404-915c164e-2747-4217-8b6a-005d52f7684f.png)

2. Click on the 'Get API Key ->' button and follow the steps, the developer version of the API is free, so this is the one we want.

3. Now open the config_EXAMPLE.json file with whatever program you choose. 

4. Copy the API key you just got from https://newsapi.org and replace '_YOUR API KEY GOES HERE_' with the API key you have just copied.

![APIKEY PLACEMENT IMAGE](https://user-images.githubusercontent.com/46387503/143689285-31fe84c1-ca78-4d47-9a2f-2b015d7ff36b.png)

5. Rename the config_EXAMPLE.json file to config.json

6. There are other things that you can change in this file like nation (England, Scotland or Wales), location, and area.

7. Try out different locations, do note that different locations need different location_types

## location_type

![PARAMS IMAGE EXAMPLE](https://user-images.githubusercontent.com/46387503/143689354-6c35f1de-9f9d-4c19-92e6-d452feb3c3db.png)

location_type(s)  that are available: "region", "utla" (upper tier local authority), "ltla" (lower tier local authority)

If the website is not working and crashing, try changing the location_type incase it is not correct for which location you are trying to output the data for.

#### Example: 
London requires "location_type": "region"
Exeter requires "location_type": "ltla"

# SETTING UP THE VIRTUAL ENVIRONMENT AND RUNNING THE CODE (MACOS)

#### CD to the directory of the project in the terminal
#### Type this code -> bravo, program should be running.
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

# RUNNING PYTEST
For the tests to run correctly and the modules to be found you have to set up the python module

For this, make sure you are in your virtual environment
- Denoted by a (.venv) at the start of the line in the terminal

Then type:

```
pip install -e .
```

This code is installing the module into itself by running the given *setup.py* file.

``` python
from setuptools import setup, find_packages

setup(name="covid_dashboard", packages=find_packages())
```

Now making sure you are in the root of the project directory
- running pwd should output something ending with */covid_dashboard*

Type:

```
pytest
```

Then all the tests should run!