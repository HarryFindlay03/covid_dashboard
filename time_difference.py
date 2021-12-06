from datetime import datetime

def time_to_go(input_time:str) -> tuple:
    """Function to compute time delta betweeen time of update and current time
       It will find the difference in seconds, then convert this value to hours:minutes:seconds

    Args:
        input_time ([string]): String taken from front end html submit box with type="time"

    Returns:
        tuple: 0th index being the string output for flask webpage, 1st index being the total seconds to add to the scheduler
    """
    input_time_list = input_time.split(':')
    input_hours, input_minutes = int(input_time_list[0]), int(input_time_list[1])

    current_datetime = datetime.now()
    current_year = current_datetime.year
    current_month = current_datetime.month
    current_day = current_datetime.day

    if input_hours < current_datetime.hour:
        current_day += 1
    elif input_hours == current_datetime.hour and input_minutes < current_datetime.minute:
        current_day += 1

    try:
        input_time_obj = datetime(current_year, current_month, current_day, input_hours, input_minutes, current_datetime.second)
    except ValueError:
        #Increasing the month by one if the increased day is over how many days are in that month
        input_time_obj = datetime(current_year, current_month+1, 1, input_hours, input_minutes, current_datetime.second)
    except ValueError:
        #If month increases out of range due to being the last day of year (31/12 -> 32/12?) 
        #then increase the year by 1 and set the date to 1st of Jan (1st month)
        input_time_obj = datetime(current_year+1, 1, 1, input_hours, input_minutes, current_datetime.second)

    total_seconds = 0
    time_diff_hours = 0
    time_diff_minutes = 0

    #If minutes are the same, then it is 23 hours and 59 minutes to go
    if input_time_obj.minute == current_datetime.minute:
        total_seconds = 86_400
        time_diff_hours = 23
        time_diff_minutes = 59
    #else do normal calculations to get the time to go
    else:
        #Temp variable to store time difference before formatting
        c = input_time_obj - current_datetime

        total_seconds = c.total_seconds()

        #CONVERT SECONDS TO HOURS:MINUTES:SECONDS
        time_diff_hours = total_seconds / 60 / 60
        time_diff_minutes = (time_diff_hours * 60) % 60

    return_str = "{}:{}"
    return [return_str.format(int(time_diff_hours), int(time_diff_minutes)), total_seconds]