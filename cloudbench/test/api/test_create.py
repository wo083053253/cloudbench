#coding:utf-8
import decimal
import unittest
import simplejson as json

from requests import Response

from cloudbench.api.client import Client
from cloudbench.api.util import path_join

from cloudbench.test.utils import TEST_ENDPOINT, PredictableTestAdapter, make_json_response


OBJ_RESPONSE = {
    "id": "1",
    "k": "v",
    "a": 1,
}

class APICreateTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client(TEST_ENDPOINT)  # We'll never hit that anyway
        test_loc = path_join(TEST_ENDPOINT, "/created/loc/1")
        created = Response()
        created.status_code = 201
        created.headers["location"] =  test_loc

        self.adapter = PredictableTestAdapter([created, make_json_response(OBJ_RESPONSE)])
        self.client._session.mount(TEST_ENDPOINT, self.adapter)

    def test_create_workflow(self):
        """
        Test that we have the a POST - GET workflow for creation
        We also test that we return the object
        """
        ret = self.client.measurements.create()

        self.assertEqual(2, len(self.adapter.requests))
        create, retrieve = self.adapter.requests

        self.assertEqual("POST", create.method)
        self.assertEqual("GET", retrieve.method)

        self.assertDictEqual(OBJ_RESPONSE, ret)

    def test_create_req(self):
        """
        Test that the format and headers of the create request are valid
        """
        kw = {"a":"1", "b":"2", "rel":{"id":1}, "dec_val": decimal.Decimal("123.98623")}

        expected = {}
        expected.update(kw)
        expected["dec_val"] = 123.98623

        self.client.measurements.create(**kw)
        req = self.adapter.requests[0]
        self.assertDictEqual(expected, json.loads(req.body))
        self.assertEqual("application/json", req.headers["content-type"])


