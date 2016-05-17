import os
import csv
import logging
from collections import namedtuple
#from collections import defaultdict

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
CSV_PATH = BASE_PATH + '/resorts.csv'
CSV_PATH_UNIT = BASE_PATH + '/units.csv'
CSV_PATH_PHOTO = BASE_PATH + '/photos.csv'
# reader = csv.DictReader(open(BASE_PATH + '/resorts.csv'))

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
fields = ("resortName", "tag", "group", "fileName", "ext", "alt")
class PhotoRecord(namedtuple('PhotoRecord_', fields)):

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


def read_data_photos():
    logging.info('...reading file : loading Photo data........')
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


