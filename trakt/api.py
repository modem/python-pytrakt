import json
import logging
from functools import lru_cache
from json import JSONDecodeError

from requests import Session

from trakt import errors
from trakt.errors import BadResponseException

__author__ = 'Elan Ruusamäe'


class HttpClient:
    """Class for abstracting HTTP requests
    """

    #: Default request HEADERS
    headers = {'Content-Type': 'application/json', 'trakt-api-version': '2'}

    def __init__(self, base_url: str, session: Session):
        self.base_url = base_url
        self.session = session
        self.auth = None
        self.logger = logging.getLogger('trakt.http_client')

    def get(self, url: str):
        return self.request('get', url)

    def delete(self, url: str):
        self.request('delete', url)

    def post(self, url: str, data):
        return self.request('post', url, data=data)

    def put(self, url: str, data):
        return self.request('put', url, data=data)

    def set_auth(self, auth):
        self.auth = auth

    def request(self, method, url, data=None):
        """Handle actually talking out to the trakt API, logging out debug
        information, raising any relevant `TraktException` Exception types,
        and extracting and returning JSON data

        :param method: The HTTP method we're executing on. Will be one of
            post, put, delete, get
        :param url: The fully qualified url to send our request to
        :param data: Optional data payload to send to the API
        :return: The decoded JSON response from the Trakt API
        :raises TraktException: If any non-200 return code is encountered
        """

        url = self.base_url + url
        self.logger.debug('REQUEST [%s] (%s)', method, url)
        if method == 'get':  # GETs need to pass data as params, not body
            response = self.session.request(method, url, headers=self.headers, auth=self.auth, params=data)
        else:
            response = self.session.request(method, url, headers=self.headers, auth=self.auth, data=json.dumps(data))
        self.logger.debug('RESPONSE [%s] (%s): %s', method, url, str(response))

        if response.status_code == 204:  # HTTP no content
            return None
        self.raise_if_needed(response)

        return self.decode_response(response)

    @staticmethod
    def decode_response(response):
        try:
            return json.loads(response.content.decode('UTF-8', 'ignore'))
        except JSONDecodeError as e:
            raise BadResponseException(f"Unable to parse JSON: {e}")

    def raise_if_needed(self, response):
        if response.status_code in self.error_map:
            raise self.error_map[response.status_code](response)

    @property
    @lru_cache(maxsize=None)
    def error_map(self):
        """Map HTTP response codes to exception types
        """

        # Get all of our exceptions except the base exception
        errs = [getattr(errors, att) for att in errors.__all__
                if att != 'TraktException']

        return {err.http_code: err for err in errs}
