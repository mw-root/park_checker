import json
import requests
from datetime import date, datetime, timedelta
from enum import Enum
from notifier import push_note

class Park:
    def __init__(self, name, canoe_params, hiking_params, resource_location_id):
        self.name                   = name
        self.resource_location_id   = resource_location_id
        self.canoe                  = canoe_params
        self.hiking                 = hiking_params

class QueryConfigParams:
    def __init__(self, booking_uid, booking_category_id, cart_uid, map_id):
        self.booking_uid            = booking_uid
        self.booking_category_id    = booking_category_id
        self.cart_uid               = cart_uid
        self.map_id                 = map_id

class Parks:
    def __init__(self):
        self.killarney  = Park(
                            name = 'Killarney',
                            resource_location_id = '-2147483601',
                            canoe_params = QueryConfigParams(
                                booking_uid             = '0',
                                booking_category_id     = '4',
                                cart_uid                = '3f106ce0-2557-4c04-ad9c-cde9627a3bf2',
                                map_id                  = '-2147483430'

                            ),
                            hiking_params = QueryConfigParams(
                                booking_uid             = '8',
                                booking_category_id     = '5',
                                cart_uid                = 'f7fc7a3e-ddf1-474b-ab0b-e8a0bd7b63ad',
                                map_id                  = '-2147483429'
                            )
                        )
        self.algonquin  = Park(
                            name = 'Alongquin',
                            resource_location_id = '-2147483644',
                            canoe_params = QueryConfigParams(
                                booking_uid             = 'b',
                                booking_category_id     = '4',
                                cart_uid                = 'a49459c0-c914-4586-927e-fbb6881588ea',
                                map_id                  = '-2147483635'
                            ),
                            hiking_params = None
                        )        

parks = Parks()

class SiteType(Enum):
    canoe = 'canoe'
    hiking = 'hiking'

class Lake:
    def __init__(self, name, park, site_type, id):
        self.name       = name
        self.park       = park
        self.site_type  = site_type
        self.id         = id

class Lakes:
    def __init__(self):
        self.boundary_lake      = Lake('Boundary Lake',         parks.killarney, SiteType.canoe,  -2147475324)
        self.balsam_lake        = Lake('Balsam Lake',           parks.killarney, SiteType.canoe,  -2147475143)
        self.bell_lake          = Lake('Bell/Three Mile Lakes', parks.killarney, SiteType.canoe,  -2147475336)
        self.david_lake         = Lake('David Lake',            parks.killarney, SiteType.canoe,  -2147475333)
        self.fox_deacon_lake    = Lake('Fox/Deacon Lake',       parks.killarney, SiteType.canoe,  -2147475175)
        self.grey_lake          = Lake('Grey Lake',             parks.killarney, SiteType.canoe,  -2147475179)
        self.harry_lake         = Lake('Harry Lake',            parks.killarney, SiteType.canoe,  -2147475207)
        self.johnnie_lake       = Lake('Johnnie Lake',          parks.killarney, SiteType.canoe,  -2147475294)
        self.little_bell_lake   = Lake('Little Bell Lake',      parks.killarney, SiteType.canoe,  -2147475285)
        self.topaz_lake         = Lake('Topaz Lake',            parks.killarney, SiteType.hiking, -2147475348)
        self.big_thunder_lake   = Lake('Big Thunder',           parks.algonquin, SiteType.canoe,  -2147482892)

availability_by_date = {}

def get_availability_by_date(d, lake):

    key = f'''{lake.park.name.upper()}_{lake.site_type.name.upper()}_{d.strftime('%Y_%m_%d')}'''
    
    try:
        return(availability_by_date[key])
    except KeyError:
        pass
    
    availability_by_date[key] = query_park_availability(d, lake)

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

        availabilities = get_availability_by_date(d, lake)
        
        a = availabilities[str(lake.id)]
        if a[0]['availability'] == 0:
            msgs.append(
                f'{lake.name} in {lake.park.name.capitalize()} is available on {d.isoformat()}'
            )
    
    for msg in msgs:
        print(msg)

    push_note('\n'.join(msgs), 'Lake Availability Note!')

def query_park_availability(d, lake):

    url = get_url_for_date(d, lake)
    #print(url)
    r = requests.get(url)

    availabilities = r.json()['resourceAvailabilities']

    return(availabilities)

def get_url_for_date(d, lake):
    seed = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.000Z')

    park_params     = lake.park
    query_params    = getattr(lake.park, lake.site_type.name)
    
    return(
           'https://reservations.ontarioparks.com/api/availability/'
        f'''map?mapId={query_params.map_id}'''
        f'''&bookingCategoryId={query_params.booking_category_id}'''
        f'''&resourceLocationId={park_params.resource_location_id}'''
           '&equipmentCategoryId=null'
           '&subEquipmentCategoryId=null'
        f'''&cartUid={query_params.cart_uid}'''
        f'''&bookingUid={query_params.booking_uid}'''
        f'''&startDate={d.isoformat()}&endDate={(d + timedelta(days = 1)).isoformat()}'''
           '&getDailyAvailability=false&isReserving=true&filterData=%5B%5D&boatLength=null&boatDraft=null&boatWidth=null&partySize=1'
        f'''&seed={seed}'''
    )

if __name__ == '__main__':
    main()