import data
import logging

from collections import defaultdict
from datetime import datetime

# resort-names - used as resort ID
RESORT_NAME_LIST = ["bj", "kirk", "dw", "kirt", "plp", "pelican", "vp", "vbay", "vwind"]

# photo file path
PHOTO_PATH_THUMB = 'https://dl.dropboxusercontent.com/u/122147773/gokitebaja/image-480/la-ventana-'
PHOTO_PATH_1X = 'https://dl.dropboxusercontent.com/u/122147773/gokitebaja/image/la-ventana-'
PHOTO_PATH_2X = 'https://dl.dropboxusercontent.com/u/122147773/gokitebaja/image/la-ventana-'

class ResortInfo(object):
    def __init__(self, resort):
        self.resort = resort
        self.profile_photo = None
        self.photos = None
        self.units = None

    def set_profile_photo(self, profile_photo):
        self.profile_photo = profile_photo

    def set_photos(self, photos):
        self.photos = photos

    def set_units(self, units):
        self.units = units

    def serialize_resort_summary(self, resort, profile_photo):
        if resort is None:
            return {}
        return {
            'name': resort.name,
            'displayName': resort.displayName,
            'profilePhoto': serialize_profile_photo(profile_photo),
            'beachFront': resort.privateBeach,
            'price': 150,
            'desc': ''
        }

    def serialize_resort_info(self):
        resort = self.resort
        if resort is None:
            return {}
        return {
            'name': resort.name,
            'displayName': resort.displayName,
            'profilePhoto': serialize_profile_photo(self.profile_photo),
            'beachFront': resort.privateBeach,
            'wifi': resort.wifi,
            'pool': resort.swimPool,
            'kiteSchool': resort.lessonKite,
            'price': 150,
            # TODO - replace with real!
            'desc': get_mock_desc(),
            # 'highlight': serialize_resort_highlight(resort),
            'generalSection': serialize_section_general(resort),
            'foodSection': serialize_section_food(resort),
            'activitySection': serialize_section_activity(resort),
            'policySection': serialize_section_policy(resort),
            'unitTypes': serialize_units_summary(self.units),
            'photos': serialize_photos(self.photos)
        }


class UnitInfo(object):
    def __init__(self, unit):
        self.unit = unit
        self.profile_photo = None
        self.photos = None

    def set_profile_photo(self, profile_photo):
        self.profile_photo = profile_photo

    # @staticmethod
    # def serialize_units_summary(units):
    #     units_json = []
    #     for unit in units:
    #         units_json.append(serialize_unit_summary(unit))
    #     return units_json

    # @staticmethod
    # def serialize_unit_summary(unit):
    #     return {
    #         'displayName': unit.displayName,
    #         'profilePhoto': get_mock_unit_profile_photo(),
    #         'maxCapacity': unit.maxCapacity,
    #         'price': 150
    #     }
    #
    # @staticmethod
    # def serialize_unit_detail(unit):
    #     return {
    #         'displayName': unit.displayName,
    #         'profilePhoto': get_mock_unit_profile_photo(),
    #         'maxCapacity': unit.maxCapacity,
    #         'price': 150
    #         }


def serialize_resorts(resorts):
    json = []
    # resort_instance = Resort()
    for resort in resorts:
        resort_info = ResortInfo(resort)
        # json.append(resortInfo.serialize_resort_summary(resort))
        profile_photo = find_profile_photo_by_resort_name(resort.name)
        json.append(resort_info.serialize_resort_summary(resort, profile_photo))
    return json


def serialize_resort_detail(resort):
    return ResortInfo().serialize_resort_detail(resort)


def find_all_resorts():
    return data.ResortData.resorts


def find_resort_by_name(resortname):
    for resort in data.ResortData.resorts:
        if resort.name == resortname:
            return resort
    return None


def find_units_by_resort_name(resortname):
    return data.DictionaryData.units_by_resort_dict[resortname]


def find_unit_by_name(name):
    for unit in data.ResortData.units:
        if unit.typeName == name:
            return unit
    return None


def find_profile_photo_by_resort_name(resortname):
    profile_photos = data.DictionaryData.profile_photo_dict[resortname]
    return get_first_element(profile_photos)


def find_photos_by_resort_name(resortname):
    return data.DictionaryData.photos_by_resort_dict[resortname]


def find_photos_by_unit_type(typename):
    return data.DictionaryData.photos_by_unit_dict[typename]


def find_profile_photo_for_unit_type(typename):
    return data.DictionaryData.photos_by_unit_dict[typename]


def find_profile_photo_by_resort_name(resortname):
    profile_photos = data.DictionaryData.profile_photo_dict[resortname]
    return get_first_element(profile_photos)


def find_photos_by_resort_name(resortname):
    return data.DictionaryData.photos_by_resort_dict[resortname]


def find_photos_by_unit_type(typename):
    return data.DictionaryData.photos_by_unit_dict[typename]


def find_profile_photo_for_unit_type(typename):
    return get_first_element(data.DictionaryData.photos_by_unit_dict[typename])


def find_price_data_for_unit(unitname):
    for price_data in data.ResortData.prices2:
        if price_data.typeName == unitname:
            return price_data
    return None


def find_prices_for_date_range(typename, begin_date, end_date):
    price_data = find_price_data_for_unit(typename)

    if not begin_date:
        if price_data.lowPrice:
            return price_data.lowPrice
        # TODO - throw Error if there is no lowPrice
        else:
            return 150

    if not end_date:
        return find_price_for_date(price_data, begin_date)

    # TODO - calcuate AVG price for date range
    return find_price_for_date(price_data, begin_date)


def find_price_for_date(price_data, date):
    if price_data.promoBeginDate and is_in_range(date, price_data.promoBeginDate, price_data.promoEndDate):
        return price_data.promoPrice
    elif price_data.peakBeginDate1 and is_in_range(date, price_data.peakBeginDate1, price_data.peakEndDate1):
        return price_data.peakPrice1
    elif price_data.peakBeginDate2 and is_in_range(date, price_data.peakBeginDate2, price_data.peakEndDate2):
        return price_data.peakPrice2
    elif price_data.highBeginDate and is_in_range(date, price_data.highBeginDate, price_data.highEndDate):
        return price_data.highPrice
    else:
        return price_data.lowPrice


def is_in_range(date_str, begin_date_str, end_date_str):
    logging.info(convert_string_to_date(begin_date_str))
    logging.info(convert_string_to_date(date_str))
    logging.info(convert_string_to_date(end_date_str))

    if convert_string_to_date(begin_date_str) <= convert_string_to_date(date_str) <= convert_string_to_date(end_date_str):
        return True
    return False


# assume always ISO date
def convert_string_to_date(date_string):
    return datetime.strptime(date_string, '%Y-%m-%d')


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


def serialize_units_summary(units):
    units_json = []
    for unit in units:
        units_json.append(serialize_unit_summary(unit))
    return units_json


def serialize_unit_summary(unit):
    profile_photo = find_profile_photo_for_unit_type(unit.typeName)
    return {
        'unitType': unit.typeName,
        'type': unit.type,
        'displayName': unit.displayName,
        'profilePhoto': build_photo_url_full_1x(profile_photo),
        'maxCapacity': unit.maxCapacity,
        'price': 150,
        }


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


# def serialize_resort_highlight(resort):
#     data = []
#     if resort.wifi == 'Y':
#         data.append('WIFI')
#     if resort.privateBeach == 'Y':
#         data.append('BEACHFRONT')
#     if resort.swimPool == 'Y':
#         data.append('POOL')
#     if resort.lessonKite == 'Y':
#         data.append('KITE')
#     return data


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


def get_mock_desc():
    return "Located just a 40 minute drive south of La Paz on the Sea of Cortez in Baja lies one of Mexico's most beautiful secrets..."


"""
    Serialize Unit Detail
"""
# highlight: type, maxCapacity, numBedroom, numBathroom
# space: type,maxCapacity,bedSetup,numBedroom,numBathroom (privateBath is redundant here)
# amenities: kitchen,kitchenette, ac,patio,seaview
def serialize_unit_detail(unit, begin_date, end_date):
    resort = find_resort_by_name(unit.resortName)
    profile_photo = find_profile_photo_for_unit_type(unit.typeName)
    photos = find_photos_by_unit_type(unit.typeName)
    price = find_prices_for_date_range(unit.typeName, begin_date, end_date)
    return {
        'unitType': unit.typeName,
        'displayName': unit.displayName,
        'profilePhoto': serialize_profile_photo(profile_photo),
        'price': price,
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
    if unit.type == 'CASA' or unit.type == 'CASITA':
        return "Entire home/apt"
    elif unit.type == 'BUNGALOW':
        return 'Standalone bungalow'
    elif unit.type == 'ROOM':
        return 'Room'
        # else:
        #     return 'Unknown'

