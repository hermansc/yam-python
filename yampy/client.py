import json

import requests

from constants import DEFAULT_BASE_URL
from errors import ResponseError, NotFoundError, InvalidAccessTokenError, \
    RateLimitExceededError, UnauthorizedError

class Client(object):
    """
    A client for the Yammer API.
    """

    def __init__(self, access_token=None, base_url=None):
        self.access_token = access_token
        self.base_url = base_url or DEFAULT_BASE_URL

    def get(self, path, **kwargs):
        """
        Makes an HTTP GET request to the Yammer API. Any keyword arguments will
        be converted to query string parameters.

        The path should be the path of an API endpoint, e.g. "/messages"
        """
        return self._request("get", path, **kwargs)

    def post(self, path, **kwargs):
        """
        Makes an HTTP POST request to the Yammer API. Any keyword arguments
        will be sent as the body of the request.

        The path should be the path of an API endpoint, e.g. "/messages"
        """
        return self._request("post", path, **kwargs)

    def _request(self, method, path, **kwargs):
        response = requests.request(
            method=method,
            url=self._build_url(path),
            headers=self._build_headers(),
            params=kwargs,
        )
        return self._parse_response(response)

    def _build_url(self, path):
        return self.base_url + path + ".json"

    def _build_headers(self):
        if self.access_token:
            return {
                "Authorization": "Bearer %s" % self.access_token,
            }
        else:
            return {}

    def _parse_response(self, response):
        if 200 <= response.status_code < 300:
            return json.loads(response.text)
        else:
            raise self._exception_for_response(response)

    def _exception_for_response(self, response):
        if response.status_code == 404:
            return NotFoundError(response.reason)
        elif response.status_code == 400 and "OAuthException" in response.text:
            return InvalidAccessTokenError(response.reason)
        elif response.status_code == 401:
            return UnauthorizedError(response.reason)
        elif response.status_code == 429:
            return RateLimitExceededError(response.reason)
        else:
            return ResponseError("%d error: %s" % (
                response.status_code, response.reason,
            ))
