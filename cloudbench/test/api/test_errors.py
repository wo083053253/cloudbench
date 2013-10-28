#coding:utf-8
import unittest
import six

from requests import Response

from cloudbench.api.client import Client
from cloudbench.api.exceptions import APIError

from cloudbench.test.api import MockTimeSleep
from cloudbench.test.api.test_create import OBJ_RESPONSE
from cloudbench.test.api.test_get import BASE_RESPONSE, OBJ_1_PARTIAL
from cloudbench.test.utils import TEST_ENDPOINT, RepeatingTestAdapter, PredictableTestAdapter, make_json_response


class ErrorTestCase(unittest.TestCase):
    def test_error_wrapping(self):
        """
        Test that HTTP errors are wrapped into API Errors
        """
        client = Client(TEST_ENDPOINT)
        response = Response()
        response.status_code = 500
        response.reason = "INTERNAL SERVER ERROR"
        adapter = RepeatingTestAdapter(response)

        client._session.mount(TEST_ENDPOINT, adapter)

        # We want a bit more control than just assertRaises
        try:
            client.measurements.get()
        except APIError as e:
            self.assertIsNotNone(e.response)
            self.assertEqual(500, e.response.status_code)
            self.assertEqual("INTERNAL SERVER ERROR", e.response.reason)
        else:
            self.fail("No APIError was raised")

    def test_retry(self):
        retry_max = 2
        retry_wait = 7

        client = Client(TEST_ENDPOINT, retry_max=retry_max, retry_wait=retry_wait)

        err_response = Response()
        err_response.status_code = 500
        err_response.reason = "INTERNAL SERVER ERROR"

        response_data = dict(BASE_RESPONSE)
        response_data["objects"] = [OBJ_1_PARTIAL]
        response_data["total_count"] = 1
        success_response = make_json_response(response_data)

        adapter = PredictableTestAdapter([err_response, err_response, success_response])
        client._session.mount(TEST_ENDPOINT, adapter)

        mock_sleep = MockTimeSleep()

        with mock_sleep:
            try:
                 response = client.measurements.list()
            except APIError as e:
                self.fail("API call wasn't retried: %s" % e)

        self.assertEqual([OBJ_1_PARTIAL], response)
        self.assertEqual([retry_wait, retry_wait], mock_sleep.calls)


        adapter = PredictableTestAdapter([err_response, err_response, err_response, success_response])
        client._session.mount(TEST_ENDPOINT, adapter)

        mock_sleep = MockTimeSleep()

        with mock_sleep:
            self.assertRaises(APIError, client.measurements.list)

        self.assertEqual([retry_wait, retry_wait], mock_sleep.calls)

    def test_random_retry(self):
        retry_max = 50  # We want a large sample
        retry_wait = 100
        retry_range = 5

        client = Client(TEST_ENDPOINT, retry_max=retry_max, retry_wait=retry_wait, retry_range=retry_range)
        err_response = Response()
        err_response.status_code = 500
        err_response.reason = "INTERNAL SERVER ERROR"

        adapter = RepeatingTestAdapter(err_response)
        client._session.mount(TEST_ENDPOINT, adapter)

        mock_sleep = MockTimeSleep()

        with mock_sleep:
            self.assertRaises(APIError, client.measurements.list)

        for wait_time in mock_sleep.calls:
            self.assertGreaterEqual(wait_time, retry_wait - retry_range)
            self.assertLessEqual(wait_time, retry_wait + retry_range)

        self.assertFalse(all([wait_time == retry_wait for wait_time in mock_sleep.calls]))

    def test_negative_retry(self):
        retry_max = 100
        retry_wait = 0
        retry_range = 10

        client = Client(TEST_ENDPOINT, retry_max=retry_max, retry_wait=retry_wait, retry_range=retry_range)
        err_response = Response()
        err_response.status_code = 500
        err_response.reason = "INTERNAL SERVER ERROR"

        adapter = RepeatingTestAdapter(err_response)
        client._session.mount(TEST_ENDPOINT, adapter)

        mock_sleep = MockTimeSleep()

        with mock_sleep:
            self.assertRaises(APIError, client.measurements.list)

        for wait_time in mock_sleep.calls:
            self.assertGreaterEqual(wait_time, 0)

    def test_race_condition(self):
        self.client = Client(TEST_ENDPOINT)  # We'll never hit that anyway

        response_data = dict(BASE_RESPONSE)

        absent = make_json_response(response_data)

        exists = Response()
        exists.status_code = 400
        exists.reason = "BAD REQUEST"
        exists._content = six.b('{"configuration": {"__all__": ["Configuration with this I/O Mode, Block Size and I/O Depth already exists."]}}')

        response_data = dict(BASE_RESPONSE)
        response_data["objects"] = [OBJ_1_PARTIAL]
        response_data["total_count"] = 1
        success_response = make_json_response(response_data)

        self.adapter = PredictableTestAdapter([absent, exists, success_response, make_json_response(OBJ_RESPONSE)])
        self.client._session.mount(TEST_ENDPOINT, self.adapter)

        ret = self.client.configurations.get_or_create()
        self.assertDictEqual(OBJ_RESPONSE, ret)
        self.assertEqual(4, len(self.adapter.requests))
