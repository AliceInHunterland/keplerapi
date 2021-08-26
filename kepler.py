import csv
import glob
import json
import elevation
import os
import geopandas as gpd
from raster2xyz.raster2xyz import Raster2xyz
import pandas as pd
from my_keplergl_cli import Visualize

MAPBOX_API_KEY = 'pk.eyJ1IjoiZWt0bGFncmFuemgxIiwiYSI6ImNrczZkd3EwbzAwczkycW96b3ZpbGJuaTMifQ.hVA0mIakF4asjiJmh7gPEA'

df = pd.DataFrame(
    {'City': ['Buenos Aires', 'Brasilia', 'Santiago', 'Bogota', 'Caracas'],
     'Country': ['Argentina', 'Brazil', 'Chile', 'Colombia', 'Venezuela'],
     'Latitude': [-34.58, -15.78, -33.45, 4.60, 10.48],
     'Longitude': [-58.66, -47.91, -70.66, -74.08, -66.86]})


# Create your geospatial objects

def add_point(point, file_name):
    list_point = json.loads(point)
    print(list_point)
    colomns = []
    vals = []
    for item in list_point:
        print(list_point[item])
        colomns.append(item)
        vals.append(list_point[item])
    if os.path.exists(file_name + '.csv'):
        with open(file_name + '.csv', 'a') as fd:
            writer = csv.writer(fd)
            writer.writerow(vals)
    else:
        with open(file_name + '.csv', 'w') as fd:
            writer = csv.writer(fd)
            writer.writerow(colomns)
            writer.writerow(vals)

    print(list_point)
    return 'Added'


def zeroing():
    result = glob.glob('*.{}'.format('csv'))
    print(result)
    for file in result:
        os.remove(file)
    if os.path.exists("current_config.json"):
        os.remove("current_config.json")
    Visualize(api_key=MAPBOX_API_KEY)


def add_layer(layer_config, json_of_points=None):
    # name type
    with open('layer.json') as f:
        layer_style = f.read()

    layer_config = json.loads(layer_config)

    if json_of_points is not None:

        for point in json.loads(json_of_points):
            add_point(json.dumps(point), layer_config['data_name'])

    style = json.loads(layer_style)
    style["config"]["dataId"] = layer_config['data_name']
    style["config"]["label"] = layer_config['layer_name']
    style["type"] = layer_config['type']
    if os.path.exists('current_config.json'):
        with open('current_config.json') as f:
            text = f.read()
        keplergl_config = json.loads(text)
        for item, layer in enumerate(keplergl_config['config']['config']['visState']["layers"]):

            if layer["config"]["label"] == layer_config['layer_name']:
                print(layer["config"]["label"])
                keplergl_config['config']['config']['visState']["layers"].pop(item)

    else:

        with open('keplergl_config.json') as f:
            text = f.read()
            keplergl_config = json.loads(text)

    print(len(keplergl_config['config']['config']['visState']["layers"]))
    style["id"] = len(keplergl_config['config']['config']['visState']["layers"])
    keplergl_config['config']['config']['visState']["layers"].append(style)

    prepared_data = []
    names_data = []
    for layer in keplergl_config['config']['config']['visState']["layers"]:

        if os.path.exists(layer["config"]["dataId"] + '.csv'):
            df = pd.read_csv(layer["config"]["dataId"] + '.csv')
            gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.x, df.y))
            prepared_data.append(gdf)
            names_data.append(layer["config"]["dataId"])

    with open('current_config.json', 'w') as f:
        f.write(json.dumps(keplergl_config))
    Visualize(prepared_data, names=names_data, api_key=MAPBOX_API_KEY)
    return 'Success'


def bounds_layer(bound):
    # bounds=(12.55, 41.95, 12.65, 42)
    print(type(bound))
    elevation.clip(bounds=bound, output=os.path.join(os.path.abspath(os.getcwd()), 'rome.tif'))

    print('sssss')
    input_raster = './rome.tif'
    output_csv = './rome.csv'

    rtxyz = Raster2xyz()
    rtxyz.translate(input_raster, output_csv)

    add_layer(json.dumps({'data_name': 'rome', 'type': 'point', 'layer_name': 'bounds'}))
    return "Success"


def add_filter(data_name):
    if os.path.exists('current_config.json'):
        with open('current_config.json') as f:
            text = f.read()
    else:

        with open('keplergl_config.json') as f:
            text = f.read()

    keplergl_config = json.loads(text)
    keplergl_config['config']['config']['visState']['filters'][0]['dataId'] = data_name
    print(keplergl_config)
    with open('current_config.json', 'w') as f:
        f.write(json.dumps(keplergl_config))
    # for layer in keplergl_config['config']['config']['visState']["layers"]:
    #
    #     if layer["config"]["dataId"] == data_name:
    #         layer_name = layer["config"]["label"]
    add_layer(json.dumps({'data_name': data_name, 'type': 'point', 'layer_name':"filter"}))

    # Visualize(api_key=MAPBOX_API_KEY)


# add_filter('qw2')

# delete all csv and temp files
#zeroing()

# Adding point into test.csv
# add_point('{"x": 1, "y": 2, "z": 3}', 'test')

# Adding layer with data from qw1.csv, tipe of data can be point,.(i foggot)... and name of layer -first
# add_layer(json.dumps({'data_name': 'qw1', 'type': 'point', 'layer_name': 'first'}),
#          json.dumps([{"x": 1, "y": 2, "z": 3}, {"x": 2, "y": 1, "z": 3}]))
# add_layer(json.dumps({'data_name': 'qw2', 'type': 'point', 'layer_name': 'vtoroi'}),
#           json.dumps([{"x": 3, "y": 2, "z": 3}, {"x": 2, "y": 3, "z": 3}]))
# add_point(json.dumps({"x": 2, "y": 2, "z": 3}), 'qw2')
# add_point(json.dumps({"x": 2, "y": 2, "z": 3,'datatime':4444}), 'qw1')
# add_point(json.dumps({"x": 2, "y": 2, "z": 3,'datatime':4444}), 'qw2')
# #
# add_layer(json.dumps({'data_name': 'qw2', 'type': 'point', 'layer_name': '1'}))
#
# add_filter('qw2')
# html_path = vis.render(open_browser=True, read_only=False)

# Adding layer with points from the square
# bounds_layer((9.89, 41.89, 10, 42))
