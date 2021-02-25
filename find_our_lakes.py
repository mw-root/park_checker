import json
import requests
from datetime import date, datetime, timedelta
from enum import Enum
from notifier import push_note

class Parks(Enum):
    KILLARNEY = 1
    KILLARNEY_HIKE = 2
    ALGONQUIN = 3

class Lake:
    def __init__(self, name, park, id):
        self.name   = name
        self.park   = park
        self.id     = id

class Lakes:
    def __init__(self):
        self.boundary_lake      = Lake('Boundary Lake',         Parks.KILLARNEY,        -2147475324)
        self.balsam_lake        = Lake('Balsam Lake',           Parks.KILLARNEY,        -2147475143)
        self.bell_lake          = Lake('Bell/Three Mile Lakes', Parks.KILLARNEY,        -2147475336)
        self.david_lake         = Lake('David Lake',            Parks.KILLARNEY,        -2147475333)
        self.fox_deacon_lake    = Lake('Fox/Deacon Lake',       Parks.KILLARNEY,        -2147475175)
        self.grey_lake          = Lake('Grey Lake',             Parks.KILLARNEY,        -2147475179)
        self.harry_lake         = Lake('Harry Lake',            Parks.KILLARNEY,        -2147475207)
        self.johnnie_lake       = Lake('Johnnie Lake',          Parks.KILLARNEY,        -2147475294)
        self.little_bell_lake   = Lake('Little Bell Lake',      Parks.KILLARNEY,        -2147475285)
        self.topaz_lake         = Lake('Topaz Lake',            Parks.KILLARNEY_HIKE,   -2147475348)
        self.big_thunder_lake   = Lake('Big Thunder',           Parks.ALGONQUIN,        -2147482892)

availability_by_date = {}

def get_availability_by_date(d, park):

    key = f'''{park.name}_{d.strftime('%Y_%m_%d')}'''
    
    try:
        return(availability_by_date[key])
    except KeyError:
        pass
    
    availability_by_date[key] = query_park_availability(d, park)

    return(availability_by_date[key])

def main():
    
    lakes = Lakes()

    site_list = [
        { 'date': date(2021, 7, 25), 'lake': lakes.topaz_lake },
        { 'date': date(2021, 7, 26), 'lake': lakes.topaz_lake },
        { 'date': date(2021, 7, 25), 'lake': lakes.grey_lake },
        { 'date': date(2021, 7, 25), 'lake': lakes.johnnie_lake },
        { 'date': date(2021, 7, 26), 'lake': lakes.grey_lake },
        { 'date': date(2021, 7, 26), 'lake': lakes.johnnie_lake },
        { 'date': date(2021, 7, 27), 'lake': lakes.boundary_lake },
        { 'date': date(2021, 7, 27), 'lake': lakes.david_lake },
        { 'date': date(2021, 7, 28), 'lake': lakes.boundary_lake },
        { 'date': date(2021, 7, 28), 'lake': lakes.david_lake },
        { 'date': date(2021, 7, 29), 'lake': lakes.fox_deacon_lake },
        { 'date': date(2021, 7, 29), 'lake': lakes.harry_lake },
        { 'date': date(2021, 7, 30), 'lake': lakes.fox_deacon_lake },
        { 'date': date(2021, 7, 30), 'lake': lakes.harry_lake },
        { 'date': date(2021, 7, 31), 'lake': lakes.little_bell_lake },
        { 'date': date(2021, 7, 31), 'lake': lakes.bell_lake },
        { 'date': date(2021, 7, 31), 'lake': lakes.balsam_lake },
    ]
    msgs = []
    for site in site_list:
        d = site['date']
        lake = site['lake']

        availabilities = get_availability_by_date(d, lake.park)
        
        a = availabilities[str(lake.id)]
        if a[0]['availability'] == 0:
            msgs.append(
                f'{lake.name} in {lake.park.name.capitalize()} is available on {d.isoformat()}'
            )
    
    for msg in msgs:
        print(msg)

    push_note('\n'.join(msgs), 'Lake Availability Note!')

def query_park_availability(d, park):

    url = get_url_for_date(d, park)
    #print(url)
    r = requests.get(url)

    availabilities = r.json()['resourceAvailabilities']

    return(availabilities)

def get_url_for_date(d, park):
    seed = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')

    booking_config = {
        'KILLARNEY': {
            'booking_uid':          '0',
            'booking_category_id':  '4',
            'cart_uid':             '3f106ce0-2557-4c04-ad9c-cde9627a3bf2',
            'map_id':               '-2147483430',
            'resource_location_id': '-2147483601'
        },
        'KILLARNEY_HIKE': {
            'booking_uid':          '8',
            'booking_category_id':  '5',
            'cart_uid':             'f7fc7a3e-ddf1-474b-ab0b-e8a0bd7b63ad',
            'map_id':               '-2147483429',
            'resource_location_id': '-2147483601'
        },
        'ALGONQUIN': {
            'booking_uid':          'b',
            'booking_category_id':  '4',
            'cart_uid':             'a49459c0-c914-4586-927e-fbb6881588ea',
            'resource_location_id': '-2147483644',
            'map_id':               '-2147483635'
        }
    }

    return(
           'https://reservations.ontarioparks.com/api/availability/'
        f'''map?mapId={booking_config[park.name]['map_id']}'''
        f'''&bookingCategoryId={booking_config[park.name]['booking_category_id']}'''
        f'''&resourceLocationId={booking_config[park.name]['resource_location_id']}'''
           '&equipmentCategoryId=null'
           '&subEquipmentCategoryId=null'
        f'''&cartUid={booking_config[park.name]['cart_uid']}'''
        f'''&bookingUid={booking_config[park.name]['booking_uid']}'''
        f'''&startDate={d.isoformat()}&endDate={(d + timedelta(days = 1)).isoformat()}'''
           '&getDailyAvailability=false&isReserving=true&filterData=%5B%5D&boatLength=null&boatDraft=null&boatWidth=null&partySize=1'
        f'''&seed={seed}'''
    )

if __name__ == '__main__':
    main()    


