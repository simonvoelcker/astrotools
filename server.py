import argparse
import json
import queue
import os
import threading

from flask import Flask, render_template, request, Response
from flask.json import jsonify

from lib.indi.controller import INDIController


app = Flask(__name__)
app.config['bootstrap_version']='3.3.7'
app.config['jquery_version']='3.1.1'
app.config['image_format'] = 'jpg'

subscriptions = []
indi_controller = None

def get_indi_controller():
    global indi_controller
    if indi_controller is None:
        indi_controller = INDIController(workdir=os.path.join(app.static_folder, 'images'))
    return indi_controller

def put_event(event):
    for subscription in subscriptions:
        subscription.put(event)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/devices')
def devices():
    return jsonify(get_indi_controller().devices())

@app.route('/device_names')
def device_names():
    return jsonify({'devices': get_indi_controller().device_names()})

@app.route('/device/<devicename>/properties')
def properties(devicename):
    return jsonify({'device': devicename, 'properties': get_indi_controller().properties(devicename)})

@app.route('/device/<devicename>/properties/<property>')
def property(devicename, property):
    return jsonify(get_indi_controller().property(devicename, property))

@app.route('/device/<devicename>/properties/<property>', methods=['PUT'])
def set_property(devicename, property):
    return jsonify(get_indi_controller().set_property(devicename, property, request.json['value']))

def image_path(file):
    return '/'.join([app.static_url_path, 'images', file]) 

def image_event(image_filepath):
    put_event({
        'type': 'image',
        'image_url': image_path(image_filepath),
        'image_id': '6174'
    })

def notification(level, title, message):
    put_event({
        'type': 'notification',
        'level': level,
        'title': title,
        'message': message
    })

@app.route('/status')
def status():
    return jsonify(get_indi_controller().status())

@app.route('/device/<devicename>/capture/<exposure>/<gain>')
def capture(devicename, exposure, gain):
    def exp():
        try:
            image_event(get_indi_controller().capture_image(devicename, float(exposure), float(gain)))
        except Exception as e:
            app.logger.error('Capture error', exc_info=e)

    threading.Thread(target=exp).start()
    return ('', 204)

@app.route('/device/<devicename>/start_sequence/<exposure>/<gain>')
def start_sequence(devicename, exposure, gain):
    def exp():
        try:
            while(app.config['framing']):
                image_event( get_indi_controller().capture_image(devicename, float(exposure), float(gain)))
        except Exception as e:
            app.logger.error('Capture error', exc_info=e)

    app.config['framing'] = True
    threading.Thread(target = exp).start()
    return('', 204)

@app.route('/device/<devicename>/stop_sequence')
def stop_sequence(devicename):
    app.config['framing'] = False
    return('', 200)

@app.route('/events')
def events():
    def gen():
        q = queue.Queue()
        subscriptions.append(q)
        while(True):
            data = q.get()
            yield(f'data: {json.dumps(data)}\n\n')
    return Response(gen(), mimetype="text/event-stream")

@app.route('/shutdown')
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        notification('warning', 'Error', 'unable to shutdown the server')
        return('', 500)
    func()
    return ('', 204)

@app.route('/clean-cache')
def clean_cache():
    numfiles = get_indi_controller().clean_cache()
    return jsonify({'files': numfiles})

app.secret_key = b'\xcc\xfc\xbe6^\x9a\xbf>\xbc\xaa\x9e\xe8\xa6\n7'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', help="Run server in debug mode (default: off)", action='store_true')
    parser.add_argument('--host', help="Hostname for server listening (default: 127.0.0.1)", default='127.0.0.1')
    parser.add_argument('-p', '--port', help="Port for server listening (default: 5000)", default='5000')
    args = parser.parse_args()
    app.run(threaded=True, host=args.host, port=int(args.port), debug=args.debug)
