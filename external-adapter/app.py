from crypt import methods
from flask import Flask, request, jsonify
from adapters.iris_adapter import IrisAdapter
from adapters.adapter import Adapter
from adapters.image_hash_adapter import ImageHashAdapter

"""
app.py
- Defines function that automatically runs when app/flask server is start up.
"""
app = Flask(__name__)

"""
@app.before_request is a decorator that servers as a shorthand for 
    'app.add_url_rule("/", view_func=index)'. It runs before every request that is sent to the app.
    https://flask.palletsprojects.com/en/2.2.x/api/#flask.Flask.before_request
log_request_info:
    - Logs the header and body data for every request that comes in before the request is fulfilled, 
    eg: before call_adapter is called.
"""
@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())

"""
@app.route('/', methods=['POST']) is a decorator that serves as short hand for the routing rule.
    https://flask.palletsprojects.com/en/2.2.x/api/#flask.Flask.before_request
"""
@app.route('/', methods=['POST'])
def call_adapter():
    data = request.get_json()
    if data == '':
        data = {}
    adapter = Adapter(data)
    return jsonify(adapter.result)

@app.route('/image_hash', methods=['POST'])
def image_hash_adapter():
    data=request.get_json()
    if data == '':
        data = {}
    print(data)
    adapter = ImageHashAdapter(data)
    return jsonify(adapter.result)

@app.route('/iris', methods=['POST'])
def iris_adapter():
    data=request.get_json()
    if data == '':
        data = {}
    print(data)
    adapter = IrisAdapter(data)
    return jsonify(adapter.result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='8080', threaded=True)
