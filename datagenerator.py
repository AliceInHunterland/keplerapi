import time
import kepler
import json
import numpy as np

start = int(time.time())

# (9.55, 41.95, 10.65, 42)
# (9.8, 41.8, 10, 42))
temp = np.linspace(start, start + 200, 200)
x = np.linspace(9.89, 10, 200)
# print(x)
y = 41.89 + 0.1 * np.sin(100*x)
# print(y)
import datetime

kepler.zeroing()
for i, val in enumerate(x):
    print(val)
    print(y[i])
    print(temp[i])
    now = datetime.datetime.now()
    now.strftime('%m/%d/%y %H:%M:%S')
    print(type(now))
    kepler.add_point(json.dumps({"x": val, "y": y[i], "z": 5, 'datatime': str(now)}), 'robot')
kepler.bounds_layer((9.79, 41.79, 10, 42))
kepler.add_layer(json.dumps({'data_name': 'robot', 'type': 'point', 'layer_name': 'robot_path'}))
#kepler.add_filter('robot')
