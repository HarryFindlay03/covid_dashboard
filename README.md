# covid_dashboard

When this repo is forked you will see a config_EXAMPLE.json file

![Image showing config_EXAMPLE.json](https://user-images.githubusercontent.com/46387503/143605914-9ffb4a3e-c676-4370-a0a4-d214c6324ac1.png)

Before this code will work we have to do a few things we have to do...

1. Navigate to https://newsapi.org, the webpage should look something like this

![newsapi website example image](https://user-images.githubusercontent.com/46387503/143606404-915c164e-2747-4217-8b6a-005d52f7684f.png)

2. Click on the 'Get API Key ->' button and follow the steps, the developer version of the API is free, so this is the only key you will need

3. Now open the config_EXAMPLE.json file with whatever program you choose. 

4. Copy the API key you just got from https://newsapi.org and replace '<YOUR API KEY GOES HERE>' with the API key you have just copied.

5. rename the config_EXAMPLE.json file to config.json

6. There are other things that you can change in this file like nation (England, Scotland or Wales) and location and area.

7. Try out different locations, do note that different locations need different area types

## location_type
Location types are: "region", "utla" (upper tier local authority), "ltla" (lower tier local authority)

If the website is not working and crashing, try changing the location_type to try and match it to where you are trying to get covid data for

#### Example: 
London requires "location_type": "region"
Exeter requires "location_type": "ltla"
