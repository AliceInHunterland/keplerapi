import json
import os

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask import Flask, jsonify, render_template, send_from_directory, request
from marshmallow import Schema, fields
import kepler
from ast import literal_eval as make_tuple

app = Flask(__name__, template_folder='swagger/templates')


@app.route('/')
def home():
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
    print(data_name,typ,layer_name)
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


if __name__ == '__main__':
    app.run(debug=True)