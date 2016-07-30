import sys
import logging
import json

from collections import defaultdict
from datetime import timedelta, datetime
from application.common import utils
from application.contents import data

from . import get_resort_data
from . import get_dictionary_data

DATE_ISO_FORMAT = '%Y-%m-%d'

# resort-names - used as resort ID
RESORT_NAME_LIST = ["bj", "kirk", "dw", "kirt", "plp", "pelican", "vp", "vbay", "vwind"]

# photo file path
PHOTO_PATH_THUMB = 'https://dl.dropboxusercontent.com/u/122147773/gokitebaja/image-480/la-ventana-'
PHOTO_PATH_1X = 'https://dl.dropboxusercontent.com/u/122147773/gokitebaja/image/la-ventana-'
PHOTO_PATH_2X = 'https://dl.dropboxusercontent.com/u/122147773/gokitebaja/image/la-ventana-'

class ResortInfo(object):
    def __init__(self, resort, begin_date, end_date, count=None):
        self.resort = resort
        self.begin_date = begin_date
        self.end_date = end_date
        self.profile_photo = None
        self.photos = None
        self.units = None
        self.unit_info_list = []
        self.count = count
        self.active = True

        self.check_active()
        self.build_profile_photo()

    def __repr__(self):
        return "(resort name = %s : begin_date = %s end_date = %s count = %s)" \
               % (self.resort.name, self.begin_date, self.end_date, self.count)

    # deactivate some resorts for now
    def check_active(self):
        if self.resort.name == 'vp' or self.resort.name == 'vwind':
            self.active = False

    def build_profile_photo(self):
        profile_photos = get_dictionary_data().profile_photo_dict[self.resort.name]
        self.profile_photo = get_first_element(profile_photos)

    def set_units(self, units):
        self.units = units

    def set_unit_info_list(self, unit_info_list):
        self.unit_info_list = unit_info_list

    def serialize_resort_summary(self):
        if self.resort is None:
            return {}

        # TODO - set unit data from /search
        units = find_units_by_resort_name(self.resort.name)
        price_list = []
        for unit in units:
            unit_info = UnitInfo(unit, self.begin_date, self.end_date)
            if unit_info.avg_price:
                price_list.append(unit_info.avg_price)

        return {
            'name': self.resort.name,
            'displayName': self.resort.displayName,
            'profilePhoto': serialize_profile_photo(self.profile_photo),
            'beachFront': self.resort.privateBeach,
            'price': min(price_list) if price_list else None,
            'maxPrice': max(price_list) if price_list else None,
            'highlights': serialize_resort_highlight(self.resort),
            'count': self.count,
            'active': self.active
        }

    def serialize_resort_info(self):
        resort = self.resort
        if resort is None:
            return {}

        self.units = find_units_by_resort_name(self.resort.name)
        self.photos = find_photos_by_resort_name(self.resort.name)

        return {
            'name': resort.name,
            'displayName': resort.displayName,
            'profilePhoto': serialize_profile_photo(self.profile_photo),
            'beachFront': resort.privateBeach,
            'wifi': resort.wifi,
            'pool': resort.swimPool,
            'kiteSchool': resort.lessonKite,
            'desc': resort.about,
            'highlights': serialize_resort_highlight(resort),
            'generalSection': serialize_section_general(resort),
            'foodSection': serialize_section_food(resort),
            'activitySection': serialize_section_activity(resort),
            'policySection': serialize_section_policy(resort),
            'unitTypes': self.serialize_units_summary(),
            'photos': serialize_photos(self.photos),
            'active': self.active
        }

    def serialize_units_summary(self):
        units_json = []
        if self.unit_info_list:
            for unit_info in self.unit_info_list:
                print unit_info.serialize_unit_summary()
                units_json.append(unit_info.serialize_unit_summary())
        else:
            for unit in self.units:
                units_json.append(UnitInfo(unit, self.begin_date, self.end_date).serialize_unit_summary())
        return units_json


class UnitInfo(object):
    def __init__(self, unit, begin_date, end_date, count=None):
        self.unit = unit
        self.begin_date = begin_date
        self.end_date = end_date
        self.count = count
        self.profile_photo = None
        self.photos = None
        self.price_info_list = []
        self.avg_price = 0

        self.build_profile_photo()
        self.build_price_info()
        self.build_avg_price()

    def __repr__(self):
        return "(unit type name = %s : begin_date = %s end_date = %s : count = %s price = %s)" \
               % (self.unit.typeName, self.begin_date, self.end_date, self.count, self.avg_price)

    def build_profile_photo(self):
        self.profile_photo = get_first_element(get_dictionary_data().photos_by_unit_dict[self.unit.typeName])

    def build_price_info(self):
        # if begin_date is null, show price for today
        if not self.begin_date:
            self.begin_date = datetime.today()

        # if end_date is null, show price for begin date
        if not self.end_date:
            self.end_date = self.begin_date + timedelta(days=1)
            # date = convert_string_to_date(begin_date)

        # build PriceInfo for each date
        for single_date in daterange(self.begin_date, self.end_date):
            unitname = self.unit.typeName
            price_info = PriceInfo(unitname, utils.convert_date_to_string(single_date), find_price_for_date(unitname, single_date))
            self.price_info_list.append(price_info)

    def build_avg_price(self):
        if not self.price_info_list[0].price:
            self.avg_price = None
            return
        sum_val = sum(p.price for p in self.price_info_list)
        if not sum_val:
            self.avg_price = None
            return
        avg_price = sum_val / float(len(self.price_info_list))
        self.avg_price = int(avg_price)

    def serialize_unit_summary(self):
        unit = self.unit
        if unit is None:
            return {}

        return {
            'unitType': unit.typeName,
            'type': unit.type,
            'displayName': unit.displayName,
            'profilePhoto': build_photo_url_full_1x(self.profile_photo),
            'maxCapacity': unit.maxCapacity,
            'count': self.count,
            'price': self.avg_price,
            'priceMatrix': serialize_prices(self.price_info_list)
        }

    def serialize_unit_detail(self):
        unit = self.unit
        if unit is None:
            return {}

        resort = find_resort_by_name(self.unit.resortName)
        photos = find_photos_by_unit_type(self.unit.typeName)

        return {
            'unitType': unit.typeName,
            'displayName': unit.displayName,
            'profilePhoto': serialize_profile_photo(self.profile_photo),
            'price': self.avg_price,
            'priceMatrix': serialize_prices(self.price_info_list),
            'resortName': unit.resortName,
            'resortDisplayName': resort.displayName,
            'photos': serialize_photos(photos),
            'highlight': serialize_unit_highlight(unit),
            'space': serialize_unit_space(unit),
            'amenity': serialize_unit_amenity(unit),
            'resortPolicy': serialize_section_policy(resort),
            'resortGeneral': serialize_section_general(resort),
            'resortFood': serialize_section_food(resort)
        }


class PriceInfo(object):
    def __init__(self, unit, date, price):
        self.unit = unit
        self.date = date
        self.price = price

    def __repr__(self):
        return "(unit = %s : date = %s , price = %i)" % (self.unit, self.date, self.price)

    def serialize_price_info(self):
        unit = self.unit
        if unit is None:
            return {}
        return {
            'name': self.unit,
            'date': self.date,
            'price': self.price if self.price else 0
        }


def serialize_resort_info_list(resort_info_list):
    json = []
    for resort_info in resort_info_list:
        json.append(resort_info.serialize_resort_summary())
    return json


def find_all_resorts():
    return get_resort_data().resorts


def find_resort_by_name(resortname):
    for resort in get_resort_data().resorts:
        if resort.name == resortname:
            return resort
    return None


def find_units_by_resort_name(resortname):
    return get_dictionary_data().units_by_resort_dict[resortname]


def find_unit_by_name(name):
    for unit in get_resort_data().units:
        if unit.typeName == name:
            return unit
    return None


def find_photos_by_resort_name(resortname):
    return get_dictionary_data().photos_by_resort_dict[resortname]


def find_photos_by_unit_type(typename):
    return get_dictionary_data().photos_by_unit_dict[typename]


def find_profile_photo_for_unit_type(typename):
    return get_dictionary_data().photos_by_unit_dict[typename]


def find_photos_by_resort_name(resortname):
    return get_dictionary_data().photos_by_resort_dict[resortname]


def find_photos_by_unit_type(typename):
    return get_dictionary_data().photos_by_unit_dict[typename]


def find_profile_photo_for_unit_type(typename):
    return get_first_element(get_dictionary_data().photos_by_unit_dict[typename])


def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)


def find_price_data_for_unit(unitname):
    for price_data in get_resort_data().prices:
        if price_data.typeName == unitname:
            return price_data
    return None


def find_price_for_date(unitname, date):
    price_data = find_price_data_for_unit(unitname)

    if price_data is None:
        return None

    if price_data and price_data.promoBeginDate and is_in_range(date, price_data.promoBeginDate, price_data.promoEndDate):
        return convert_price_string_to_number(price_data.promoPrice)
    elif price_data.peakBeginDate1 and is_in_range(date, price_data.peakBeginDate1, price_data.peakEndDate1):
        return convert_price_string_to_number(price_data.peakPrice1)
    elif price_data.peakBeginDate2 and is_in_range(date, price_data.peakBeginDate2, price_data.peakEndDate2):
        return convert_price_string_to_number(price_data.peakPrice2)
    elif price_data.highBeginDate and is_in_range(date, price_data.highBeginDate, price_data.highEndDate):
        return convert_price_string_to_number(price_data.highPrice)
    else:
        return convert_price_string_to_number(price_data.lowPrice)


def is_in_range(date, begin_date_str, end_date_str):
    if utils.convert_string_to_date(begin_date_str) <= date <= utils.convert_string_to_date(end_date_str):
        return True
    return False


def convert_price_string_to_number(price_string):
    if not price_string:
        return None
    return int(float(price_string))


def get_first_element(list):
    return list[0] if list else None


def build_photo_url(file_path, photo):
    if not photo:
        return None
    if photo.ext:
        url = file_path + photo.fileName + photo.ext
    else:
        url = file_path + photo.fileName + '.jpg'
    return url


def build_photo_url_thumb(photo):
    return build_photo_url (PHOTO_PATH_THUMB, photo)


def build_photo_url_full_1x(photo):
    return build_photo_url (PHOTO_PATH_1X, photo)


def build_photo_url_full_2x(photo):
    return build_photo_url (PHOTO_PATH_2X, photo)


def serialize_prices(prices):
    json = []
    for price in prices:
        json.append(PriceInfo.serialize_price_info(price))
    return json


def serialize_photos(photos):
    json = []
    for photo in photos:
        json.append(serialize_photo(photo))
    return json


def serialize_photo(photo):
    if not photo:
        return None
    return {
        # 'resortName': photo.resortName,
        'photoUrl': build_photo_url_full_1x(photo),
        'alt': photo.alt,
        'group': photo.group,
        'unitGroup': photo.unitGroup,
    }


def serialize_profile_photo(photo):
    if not photo:
        return None
    return {
        'thumbUrl': build_photo_url_thumb(photo),
        'thumbUrl2x': build_photo_url_thumb(photo),
        'thumbUrl3x': "",
        'photoUrl': build_photo_url_full_1x(photo),
        'photoUrl2x': build_photo_url_full_2x(photo),
        'photoUrl3x': ""
    }


def serialize_resort_highlight(resort):
    highlight = []
    if resort.privateBeach == 'Y':
        highlight.append('Beachfront')
    if resort.swimPool == 'Y':
        highlight.append('Pool')
    if resort.lessonKite == 'Y':
        highlight.append('Kite school')
    if resort.wifi == 'Y':
        highlight.append('Wifi')

    return highlight


def serialize_section_general(resort):
    data = []
    if resort.wifi == 'Y':
        data.append('Free Wifi')
    if resort.parking == 'Y':
        data.append('Free Parking')
    return data


def serialize_section_food(resort):
    data = []
    if resort.communalKitchen == 'Y':
        data.append('Communal Kitchen')
    if resort.freeBreakfast == 'Y':
        data.append('Free Breakfast')
    if resort.noteOnFood:
        # data.append(resort.noteOnFood)
        data.extend(x.lstrip() for x in resort.noteOnFood.split(","))
    return data


def serialize_section_activity(resort):
    data = []
    if resort.swimPool == 'Y':
        data.append('Swimming Pool')
    if resort.lessonKite == 'Y':
        data.append('Kiteboarding Lesson')
    if resort.rentKite == 'Y':
        data.append('Kiteboarding Gear Rental')
    if resort.lessonWindsurf == 'Y':
        data.append('Windsurfing Lesson')
    if resort.rentWindsurf == 'Y':
        data.append('Windsurfing Gear Rental')
    if resort.fishingTrip == 'Y':
        data.append('Fishing Trip')
    if resort.scubaDivingTrip == 'Y':
        data.append('Scuba Diving Trip')
    if resort.rentPerformanceMtnBike == 'Y':
        data.append('Performance Bike Rental')
    if resort.mtnbike == 'Y':
        data.append('Free Mountain/Cruiser Bike Rental')
    if resort.noteOnActivity:
        # data.append(resort.noteOnActivity)
        data.extend(x.lstrip() for x in resort.noteOnActivity.split(","))
    if resort.yoga == 'Y':
        data.append('Yoga')
    if resort.massage == 'Y':
        data.append('Massage')
    return data


def serialize_section_policy(resort):
    return {
        'checkIn': resort.checkIn,
        'checkOut': resort.checkOut,
        'ccAccepted': resort.cc,
        'extraPersonCharge': resort.extraPersonCharge,
        'petsAllowed': resort.pets,
        'minimumStay': resort.minimumStay,
        'cancelPolicy': resort.cancelPolicy
    }


def serialize_unit_highlight(unit):
    highlight = []
    highlight.append(serialize_unit_type(unit))
    highlight.append(unit.numBedroom + ' Bedrooms')
    highlight.append(unit.numBathroom + ' Bathrooms')
    if (unit.type == 'ROOM' or unit.type == 'BUNGALOW') and unit.numBathroom >= '1':
        highlight.append('Private Bath')
    return highlight


def serialize_unit_space(unit):
    return {
        'maxCapacity': unit.maxCapacity,
        'numBedroom': unit.numBedroom,
        'numBathroom': unit.numBathroom,
        'type': unit.type,
        'bedSetup': unit.bedSetup
    }


def serialize_unit_amenity(unit):
    amenity = []
    if unit.kitchen == 'Y':
        amenity.append('Kitchen')
    if unit.kitchenette == 'Y':
        amenity.append('Kitchenette')
    if unit.ac == 'Y':
        amenity.append('AC')
    if unit.patio == 'Y':
        amenity.append('Patio')
    if unit.seaview == 'Y':
        amenity.append('Seaview')
    return amenity


def serialize_unit_type(unit):
    if unit.type == 'CASA' or unit.type == 'CASITA' or unit.type == 'HOUSE':
        return "Entire home/apt"
    elif unit.type == 'BUNGALOW':
        return 'Standalone bungalow'
    elif unit.type == 'ROOM':
        return 'Room'
        # else:
        #     return 'Unknown'

