import os
import csv
import logging
from collections import namedtuple

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
# CSV_PATH = BASE_PATH + '/test.csv'
CSV_PATH = BASE_PATH + '/resorts.csv'
# reader = csv.DictReader(open(BASE_PATH + '/resorts.csv'))
# reader = csv.DictReader(open(BASE_PATH + '/test.csv'))

# fields = ("name","category","resortId", "gcalId")
# name,displayName,wifi,parking,communalKitchen,privateBeach,freeBreakfast,noteOnFood,
# lessonKite,rentKite,lessonWindsurf,rentWindsurf,mtnbike,rentPerformanceMtnBike,fishingTrip,scubaDivingTrip,yoga,massage,noteOnActivity,
# checkIn,checkOut,cc,extraPersonCharge,pets,minimumStay,cancelPolicy,profilePhoto,photos

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


def read_data():
    logging.info('........Loading data %s........', CSV_PATH)
    with open(CSV_PATH, 'rU') as data:
        data.readline()            # Skip the header
        reader = csv.reader(data)  # Create a regular tuple reader
        for row in map(ResortRecord.parse, reader):
            #logging.info(row)
            yield row


def find_all_resorts():
    result = []
    for row in read_data():
        result.append(row)
    return result


def find_resort(resortname):
    for row in read_data():
        if row.name == resortname:
            return row
    #return result
    return None


# def serialize_resorts(resorts):
#     resorts_json = []
#     for resort in resorts:
#         resorts_json.append(serialize_resort_summary(resort))
#     return resorts_json


def serialize_resort_summary(resort):
    return {
        'name': resort.name,
        'displayName': resort.displayName,
        'profilePhoto': get_profile_photo(resort.name),
        'beachFront': resort.privateBeach,
        'price': 150,
        'desc': ''
    }


# def serialize_resort_detail(resort, units):
#     return {
#         'name': resort['name'],
#         'displayName': resort['displayName'],
#         # TODO - replace with real!
#         'profilePhoto': get_mock_profile_photo(),
#         'beachFront': resort['privateBeach'],
#         'price': 150,
#         # TODO - replace with real!
#         'desc': get_mock_desc(),
#         'generalSection': serialize_section_general(resort),
#         'foodSection': serialize_section_food(resort),
#         'activitySection': serialize_section_activity(resort),
#         'policySection': serialize_section_policy(resort),
#         'photos': get_mock_photos(),
#         'unitTypes': serialize_units_summary(units)
#     }

def serialize_resort_detail(resort, units):
    if resort is None:
        return {}
    return {
        'name': resort.name,
        'displayName': resort.displayName,
        'profilePhoto': get_mock_profile_photo(),
        'beachFront': resort.privateBeach,
        'price': 150,
        # TODO - replace with real!
        'desc': get_mock_desc(),
        'generalSection': serialize_section_general(resort),
        'foodSection': serialize_section_food(resort),
        'activitySection': serialize_section_activity(resort),
        'policySection': serialize_section_policy(resort),
        'photos': get_mock_photos(),
        #'unitTypes': serialize_units_summary(units)
    }


def serialize_units_summary(units):
    units_json = []
    for unit in units:
        units_json.append(serialize_unit_summary(unit))
    return units_json


def serialize_unit_summary(unit):
    return {
        'displayName': unit['displayName'],
        'profilePhoto': get_mock_unit_profile_photo(),
        'maxCapacity': unit['maxCapacity'],
        'price': 150,
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


def get_profile_photo(resort):

    path = "https://dl.dropboxusercontent.com/u/122147773/gokitebaja/image/Kite%20Baja-"
    if resort == 'bj':
        thumbUrl = path + '4.jpg'
        thumbUrl2x = path + '4.jpg'
        photoUrl = path + '4.jpg'
        photoUrl2x = path + '4.jpg'
    if resort == 'kirk':
        thumbUrl = path + '249.jpg'
        thumbUrl2x = path + '249.jpg'
        photoUrl = path + '249.jpg'
        photoUrl2x = path + '249.jpg'
    if resort == 'dw':
        thumbUrl = path + '158.jpg'
        thumbUrl2x = path + '158.jpg'
        photoUrl = path + '158.jpg'
        photoUrl2x = path + '158.jpg'
    if resort == 'kirt':
        thumbUrl = path + '59.jpg'
        thumbUrl2x = path + '59.jpg'
        photoUrl = path + '59.jpg'
        photoUrl2x = path + '59.jpg'
    # TODO - select correct image
    if resort == 'plp':
        thumbUrl = path + '87.jpg'
        thumbUrl2x = path + '87.jpg'
        photoUrl = path + '87.jpg'
        photoUrl2x = path + '87.jpg'
    if resort == 'pelican':
        thumbUrl = path + '180.jpg'
        thumbUrl2x = path + '180.jpg'
        photoUrl = path + '180.jpg'
        photoUrl2x = path + '180.jpg'
    if resort == 'vp':
        thumbUrl = path + '84.jpg'
        thumbUrl2x = path + '84.jpg'
        photoUrl = path + '84.jpg'
        photoUrl2x = path + '84.jpg'
    if resort == 'vbay':
        thumbUrl = path + '137.jpg'
        thumbUrl2x = path + '137.jpg'
        photoUrl = path + '137.jpg'
        photoUrl2x = path + '137.jpg'
    if resort == 'vwind':
        thumbUrl = path + '59.jpg'
        thumbUrl2x = path + '59.jpg'
        photoUrl = path + '59.jpg'
        photoUrl2x = path + '59.jpg'
    return {
        'thumbUrl': thumbUrl,
        'thumbUrl2x': thumbUrl2x,
        'thumbUrl3x': "",
        'photoUrl': photoUrl,
        'photoUrl2x': photoUrl2x,
        'photoUrl3x': ""
    }

def get_mock_profile_photo():
    # thumbUrl = "https://dl.dropboxusercontent.com/u/122147773/showcase/search-result/thumbnail-sleep-full-01.png"
    # thumbUrl2x = "https://dl.dropboxusercontent.com/u/122147773/showcase/search-result/thumbnail-sleep-full-01@2x.png"
    # thumbUrl3x = ""
    # photoUrl = "https://dl.dropboxusercontent.com/u/122147773/showcase/search-result/header-sleep-full-01.png"
    # photoUrl2x = "https://dl.dropboxusercontent.com/u/122147773/showcase/search-result/header-sleep-full-01@2x.png"
    # photoUrl3x = ""
    path1 = "https://dl.dropboxusercontent.com/u/122147773/gokitebaja/image/Kite%20Baja-"
    path2 = "https://dl.dropboxusercontent.com/u/122147773/gokitebaja/profile-image/Kite%20Baja-"
    thumbUrl = path1 + '142.jpg'
    thumbUrl2x = path1 + '142.jpg'
    photoUrl = path2 + '142.jpg'
    photoUrl2x = path2 + '142.jpg'
    return {
        'thumbUrl': thumbUrl,
        'thumbUrl2x': thumbUrl2x,
        'thumbUrl3x': "",
        'photoUrl': photoUrl,
        'photoUrl2x': photoUrl2x,
        'photoUrl3x': ""
    }

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

def get_mock_photos():

    # https://dl.dropboxusercontent.com/u/122147773/gokitebaja/image/Kite%20Baja-59.jpg
    path = "https://dl.dropboxusercontent.com/u/122147773/gokitebaja/image/Kite%20Baja-"
    url1 = path + "59.jpg"
    url2 = path + "60.jpg"
    url3 = path + "61.jpg"
    url4 = path + "62.jpg"
    url5 = path + "63.jpg"
    url6 = path + "64.jpg"
    url7 = path + "65.jpg"
    url8 = path + "66.jpg"
    url9 = path + "67.jpg"
    url10 = path + "68.jpg"
    return [
        {'url': url1},
        {'url': url2},
        {'url': url3},
        {'url': url4},
        {'url': url5},
        {'url': url6},
        {'url': url7},
        {'url': url8},
        {'url': url9},
        {'url': url10}
    ]


