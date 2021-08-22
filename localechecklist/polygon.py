import datetime
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import pytz
import requests
from scipy.spatial import ConvexHull
from scipy.spatial.distance import pdist, squareform

ENDPOINT = 'https://nominatim.openstreetmap.org/search/'
SEP = '%20'
TIMEZONE = 'America/New_York'  # 'US/Eastern'
FILE_DATE_FORMAT = '%H_%M_%S-%m_%d_%Y'


def str_timestamp():
    return datetime.datetime.now().replace(tzinfo=pytz.timezone(TIMEZONE)).strftime(FILE_DATE_FORMAT)


def get_city_data(city, state, address_data=True, polygon_svg=True):
    query = f'{SEP}'.join(city.split(' ') + state.split(' '))
    details = []
    if address_data:
        details.append('&address_details=1')
    if polygon_svg:
        details.append('&polygon_svg=1')
    url = ENDPOINT + query + '?format=json' + ''.join(details)
    try:
        results = requests.get(url).json()
        if results[0]['class'] == 'boundary':
            return results[0]
        else:
            log_anomaly(url, results, 'Wrong Search Terms?')
    except Exception as e:
        log_anomaly(url, results, str(e))


def log_anomaly(url, json_data, exception):
    path = os.path.abspath(os.path.join('..', 'logs', 'anomoly_%s.txt' % str_timestamp()))
    with open(path, 'w') as f:
        f.writelines('\n'.join([url, exception] + [json.dumps(d, indent=2)+'\n' for d in json_data]))


data = get_city_data('frederick', 'md')
boundary_str = data['svg']
boundary_list = boundary_str.split(' ')
move = np.array([float(_) for _ in boundary_list[1:3]])
xs = np.array([float(_) for _ in boundary_list[4:-1:2]])
ys = np.array([float(_) for _ in boundary_list[5:-1:2]])

hull_vertices = ConvexHull(np.vstack([xs, ys]).T).vertices
hull_xs = xs[hull_vertices]
hull_ys = ys[hull_vertices]
hull_points = np.vstack([hull_xs, hull_ys]).T

dmat = squareform(pdist(hull_points))
max_dist_points = mdp = list(np.unravel_index(dmat.argmax(), dmat.shape))
wide_points = hull_points[mdp]
center = wide_points.mean(axis=0)
radius = np.linalg.norm(wide_points[0] - center)
circle = plt.Circle(center, radius, color='r', fill=False)

ax = plt.gca()
ax.plot(xs, ys)
ax.plot(hull_xs, hull_ys)
ax.add_patch(circle)
ax.invert_yaxis()
ax.set_aspect('equal', adjustable='box')
plt.show()
