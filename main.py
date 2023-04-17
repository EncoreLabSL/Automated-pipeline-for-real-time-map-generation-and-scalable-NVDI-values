from crypt import methods
from flask import Flask, send_file, request
from modules.render_map import render_map
import json
 
app = Flask(__name__, static_folder='static')
 
@app.route('/')
def hello_world():
    return app.send_static_file('index.html')


@app.route('/raster', methods=['POST'])
def send_raster():
    if request.method == 'POST':
        data = json.loads(request.data)
        print(data)
        geojson = data['geojson']
        fecha = data['fecha']
        ndvi_min = float(data['ndvi_min'])
        ndvi_max = float(data['ndvi_max'])
        render_map(geojson, fecha, ndvi_min, ndvi_max)
        # Beware! raster.tif is unique no matter number of connections
        return send_file("raster.pkl", attachment_filename='raster.pkl') 
    else:
        raise NotImplemented

if __name__ == '__main__':
    app.run(host='10.0.0.195', debug=True, port=5000)  # host hardcoded
