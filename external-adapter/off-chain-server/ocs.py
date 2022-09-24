from flask import Flask

from crypt import methods
from flask import Flask, request, jsonify
from iris_adapter import IrisAdapter
from adapter import Adapter
from image_hash_adapter import ImageHashAdapter

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

@app.route('/', methods=['POST'])
def compute_avg_sc():
    data = request.get_json()
    if data == '':
        data = {}

    
    adapter = Adapter(data)
    return jsonify(adapter.result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='8080', threaded=True)
