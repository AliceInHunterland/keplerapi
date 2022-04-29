import json
import os
import cv2
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask import Flask, jsonify, render_template, send_from_directory, request, redirect, url_for
from marshmallow import Schema, fields
import kepler
from werkzeug.utils import secure_filename
from ast import literal_eval as make_tuple
import requests

# from pyproj import Proj, transform

# P3857 = Proj(init='epsg:3857')
# P4326 = Proj(init='epsg:4326')


app = Flask(__name__, template_folder='swagger/templates')
app.config['UPLOAD_FOLDER'] = './uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/main')
def home():
    print('ssssssssss')
    return render_template('vis.html')


spec = APISpec(
    title='biogeohab-swagger-doc',
    version='1.0.0',
    openapi_version='3.0.2',
    plugins=[FlaskPlugin(), MarshmallowPlugin()]
)


@app.route('/api/swagger.json')
def create_swagger_spec():
    return jsonify(spec.to_dict())


class TodoResponseSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    status = fields.Boolean()
    x = fields.Float()
    y = fields.Float()
    z = fields.Float()


class TodoListResponseSchema(Schema):
    todo_list = fields.List(fields.Nested(TodoResponseSchema))


@app.route('/todo')
def todo():
    """Get List of Todo
    ---
    get:
        description: Get List of Todos
        responses:
            200:
                description: Return a todo list
                content:
                    application/json:
                        schema: TodoListResponseSchema
    """

    dummy_data = [{
        'id': 1,
        'title': 'Finish this task',
        'status': False
    }, {
        'id': 2,
        'title': 'Finish that task',
        'status': True
    }]

    return TodoListResponseSchema().dump({'todo_list': dummy_data})


class PointParameter(Schema):
    point = fields.Str()
    data_name = fields.Str()


class PointSchema(Schema):
    status = fields.Str()
    point = fields.Str()


@app.route('/add_point', methods=['POST'])
def add_point():
    """Post one Point
    ---
    post:
        description: Post One Point example
        parameters:
          - in: query
            schema: PointParameter

        responses:
            200:
                description: Return status
                content:
                    application/json:
                        schema: PointSchema
    """

    point = request.args.get('point')
    data_name = request.args.get('data_name')
    print(point)
    print(type(point))
    res = kepler.add_point(point, data_name)
    return jsonify(status=res), 200


# add_layer(json.dumps({'data_name': 'qw2', 'type': 'point', 'layer_name': 'vtoroi'}),
#           json.dumps([{"x": 3, "y": 2, "z": 3}, {"x": 2, "y": 3, "z": 3}]))
# add_point(json.dumps({"x": 1, "y": 2, "z": 3}), 'qw2')
#
# add_layer(json.dumps({'data_name': 'qw2', 'type': 'point', 'layer_name': 'vtoroi'}))
class LayerParameters(Schema):
    data_name = fields.Str()
    layer_type = fields.Str()
    layer_name = fields.Str()
    points = fields.Str()

    # name type


@app.route('/add_layer', methods=['POST'])
def add_layer():
    """Post Layer
    ---
    post:
        description: Post layer with config and json of points(more then 1)
        parameters:
          - in: query
            schema: LayerParameters

        responses:
            200:
                description: Return status
                content:
                    application/json:
                        schema: PointSchema
    """

    points = request.args.get('points')
    print(points)
    data_name = request.args.get('data_name')
    layer_name = request.args.get('layer_name')
    typ = request.args.get('layer_type')
    print(data_name, typ, layer_name)
    res = kepler.add_layer(json.dumps({'data_name': data_name, 'type': typ, 'layer_name': layer_name}), points)
    return jsonify(status=res), 200


class BoundsParameters(Schema):
    bounds = fields.Str()


@app.route('/bounds_layer', methods=['POST'])
def bounds_layer():
    """Post bounds of Layer
    ---
    post:
        description: Post the bounds of area for displaying
        parameters:
          - in: query
            schema: BoundsParameters

        responses:
            200:
                description: Return status
                content:
                    application/json:
                        schema: PointSchema
    """

    bounds = request.args.get('bounds')
    bounds = make_tuple(bounds)

    res = kepler.bounds_layer(bounds)
    return jsonify(status=res), 200


with app.test_request_context():
    # spec.path(view=todo)
    spec.path(view=add_point)
    spec.path(view=add_layer)
    spec.path(view=bounds_layer)


@app.route('/docs')
@app.route('/docs/<path:path>')
def swagger_docs(path=None):
    if not path or path == 'index.html':
        return render_template('index.html', base_url='/docs')
    else:
        return send_from_directory('./swagger/static', path)


@app.route('/upload')
def upload():
    return render_template('upload.html')


def parse_video(filepath):
    print('video is reseived ')
    vidcap = cv2.VideoCapture(filepath)
    success, image = vidcap.read()
    count = 0
    while success:
        if count > 10000 and count < 10050:
            cv2.imwrite(os.path.join('./uploads', "frame%d.jpg" % count), image)
            print(count)  # save frame as JPEG file
        success, image = vidcap.read()
        # print('Read a new frame: ', count)
        count += 1
        if count == 10051:
            break
    print('video is parsed')


def gettext(filepath, coordinates={'x': 1030, 'y': 62, 'w': 350, 'h': 100}):
    dictToSend = json.dumps({'name': coordinates})
    print(dictToSend)
    print(type(json.dumps(dictToSend)))
    files = {'image': open(filepath, 'rb')}
    res = requests.post('http://0.0.0.0:8000/get_ocr', files=files, params={"json_boxes": dictToSend})
    print(res.url)
    print('response from server:', res.text)
    mytext = res.json()["name"]
    specialChars = " '.,:;!?#$%^&*( )"
    for specialChar in specialChars:
        mytext = mytext.replace(specialChar, '')
    i = mytext.find('N')
    j = mytext.find('E')
    if i != -1 and j != -1:
        lat = mytext[i - 7:i]
        lon = mytext[j - 7:j]

        lat = lat[:2] + '.' + lat[2:]
        lon = lon[:2] + '.' + lon[2:]
        try:
            lat = (-1) * float(lat)
            lon = (-1) * float(lon)

            # lat, lon = transform(P4326, P3857, lon, lat)

        except ValueError:
            lat = ''
            lon = ''
    else:
        lat = ''
        lon = ''
    # m = mytext.split()
    # print(m)
    # lat = m[0].split(':')[1].split(';')[2][:-1]
    # lon = m[1].split(':')[1].split(';')[2][:-1]
    print(lat)
    print(lon)
    return lat, lon


@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    if request.method == 'POST':
        file = request.files['file']

        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        if request.form['text1'] != '':
            boarders = {"x": int(request.form['text1']), "y": int(request.form['text2']),
                        "w": int(request.form['text3']), "h": int(request.form['text4'])}
        else:
            boarders = {'x': 1260, 'y': 70, 'w': 350, 'h': 100}
        parse_video(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print(boarders)
        point_list = []
        for file in os.listdir(app.config['UPLOAD_FOLDER']):
            print(file)
            if file[-3:] == 'jpg':
                print('MY PICS')
                new_point = {"x": 3, "y": 2, "z": 3}
                lat, lon = gettext(os.path.join(app.config['UPLOAD_FOLDER'], file), boarders)
                print(lat, lon)
                if lat != '':
                    new_point["x"] = float(lat)
                    new_point["y"] = float(lon)
                    point_list.append(new_point)
                    print('pppppppppppp', new_point)
        print('aaaaaaaaaa', point_list)
        # add_layer(json.dumps({'data_name': 'qw2', 'type': 'point', 'layer_name': 'vtoroi'}),
        #           json.dumps([{"x": 3, "y": 2, "z": 3}, {"x": 2, "y": 3, "z": 3}]))
        kepler.add_layer(json.dumps({'data_name': 'last', 'type': 'point', 'layer_name': 'last'}),
                         json.dumps(point_list))
        return redirect(url_for('upload',
                                filename=filename))


# kepler.add_layer(json.dumps({'data_name': 'qw2', 'type': 'point', 'layer_name': 'vtoroi'}),
#                   json.dumps([{"x": 3, "y": 2, "z": 3}, {"x": 2, "y": 3, "z": 3}]))

if __name__ == '__main__':
    app.run(debug=True)
