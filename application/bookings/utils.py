from datetime import datetime, date, timedelta

ISO_FORMAT_STRING = '%Y-%m-%d'

# This is a throwaway variable to deal with a python bug
throwaway = datetime.strptime('2016-01-01', ISO_FORMAT_STRING)


def convert_string_to_date(input_date):
    return datetime.strptime(input_date, ISO_FORMAT_STRING)


def convert_date_to_string(date_):
    return date_.strftime(ISO_FORMAT_STRING)