#coding:utf-8
import unittest
from requests import Response

from cloudbench.api.client import Client
from cloudbench.api.exceptions import APIError
from cloudbench.test.api import MockTimeSleep
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
