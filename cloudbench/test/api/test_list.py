#coding:utf-8
import unittest

from cloudbench.api.client import Client

from cloudbench.test.utils import PredictableTestAdapter, make_json_response, TEST_ENDPOINT, RepeatingTestAdapter, extract_qs


EMPTY_RESPONSE = {
    "meta": {
        "limit": 20,
        "next": None,
        "offset": 0,
        "previous": None,
        "total_count": 0
    },
    "objects": []
}


class APIListTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client(TEST_ENDPOINT)  # We'll never hit that anyway

    def test_pagination(self):
        """
        Test that we access all the pages
        """

        b1 = {
            "meta": {
                "limit": 2,
                "next": "/api/v1/measurement/?offset=2&limit=2",
                "offset": 0,
                "previous": None,
                "total_count": 4},
            "objects": [{"id": 1}, {"id": 2}]
        }

        b2 = {
            "meta": {
                "limit": 2,
                "next": None,
                "offset": 2,
                "previous": "/api/v1/measurement/?offset=0&limit=2",
                "total_count": 4},
            "objects": [{"id": 3}, {"id": 4}]
        }

        adapter = PredictableTestAdapter([make_json_response(b1), make_json_response(b2)])
        self.client._session.mount(TEST_ENDPOINT, adapter)

        measurements = self.client.measurements.list()

        self.assertEqual(0, len(adapter.responses))
        self.assertEqual(4, len(measurements))
        self.assertEqual([1,2,3,4], [measurement["id"] for measurement in measurements])

    def test_filters(self):
        """
        Test that arguments are translated as filters
        """

        adapter = RepeatingTestAdapter(make_json_response(EMPTY_RESPONSE))
        self.client._session.mount(TEST_ENDPOINT, adapter)

        self.client.measurements.list()
        self.client.measurements.list(arg1="1", arg2="2")
        self.client.measurements.list(arg1="1", arg2="2", arg3="a")

        r1, r2, r3 = adapter.requests

        self.assertDictEqual({}, extract_qs(r1.url))
        self.assertDictEqual({"arg1": "1", "arg2": "2"}, extract_qs(r2.url))
        self.assertDictEqual({"arg1": "1", "arg2": "2", "arg3": "a"}, extract_qs(r3.url))

    def test_related_filters(self):
        """
        Test that we replace related objects with their IDs
        """
        adapter = RepeatingTestAdapter(make_json_response(EMPTY_RESPONSE))
        self.client._session.mount(TEST_ENDPOINT, adapter)

        self.client.measurements.list(related_obj={"id": "5", "arg2": "4"})
        self.client.measurements.list(related_obj={"id": "5"}, other="1")

        r1, r2 = adapter.requests

        self.assertDictEqual({"related_obj": "5"}, extract_qs(r1.url))
        self.assertDictEqual({"related_obj": "5", "other": "1"}, extract_qs(r2.url))
