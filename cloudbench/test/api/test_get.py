#coding:utf-8
import unittest

from cloudbench.api.client import Client
from cloudbench.api.exceptions import MultipleObjectsReturned, NoSuchObject
from cloudbench.api.util import path_join

from cloudbench.test.utils import TEST_ENDPOINT, PredictableTestAdapter, make_json_response


BASE_RESPONSE = {
    "meta": {
        "limit": 20,
        "next": None,
        "offset": 0,
        "previous": None,
        "total_count": 0
    },
    "objects": []
}

OBJ_1_PARTIAL = {
    "id": 1,
    "a": "b",
    "resource_uri": "this/path"
}

OBJ_1 = dict(OBJ_1_PARTIAL)
OBJ_1["extra"] = 2

OBJ_2_PARTIAL = {
    "id": 2,
    "a": "c",
    "resource_uri": "other/path"
}

class APIGetTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client(TEST_ENDPOINT)
        self.list_response = dict(BASE_RESPONSE)  # Make a copy

    def test_get_workflow(self):
        """
        Test that the GET workflow is correct (list + retrieve)
        """
        self.list_response["objects"] = [OBJ_1_PARTIAL]
        self.list_response["meta"]["total_count"] = 1
        adapter = PredictableTestAdapter([make_json_response(self.list_response), make_json_response(OBJ_1)])
        self.client._session.mount(TEST_ENDPOINT, adapter)

        self.client.measurements.get()

        self.assertEqual(2, len(adapter.requests))

        l, retrieve = adapter.requests

        self.assertEqual("GET", l.method)
        self.assertEqual("GET", retrieve.method)

        self.assertEqual(path_join(TEST_ENDPOINT, "this/path"), retrieve.url)

    def test_get_return(self):
        """
        Test that GET returns a single object, and that we don't use the result from list
        """
        self.list_response["objects"] = [OBJ_1_PARTIAL]
        self.list_response["meta"]["total_count"] = 1
        adapter = PredictableTestAdapter([make_json_response(self.list_response), make_json_response(OBJ_1)])
        self.client._session.mount(TEST_ENDPOINT, adapter)

        ret = self.client.measurements.get()
        self.assertDictEqual(OBJ_1, ret)

    def test_duplicate(self):
        """
        Test that we raise an error if we have multiple objects
        """
        self.list_response["objects"] = [OBJ_1_PARTIAL, OBJ_2_PARTIAL]
        self.list_response["meta"]["total_count"] = 1
        adapter = PredictableTestAdapter([make_json_response(self.list_response), make_json_response(OBJ_1)])
        self.client._session.mount(TEST_ENDPOINT, adapter)

        self.assertRaises(MultipleObjectsReturned, self.client.measurements.get)

    def test_not_found(self):
        adapter = PredictableTestAdapter([make_json_response(self.list_response), make_json_response(OBJ_1)])
        self.client._session.mount(TEST_ENDPOINT, adapter)
        self.assertRaises(NoSuchObject, self.client.measurements.get)
