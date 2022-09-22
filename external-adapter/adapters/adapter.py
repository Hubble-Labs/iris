from bridge import Bridge

import os
from requests.auth import HTTPBasicAuth

PLANET_API_KEY = os.getenv('PL_API_KEY')
auth = HTTPBasicAuth(PLANET_API_KEY, '')

class Adapter:
    base_url = 'https://api.planet.com/basemaps/v1/mosaics'
    city = ['city', 'q']

    def __init__(self, input):
        self.id = input.get('id', '1')
        self.request_data = input.get('data')
        if self.validate_request_data():
            self.bridge = Bridge()
            self.set_params()
            self.create_request()
        else:
            self.result_error('No data provided')

    def validate_request_data(self):
        if self.request_data is None:
            return False
        if self.request_data == {}:
            return False
        return True

    def set_params(self):
        for param in self.city:
            self.city = self.request_data.get(param)
            if self.city is not None:
                break
            
    def create_request(self):
        try:
            params = {
                'api_key': PLANET_API_KEY,
            }
            response = self.bridge.request(self.base_url, params)
            self.result = response.json()
            data = response.json()
            self.result_success(data)
            
        except Exception as e:
            self.result_error(e)
        finally:
            self.bridge.close()

    def result_success(self, data):
        self.result = {
            'jobRunID': self.id,
            'data': data,
            'result': self.result,
            'statusCode': 200,
        }

    def result_error(self, error):
        self.result = {
            'jobRunID': self.id,
            'status': 'errored',
            'error': f'There was an error: {error}',
            'statusCode': 500,
        }
