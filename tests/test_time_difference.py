from time_difference import time_to_go

def test_time_to_go():
    #Random time to check function works
    time = time_to_go("12:56")
    #Testing return type of function
    assert isinstance(time, list)