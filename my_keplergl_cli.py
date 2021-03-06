import json
import os
import tempfile
import webbrowser

import geojson
import shapely.geometry
from keplergl import KeplerGl
from pkg_resources import resource_filename
from shapely.geometry import mapping

SHAPELY_GEOJSON_CLASSES = [
    shapely.geometry.LineString,
    shapely.geometry.LinearRing,
    shapely.geometry.MultiLineString,
    shapely.geometry.MultiPoint,
    shapely.geometry.MultiPolygon,
    shapely.geometry.Point,
    shapely.geometry.Polygon,
    geojson.Feature,
    geojson.FeatureCollection,
    geojson.GeoJSON,
    geojson.GeoJSONEncoder,
    geojson.GeometryCollection,
    geojson.LineString,
    geojson.MultiLineString,
    geojson.MultiPoint,
    geojson.MultiPolygon,
    geojson.Point,
    geojson.Polygon
]  # yapf: disable


class Visualize:
    """Quickly visualize data in browser over Mapbox tiles with the help of the AMAZING kepler.gl.
    """

    def __init__(
            self,
            data=None,
            names=None,
            read_only=False,
            api_key=None,
            ):
        """Visualize data using kepler.gl

        Args:
            data Optional[Union[List[]]]:
                either None, a List of data objects, or a single data object. If
                data is not None, then Visualize(data) will perform all steps,
                including rendering and opening a browser.
        """
        super(Visualize, self).__init__()

        if api_key is not None:
            self.MAPBOX_API_KEY = api_key
        else:
            self.MAPBOX_API_KEY = os.getenv('MAPBOX_API_KEY')
            msg = 'Warning: api_key not provided and MAPBOX_API_KEY '
            msg += 'environment variable not set.\nMap may not display.'
            if self.MAPBOX_API_KEY is None:
                print(msg)

        config = self.config()
        self.map = KeplerGl(config=config)

        if data is not None:
            self.add_data(data=data, names=names)
        self.html_path = self.render(read_only=read_only)

    def config(self, style=None, layer=None):
        """Load kepler.gl config and insert Mapbox API Key"""

        # config_file = resource_filename('keplergl_config.json')

        # First load config file as string, replace {MAPBOX_API_KEY} with the
        # actual api key, then parse as JSON
        if os.path.exists('current_config.json'):
            with open('current_config.json') as f:
                text = f.read()
        else:

            with open('keplergl_config.json') as f:
                text = f.read()

        text = text.replace('{MAPBOX_API_KEY}', self.MAPBOX_API_KEY)
        keplergl_config = json.loads(text)



        # If style_url is not None, replace existing value

        # Remove map state in the hope that it'll auto-center based on data
        #keplergl_config['config']['config'].pop('mapState')
        return keplergl_config['config']

    def add_data(self, data, names=None):
        """Add data to kepler map

        Data should be either GeoJSON or GeoDataFrame. Kepler isn't aware of the
        geojson or shapely package, so if I supply an object from one of these
        libraries, first convert it to a GeoJSON dict.
        """
        # Make `data` iterable
        if not isinstance(data, list):
            data = [data]

        # Make `names` iterable and of the same length as `data`
        if isinstance(names, list):
            # Already iterable, make sure they're the same length
            msg = 'data and names are iterables of different length'
            assert len(data) == len(names), msg
        else:
            # `names` not iterable, make sure it's the same length as `data`
            if names is None:
                name_stub = 'data'
                names = [f'{name_stub}_{x}' for x in range(len(data))]

        for datum, name in zip(data, names):
            if any(isinstance(datum, c) for c in SHAPELY_GEOJSON_CLASSES):
                datum = dict(mapping(datum))

            self.map.add_data(data=datum, name=name)



    def render(self, open_browser=False, read_only=False):
        """Export kepler.gl map to HTML file and open in Chrome
        """
        # Generate path to a temporary file

        path = os.path.join(os.getcwd(),'swagger','templates', 'vis.html')
        if os.path.exists(path):
            os.remove(path)
        self.map.save_to_html(file_name=path, read_only=read_only)

        # Open saved HTML file in new tab in default browser
        if open_browser:
            webbrowser.open_new_tab('file://' + path)

        return path
