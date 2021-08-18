import csv
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

def add_point(point):
    list_point = json.loads(point)
    print(type(list_point))
    list_point = [list_point['x'], list_point['y'], list_point['z']]
    if os.path.exists('out.csv'):
        with open('out.csv', 'a') as fd:
            writer = csv.writer(fd)
            writer.writerow(list_point)
    else:
        with open('out.csv', 'w') as fd:
            writer = csv.writer(fd)
            writer.writerow(['x', 'y', 'z'])
            writer.writerow(list_point)

    print(list_point)
    return 'Added'
    # df_point.to_csv('out.csv', header=['x', 'y', 'z'], index=False)


def zeroing():
    if os.path.exists("out.csv"):
        os.remove("out.csv")
    if os.path.exists("current_config.json"):
        os.remove("current_config.json")


# zeroing()
# add_point('{"x": 1, "y": 2, "z": 3}')
# print('q')

# [{"x": 15, "y": 2, "z": 3},{"x": 15, "y": 2, "z": 3}]
def add_layer(layer_config, json_of_points=''):
    # name type
    if json_of_points != '':
        print(len(json.loads(json_of_points)))
        for point in json.loads(json_of_points):
            print(point)
            add_point(json.dumps(point))
    if os.path.exists('out.csv'):
        df = pd.read_csv('out.csv')

    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.x, df.y))

    with open('layer.json') as f:
        layer_style = f.read()
    layer_config = json.loads(layer_config)
    print(layer_style)
    style = json.loads(layer_style)
    style["config"]["dataId"] = layer_config['name']
    style["type"] = layer_config['type']

    layer_style = json.dumps(style)
    Visualize(gdf, names=[layer_config['name']], api_key=MAPBOX_API_KEY, layer=layer_style)
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

    df = pd.read_csv('rome.csv')

    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.x, df.y))
    with open('layer.json') as f:
        layer_style = f.read()
    style = json.loads(layer_style)
    data_name = style["config"]["dataId"]
    # Visualize one or multiple objects at a time
    Visualize(gdf, names=[data_name], api_key=MAPBOX_API_KEY, layer=layer_style)
    return "Success"
# html_path = vis.render(open_browser=True, read_only=False)
# bounds_layer((12.55, 41.95, 12.65, 42))
