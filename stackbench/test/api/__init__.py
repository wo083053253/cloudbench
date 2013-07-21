#coding:utf-8
import json
from urllib.parse import urlparse, parse_qsl
from email.message import Message

from requests import Response


TEST_ENDPOINT = "http://example.com"


class BaseTestAdapter():
    def __init__(self):
        self.requests = []

    def send(self, request, *args, **kwargs):
        self.requests.append(request)
        response = self._send(request, *args, **kwargs)
        _add_http_client_response(response)
        return response

    def _send(self, request, *args, **kwargs):
        raise NotImplementedError()

    def close(self):
        pass


class PredictableTestAdapter(BaseTestAdapter):
    def __init__(self, responses):
        self.responses = responses
        super().__init__()

    def _send(self, request, *args, **kwargs):
        return self.responses.pop(0)

class RepeatingTestAdapter(BaseTestAdapter):
    def __init__(self, response):
        self.response = response
        super().__init__()

    def _send(self, request, *args, **kwargs):
        return self.response



def _add_http_client_response(response):
    """
    Add an HTTP client respponse as original response, since it's expected
    """
    class O():
        pass

    msg = Message()
    for k, v in response.headers.items():
        msg[k] = v

    original_response = O()
    original_response.msg = msg

    raw = O()
    raw._original_response = original_response

    response.raw = raw


def make_json_response(data, status_code=200, headers=None):
    """
    :type data: dict
    :type status_code: int
    :type headers: dict

    :returns: A Response object with the corresponding JSON body
    :rtype: requests.models.Response
    """
    if headers is None:
        headers = {}

    response = Response()

    response.status_code = status_code
    response._content = json.dumps(data).encode("utf-8")

    headers["content-type"] = "application/json"
    response.headers = headers

    return response


def extract_qs(url):
    """
    :type url: str
    :returns: The querystring mapping
    :rtype: dict
    """
    p = urlparse(url)
    res = parse_qsl(p.query)

    def normalize(item):  # Remove useless lists
        arg, values = item
        if len(values):
            if len(values) > 1:
                return arg, values
            return arg, values[0]
        return arg, None

    return dict(map(normalize, res))
