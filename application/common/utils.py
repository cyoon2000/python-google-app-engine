from datetime import datetime, date, timedelta

ISO_FORMAT_STRING = '%Y-%m-%d'
ONE_DAY = 1
ONE_WEEK = 7
TWO_WEEKS = 14

weekday_dict = {0: 'Mo', 1: 'Tu', 2: 'We', 3: 'Th', 4: 'Fr', 5: 'Sa', 6: 'Su'}

# This is a throwaway variable to deal with a python bug
throwaway = datetime.strptime('2016-01-01', ISO_FORMAT_STRING)


def convert_string_to_date(input_date):
    return datetime.strptime(input_date, ISO_FORMAT_STRING)


def convert_date_to_string(date_):
    return date_.strftime(ISO_FORMAT_STRING)


def name_weekday(weekday):
    return weekday_dict[weekday]


def get_todays_date():
    return datetime.now().date()


def get_default_begin_date():
    return get_todays_date()


def get_after_date(date_, days):
    return date_ + timedelta(days=days)


def get_before_date(date_, days):
    return date_ - timedelta(days=days)


def get_begin_date(request):
    # parse parameter
    begin_date = request.args.get('from')

    # use default if not provided
    if not begin_date:
        begin_date = get_default_begin_date()
        begin_date = convert_date_to_string(begin_date)

    begin_date = convert_string_to_date(begin_date)
    return begin_date


def get_end_date(request, days=1):
    # parse parameter
    # begin_date = request.args.get('from')
    begin_date = get_begin_date(request)
    end_date = request.args.get('to')

    # use default if not provided
    # if not begin_date:
    #     begin_date = get_default_begin_date()

    if not end_date:
        # returns begin_date + days
        end_date = get_after_date(begin_date, days)
        end_date = convert_date_to_string(end_date)

    end_date = convert_string_to_date(end_date)
    return end_date
