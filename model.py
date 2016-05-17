import data
import logging

from collections import defaultdict

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
            'price': 150,
            # TODO - replace with real!
            'desc': get_mock_desc(),
            'generalSection': serialize_section_general(resort),
            'foodSection': serialize_section_food(resort),
            'activitySection': serialize_section_activity(resort),
            'policySection': serialize_section_policy(resort),
            'unitTypes': serialize_units_summary(self.units),
            'photos': serialize_photos(self.photos)
        }


class ResortsList(object):
    def __init__(self):
        logging.info("Loading Resorts Data..........................................")
        # load data from file
        self.resorts = data.resorts()
        self.units = data.units()
        self.photos = data.photos()

        # initialize dictionary for units: { resortname, list of UnitRecord }
        logging.info("Loading dictionary for units...")
        self.units_by_resort_dict = self.init_units_by_resort_dict()
        log_dictionary(self.units_by_resort_dict)

        # initialize dictionary for photos : { resortname, list of photos }
        logging.info("Loading dictionary for photos...")
        self.photos_by_resort_dict = self.init_photos_by_resort_dict()
        log_dictionary(self.photos_by_resort_dict)

        # initialize dictionary for profile-photos : { resortname, list of profile-photos }
        logging.info("Loading dictionary for profile-photos...")
        self.profile_photo_dict = self.init_profile_photo_dict()
        log_dictionary(self.profile_photo_dict)

        logging.info("................................ Resorts Data Successfully Loaded")


    def find_all_resorts(self):
        return self.resorts


    def find_resort_by_name(self, resortname):
        for resort in self.resorts:
            if resort.name == resortname:
                return resort
        return None


    def find_units_by_resort_name(self, resortname):
        return self.units_by_resort_dict[resortname]


    def find_profile_photo_by_resort_name(self, resortname):
        profile_photos = self.profile_photo_dict[resortname]
        return get_first_element(profile_photos)


    def find_photos_by_resort_name(self, resortname):
        return self.photos_by_resort_dict[resortname]


    def init_units_by_resort_dict(self):
        units_by_resort = defaultdict(list)
        for unit in self.units:
            if unit.resortName in RESORT_NAME_LIST:
                units_by_resort[unit.resortName].append(unit)
        return units_by_resort


    def init_photos_by_resort_dict(self):
        photos_by_resort = defaultdict(list)
        for photo in self.photos:
            if photo.resortName in RESORT_NAME_LIST:
                # if photo.group value is empty, do not add
                if photo.group:
                    photos_by_resort[photo.resortName].append(photo)
        # now loop thru dictionary (each resort), sort photos by group
        for resort_name, photo_list in photos_by_resort.iteritems():
            photo_list.sort(key=lambda tup: tup[2])
        return photos_by_resort


    def init_profile_photo_dict(self):
        profile_photo_dict = defaultdict(list)
        for photo in self.photos:
            # group is '0' for profile photo
            if (photo.group == '0') and (photo.resortName in RESORT_NAME_LIST):
                profile_photo_dict[photo.resortName].append(photo)
        return profile_photo_dict


    def serialize_resorts(self, resorts):
        json = []
        # resort_instance = Resort()
        for resort in resorts:
            resort_info = ResortInfo(resort)
            # json.append(resortInfo.serialize_resort_summary(resort))
            profile_photo = self.find_profile_photo_by_resort_name(resort.name)
            json.append(resort_info.serialize_resort_summary(resort, profile_photo))
        return json

    def serialize_resort_detail(self, resort):
        return ResortInfo().serialize_resort_detail(resort)



def get_first_element(list):
    return list[0] if list else None


def build_photo_url(file_path, photo):
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
        'photoUrl': build_photo_url_full_1x(photo),
        'alt': photo.alt,
        'group': photo.group
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


def serialize_section_general(resort):
    data = []
    if resort.wifi == 'Y':
        data.append('Free Wifi')
    if resort.parking == 'Y':
        data.append('Free Parking')
    if resort.communalKitchen == 'Y':
        data.append('Communal Kitchen')
    return data


def serialize_section_food(resort):
    data = []
    if resort.freeBreakfast == 'Y':
        data.append('Free Breakfast')
    return data


def serialize_section_activity(resort):
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
    return "Located just a 40 minute drive south of La Paz on the Sea of Cortez in Baja lies one of Mexico's most beautiful secrets..."


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


def log_dictionary(dict):
        for key, value in dict.items():
            logging.info(key)
        logging.info("...... %d dictionary items loaded." % len(dict))

