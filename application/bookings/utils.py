from datetime import datetime, date, timedelta

ISO_FORMAT_STRING = '%Y-%m-%d'
DEFAULT_INTERVAL = 14   # show next/prev 14 days

# This is a throwaway variable to deal with a python bug
throwaway = datetime.strptime('2016-01-01', ISO_FORMAT_STRING)


def convert_string_to_date(input_date):
    return datetime.strptime(input_date, ISO_FORMAT_STRING)


def convert_date_to_string(date_):
    return date_.strftime(ISO_FORMAT_STRING)


def get_todays_date():
    return datetime.now().date()


def get_default_begin_date():
    begin_date = '2016-07-01'
    return convert_string_to_date(begin_date)


def get_default_end_date(begin_date):
    return begin_date + timedelta(days=DEFAULT_INTERVAL - 1)


