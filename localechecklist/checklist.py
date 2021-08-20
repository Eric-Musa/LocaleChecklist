import googlemaps
import json
import os
import sqlite3


KEYS = [
    'name',
    'types',
    'rating',
    'user_ratings_total',
    'business_status',
    'formatted_address',
    'geometry',
    'plus_code',
    'place_id',
]


MILES_TO_METERS = 1600
NA = 'N/A'
SEP = '|'


def get_important_data(element, keys=KEYS):
    important_data = {k: element.get(k, NA) for k in keys}
    if (id := important_data.get('geometry', NA)) != NA:
        important_data['geometry'] = f'%s{SEP}%s' % (id['location']['lat'], id['location']['lng'])
    else:
        important_data['geometry'] = f'{NA}{SEP}{NA}'
    
    if (id := important_data.get('plus_code', NA)) != NA:
        important_data['plus_code'] = f'%s{SEP}%s' % (id['compound_code'], id['global_code'])
    else:
        important_data['plus_code'] = f'{NA}{SEP}{NA}'
    
    if (id := important_data.get('types', NA)) != NA:
        important_data['types'] = f'{SEP}'.join(id)
    else:
        important_data['types'] = f'{NA}'
    return important_data


class Places:

    def __init__(self):
        self.client = googlemaps.Client(key=os.environ.get('API_KEY'))

    def request_place(self, query='restaurant', location='Frederick, MD', radius=0.1, **kwargs):
        m_radius = radius * MILES_TO_METERS
        data = self.client.places(query=query, location=location, radius=m_radius)['results']
        # return [get_important_data(d) for d in data] if format else data
        return data


places = Places()


places_data = places.request_place()
item = places_data[0]
# print(json.dumps(item, indent=2))


DEBUG_DB = False
DB_NAME = os.path.join(os.getcwd(), '..', 'locale_database.db')

if DEBUG_DB:
    os.remove(DB_NAME)
con = sqlite3.connect(DB_NAME)

TABLE_NAME = 'places'
columns = ' text, '.join(KEYS)
columns = columns.replace('name text', 'name text PRIMARY KEY')

cur = con.cursor()
cur.execute(f'''CREATE TABLE IF NOT EXISTS {TABLE_NAME} ({columns})''')


def add_data_to_db(data):
    values_template = ", ".join(["?" for _ in range(len(KEYS))])

    table_data = [tuple(get_important_data(d).values()) for d in data]

    cur.executemany(f'''insert into {TABLE_NAME} values ({values_template})''', table_data)


add_data_to_db(places_data)
