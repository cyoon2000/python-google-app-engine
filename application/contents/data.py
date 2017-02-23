import os
import csv
import logging
from collections import namedtuple
from collections import defaultdict

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
CSV_PATH = BASE_PATH + '/csv/resorts.csv'
CSV_PATH_UNIT = BASE_PATH + '/csv/units.csv'
CSV_PATH_UNITNAME = BASE_PATH + '/csv/unitnames.csv'
CSV_PATH_PHOTO = BASE_PATH + '/csv/photos.csv'
CSV_PATH_PRICE = BASE_PATH + '/csv/prices.csv'
#CSV_PATH_PRICE2 = BASE_PATH + '/csv/prices2.csv'
# reader = csv.DictReader(open(BASE_PATH + '/resorts.csv'))

# resort-names - used as resort ID
RESORT_NAME_LIST = ["bj", "kirk", "dw", "kurt", "plp", "pelican", "vp", "vbay", "vwind"]

# parse instruction for Resort CSV file
fields = ("name", "displayName", "seoName", "email", "wifi", "parking", "communalKitchen", "privateBeach", "freeBreakfast", "noteOnFood",
          "swimPool", "lessonKite", "rentKite", "lessonWindsurf", "rentWindsurf", "mtnbike", "rentPerformanceMtnBike",
          "fishingTrip", "scubaDivingTrip", "yoga", "massage","noteOnActivity",
          "checkIn", "checkOut", "cc", "extraPersonCharge", "pets", "minimumStay", "cancelPolicy", "about")
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
fields = ("typeName", "resortName", "displayName", "type", "maxCapacity", "bedSetup",
          "numBedroom", "numBathroom", "kitchen", "kitchenette", "privateBath",
          "ac", "patio", "seaview", "notes")
class UnitRecord(namedtuple('UnitRecord_', fields)):

    @classmethod
    def parse(klass, row):
        row = list(row)                                # Make row mutable
        return klass(*row)


# parse instruction for Unit CSV file
fields = ("name", "displayName", "groupName", "gcalId")
class UnitNameRecord(namedtuple('UnitNameRecord_', fields)):

    @classmethod
    def parse(klass, row):
        row = list(row)                                # Make row mutable
        return klass(*row)


# parse instruction for Photo CSV file
fields = ("fileName", "resortName", "unitType", "group", "unitGroup", "tag", "ext", "alt")
class PhotoRecord(namedtuple('PhotoRecord_', fields)):

    @classmethod
    def parse(klass, row):
        row = list(row)                                # Make row mutable
        return klass(*row)


# parse instruction for Price CSV file
#typeName	resortName	peakBeginDate1	peakEndDate1	peakPrice1	peakBeginDate2	peakEndDate2	peakPrice2
# highBeginDate	highEndDate	highPrice	lowBeginDate	lowEndDate	lowPrice	promoBeginDate	promoEndDate	promoPrice
fields = ("typeName", "resortName", "peakBeginDate1", "peakEndDate1", "peakPrice1", "peakBeginDate2", "peakEndDate2", "peakPrice2", "highBeginDate", "highEndDate", "highPrice", "lowBeginDate", "lowEndDate", "lowPrice", "promoBeginDate", "promoEndDate", "promoPrice", "highBeginDate2", "highEndDate2", "highPrice2")
class PriceRecord(namedtuple('PriceRecord_', fields)):

    @classmethod
    def parse(klass, row):
        row = list(row)                                # Make row mutable
        return klass(*row)


def read_data_resorts():
    logging.info('...reading file : loading Resort data........')
    with open(CSV_PATH, 'rU') as data:
        data.readline()            # Skip the header
        reader = csv.reader(data)  # Create a regular tuple reader
        for row in map(ResortRecord.parse, reader):
            # logging.info(row)
            yield row


def read_data_units():
    logging.info('...reading file : loading Unit data........')
    with open(CSV_PATH_UNIT, 'rU') as data:
        data.readline()            # Skip the header
        reader = csv.reader(data)  # Create a regular tuple reader
        for row in map(UnitRecord.parse, reader):
            yield row


def read_data_unitnames():
    logging.info('...reading file : loading UnitName data........')
    with open(CSV_PATH_UNITNAME, 'rU') as data:
        data.readline()            # Skip the header
        reader = csv.reader(data)  # Create a regular tuple reader
        for row in map(UnitNameRecord.parse, reader):
            yield row


def read_data_photos():
    logging.info('...reading file : loading Photo data........')
    with open(CSV_PATH_PHOTO, 'rU') as data:
        data.readline()            # Skip the header
        reader = csv.reader(data)  # Create a regular tuple reader
        for row in map(PhotoRecord.parse, reader):
            yield row

def read_data_prices():
    logging.info('...reading file : loading Price data........')
    with open(CSV_PATH_PRICE, 'rU') as data:
        data.readline()            # Skip the header
        reader = csv.reader(data)  # Create a regular tuple reader
        for row in map(PriceRecord.parse, reader):
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


def prices():
    result = []
    for row in read_data_prices():
        result.append(row)
    return result


class ResortData():
    logging.info("Loading Resorts Data..........................................")
    resorts = resorts()
    units = units()
    photos = photos()
    prices = prices()
    logging.info("..................................Finished loading Resorts Data.")


def log_dictionary(dict):
    for key, value in dict.items():
        logging.info(key)
    logging.info("...... %d dictionary items loaded." % len(dict))


# populate dictionary (key = resortname, value = UnitRecord)
def units_by_resort_dict():
    logging.info("Loading dictionary for units...")
    units_by_resort = defaultdict(list)
    for unit in ResortData.units:
        if unit.resortName in RESORT_NAME_LIST:
            units_by_resort[unit.resortName].append(unit)

    log_dictionary(units_by_resort)
    return units_by_resort


# populate dictionary (key = resortname, value = PhotoRecord)
def photos_by_resort_dict():
    logging.info("Loading dictionary for photos of resort...")
    photos_by_resort = defaultdict(list)
    for photo in ResortData.photos:
        if photo.resortName in RESORT_NAME_LIST:
            # if photo.group value is empty, do not add
            if photo.group:
                photos_by_resort[photo.resortName].append(photo)

    # sort photos by 'group'
    for resort_name, photo_list in photos_by_resort.iteritems():
        photo_list.sort(key=lambda tup: tup[3])

    log_dictionary(photos_by_resort)
    return photos_by_resort


# populate dictionary  (key = resortName, value = PhotoRecord)
def profile_photo_dict():
    logging.info("Loading dictionary for profile-photos...")
    profile_photo_dict = defaultdict(list)
    for photo in ResortData.photos:
        # group is '0' for profile photo
        if (photo.group == '0') and (photo.resortName in RESORT_NAME_LIST):
            profile_photo_dict[photo.resortName].append(photo)

    log_dictionary(profile_photo_dict)
    return profile_photo_dict


# populate dictionary (key = typeName, value = PhotoRecord)
def photos_by_unit_dict():
    logging.info("Loading dictionary for photos of unit types..")
    photos_by_unit = defaultdict(list)
    for photo in ResortData.photos:
        # TODO - add validation
        # if photo.unitType in units():
            # do not add if unitGroup is empty
            if photo.unitGroup:
                photos_by_unit[photo.unitType].append(photo)

    # sort photos by 'unitGroup'
    # first photo is profile photo for the unit type
    for unit_name, photo_list in photos_by_unit.iteritems():
        photo_list.sort(key=lambda tup: tup[4])

    log_dictionary(photos_by_unit)
    return photos_by_unit


class DictionaryData():
    logging.info("Loading Dictionary Data..........................................")
    units_by_resort_dict = units_by_resort_dict()
    photos_by_resort_dict = photos_by_resort_dict()
    profile_photo_dict = profile_photo_dict()
    photos_by_unit_dict = photos_by_unit_dict()
    logging.info("..................................Finished loading Dictionary Data.")



