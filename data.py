import os
import csv
import logging
from collections import namedtuple
from collections import defaultdict

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
CSV_PATH = BASE_PATH + '/resorts.csv'
CSV_PATH_UNIT = BASE_PATH + '/units.csv'
CSV_PATH_PHOTO = BASE_PATH + '/photos.csv'
# reader = csv.DictReader(open(BASE_PATH + '/resorts.csv'))

# resort-names - used as resort ID
RESORT_NAME_LIST = ["bj", "kirk", "dw", "kirt", "plp", "pelican", "vp", "vbay", "vwind"]

# photo file path
PHOTO_PATH = 'https://dl.dropboxusercontent.com/u/122147773/gokitebaja/image/la-ventana-'

# parse instruction for Resort CSV file
fields = ("name", "displayName", "wifi", "parking", "communalKitchen", "privateBeach", "freeBreakfast", "noteOnFood",
          "lessonKite", "rentKite", "lessonWindsurf", "rentWindsurf", "mtnbike", "rentPerformanceMtnBike", "fishingTrip", "scubaDivingTrip",
          "yoga", "massage","noteOnActivity",
          "checkIn", "checkOut", "cc", "extraPersonCharge", "pets", "minimumStay", "cancelPolicy", "profilePhoto", "photos")
class ResortRecord(namedtuple('ResortRecord_', fields)):

    @classmethod
    def parse(klass, row):
        row = list(row)                                # Make row mutable
        # row[2] = int(row[2]) if row[2] else None       # Convert field to an integer
        # row[6] = datetime.strptime(row[6], "%d-%b-%y") # Parse the field
        # row[7] = int(row[7])                           # Convert field to an integer
        return klass(*row)

        # def __str__(self):
        #     date = self.fundedDate.strftime("%d %b, %Y")
        #     return "%s raised %i in round %s on %s" % (self.company, self.raisedAmt, self.round, date)


# parse instruction for Unit CSV file
fields = ("category", "resortName", "displayName", "type", "maxCapacity", "bedSetup",
          "numBedroom", "numBathroom", "kitchen", "kitchenette", "privateBath",
          "ac", "patio", "seaview", "profilePhoto", "photos")
class UnitRecord(namedtuple('UnitRecord_', fields)):

    @classmethod
    def parse(klass, row):
        row = list(row)                                # Make row mutable
        return klass(*row)


# parse instruction for Photo CSV file
fields = ("resortName", "tag", "group",  "alt", "fileName", "ext")
class PhotoRecord(namedtuple('PhotoRecord_', fields)):

    @classmethod
    def parse(klass, row):
        row = list(row)                                # Make row mutable
        return klass(*row)


def read_data_resorts():
    logging.info('loading Resort data........')
    with open(CSV_PATH, 'rU') as data:
        data.readline()            # Skip the header
        reader = csv.reader(data)  # Create a regular tuple reader
        for row in map(ResortRecord.parse, reader):
            # logging.info(row)
            yield row


def read_data_units():
    logging.info('loading Unit data........')
    with open(CSV_PATH_UNIT, 'rU') as data:
        data.readline()            # Skip the header
        reader = csv.reader(data)  # Create a regular tuple reader
        for row in map(UnitRecord.parse, reader):
            yield row


def read_data_photos():
    logging.info('loading Photo data........')
    with open(CSV_PATH_PHOTO, 'rU') as data:
        data.readline()            # Skip the header
        reader = csv.reader(data)  # Create a regular tuple reader
        for row in map(PhotoRecord.parse, reader):
            yield row


def resorts():
    result = []
    for row in read_data_resorts():
        result.append(row)
    return result


def units():
    result = []
    for row in read_data_units():
        result.append(row)
    return result


def photos():
    result = []
    for row in read_data_photos():
        result.append(row)
    return result


def photos_by_resort_dict():
    photos_by_resort = defaultdict(list)
    for photo in photos():
        if photo.resortName in RESORT_NAME_LIST:
            photos_by_resort[photo.resortName].append(photo)
    return photos_by_resort


def profile_photo_dict():
    profile_photo_dict = defaultdict(list)
    for photo in photos():
        # group is '0' for profile photo
        if (photo.group == '0') and (photo.resortName in RESORT_NAME_LIST):
            profile_photo_dict[photo.resortName].append(photo)
    return profile_photo_dict

def get_first_element(list):
    return list[0] if list else None

def build_photo_url(photo):
    if photo.ext:
        url = PHOTO_PATH + photo.fileName + photo.ext
    else:
        url = PHOTO_PATH + photo.fileName + '.jpg'
    return url

def get_profile_photo(resort):
    photos_dict = profile_photo_dict()
    return get_first_element(photos_dict[resort.name])


# def find_resort(resortname):
#     for row in read_data_resorts():
#         if row.name == resortname:
#             return row
#     return None

def find_resort(resorts, resortname):
    for row in resorts:
        if row.name == resortname:
            return row
    return None

# def find_units_by_resort_name(resortname):
#     result = []
#     for row in read_data_units():
#         if row.resortName == resortname:
#             result.append(row)
#     return result

def find_units_by_resort_name(units, resortname):
    result = []
    for row in units:
        if row.resortName == resortname:
            result.append(row)
    return result


def serialize_resort_summary(resort):
    profile_photo = get_profile_photo(resort)
    return {
        'name': resort.name,
        'displayName': resort.displayName,
        # 'profilePhoto': get_profile_photo(resort.name),
        'profilePhoto': serialize_profile_photo(profile_photo),
        'beachFront': resort.privateBeach,
        'price': 150,
        'desc': ''
    }


def serialize_resort_detail(resort, units, photos):
    if resort is None:
        return {}
    profile_photo = get_profile_photo(resort)
    return {
        'name': resort.name,
        'displayName': resort.displayName,
        'profilePhoto': serialize_profile_photo(profile_photo),
        'beachFront': resort.privateBeach,
        'price': 150,
        # TODO - replace with real!
        'desc': get_mock_desc(),
        'generalSection': serialize_section_general(resort),
        'foodSection': serialize_section_food(resort),
        'activitySection': serialize_section_activity(resort),
        'policySection': serialize_section_policy(resort),
        'unitTypes': serialize_units_summary(units),
        'photos': serialize_photos(photos)
    }


def serialize_units_summary(units):
    units_json = []
    for unit in units:
        units_json.append(serialize_unit_summary(unit))
    return units_json


def serialize_unit_summary(unit):
    # print unit
    return {
        'displayName': unit.displayName,
        'profilePhoto': get_mock_unit_profile_photo(),
        'maxCapacity': unit.maxCapacity,
        'price': 150,
        }

def serialize_photos(photos):
    json = []
    for photo in photos:
        json.append(serialize_photo(photo))
    return json


def serialize_photo(photo):
    return {
        # 'resortName': photo.resortName,
        'url': build_photo_url(photo),
        'alt': photo.alt
        }


def serialize_profile_photo(photo):
    if not photo:
        return None
    return {
        'thumbUrl': build_photo_url(photo),
        'thumbUrl2x': build_photo_url(photo),
        'thumbUrl3x': "",
        'photoUrl': build_photo_url(photo),
        'photoUrl2x': build_photo_url(photo),
        'photoUrl3x': ""
    }


def serialize_section_general(resort):
    # return {
    #     'wifi': resort['wifi'],
    #     'parking': resort['parking'],
    #     'communalKitchen': resort['communalKitchen']
    # }
    data = []
    if resort.wifi == 'Y':
        data.append('Free Wifi')
    if resort.parking == 'Y':
        data.append('Free Parking')
    if resort.communalKitchen == 'Y':
        data.append('Communal Kitchen')
    return data

def serialize_section_food(resort):
    # return {
    #     'freeBreakfast': resort['freeBreakfast'],
    #     'noteOnFood': resort['noteOnFood']
    # }
    data = []
    if resort.freeBreakfast == 'Y':
        data.append('Free Breakfast')
    return data

def serialize_section_activity(resort):
    # return {
    #     'lessonKite': resort['lessonKite'],
    #     'rentWindsurf': resort['rentWindsurf'],
    #     'mtnbike': resort['mtnbike'],
    #     'rentPerformanceMtnBike': resort['rentPerformanceMtnBike'],
    #     'fishingTrip': resort['fishingTrip'],
    #     'scubaDivingTrip': resort['scubaDivingTrip'],
    #     'yoga': resort['yoga'],
    #     'massage': resort['massage'],
    #     'otherActivity': resort['noteOnActivity']
    # }
    data = []
    if resort.lessonKite == 'Y':
        data.append('Kiteboarding Lesson')
    if resort.rentKite == 'Y':
        data.append('Kiteboarding Gear Rental')
    if resort.lessonWindsurf == 'Y':
        data.append('Windsurfing Lesson')
    if resort.rentWindsurf == 'Y':
        data.append('Windsurfing Gear Rental')
    if resort.rentPerformanceMtnBike == 'Y':
        data.append('Performance Bike Rental')
    if resort.fishingTrip == 'Y':
        data.append('Fishing Trip')
    if resort.scubaDivingTrip == 'Y':
        data.append('Scuba Diving Trip')
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
    return "Located just a 40 minute drive south of La Paz on the Sea of Cortez in Baja lies one of Mexico's most beautiful secrets... Baja Joe's will show you the way to Paradise!"


def get_mock_unit_profile_photo():
    thumbUrl = "https://dl.dropboxusercontent.com/u/122147773/showcase/search-result/thumbnail-sleep-full-05.png"
    photoUrl = "https://dl.dropboxusercontent.com/u/122147773/showcase/search-result/thumbnail-sleep-full-05.png"
    return {
        'thumbUrl': thumbUrl,
        'thumbUrl2x': "",
        'thumbUrl3x': "",
        'photoUrl': photoUrl,
        'photoUrl2x': "",
        'photoUrl3x': ""
    }



