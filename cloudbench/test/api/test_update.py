#coding:utf-8
import unittest

from requests import Response

from cloudbench.api.client import Client
from cloudbench.api.exceptions import APIError
from cloudbench.test.utils import TEST_ENDPOINT, PredictableTestAdapter


class APIUpdateTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client(TEST_ENDPOINT)  # We'll never hit that anyway

        self.accepted = Response()
        self.accepted.status_code = 201

        self.refused = Response()
        self.refused.status_code = 400

        self.not_found = Response()
        self.not_found.status_code = 404

    def test_update_accepted(self):
        adapter = PredictableTestAdapter([self.accepted])
        self.client._session.mount(TEST_ENDPOINT, adapter)
        self.client.update({'provider': '/api/v1/provider/2/', 'id': 2, 'resource_uri': '/api/v1/location/2/', 'name': 'us-east-1'})

        self.assertEqual(1, len(adapter.requests))
        update, = adapter.requests

        self.assertEqual("PATCH", update.method)

    def test_update_refused(self):
        adapter = PredictableTestAdapter([self.refused, self.not_found])
        self.client._session.mount(TEST_ENDPOINT, adapter)

        obj = {'provider': '/api/v1/provider/2/', 'id': 2, 'resource_uri': '/api/v1/location/2/', 'name': 'us-east-1'}

        self.assertRaises(APIError, self.client.update, obj)
        self.assertRaises(APIError, self.client.update, obj)

        self.assertEqual(2, len(adapter.requests))
