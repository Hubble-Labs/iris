import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.auth import HTTPBasicAuth
import os

PLANET_API_KEY = ""
auth = HTTPBasicAuth(PLANET_API_KEY, '')

"""
Bridge:
- Creates a sessions object
- Creates a retry object
- Creates HTTPAdapter with retry object as param to set connect settings
- The mount call registers our Transport Adapter to a prefix. 
- The request function is defined to send a GET response to the Chainlink node
"""

class Bridge(object):
    def __init__(
        self,
        retries=3,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504),
    ):
        self.session = requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def request(self, url, params={}, headers={}, timeout=15):
        try:
            session_get = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=timeout,
                auth=auth
            )
            return session_get
        except Exception as e:
            raise e

    def close(self):
        self.session.close()
