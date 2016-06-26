from datetime import datetime

# This is a throwaway variable to deal with a python bug
throwaway = datetime.strptime('2011-01-01','%Y-%m-%d')

def convert_string_to_date(input_date):
    return datetime.strptime(input_date, "%Y-%m-%d")