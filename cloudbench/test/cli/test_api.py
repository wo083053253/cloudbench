#coding:utf-8
import collections
import unittest

from cloudbench.cli import create_api_assets, report_benchmark

from cloudbench.test.cli.utils import TestAPIClient, TestVolume, TestCloud, TestJobReport


class CLIAPITestCase(unittest.TestCase):
    def setUp(self):
        self.api = TestAPIClient()

    def test_asset_creation(self):
        vol1 = TestVolume("/dev/sdc", True, "TestDisk", 15)
        vol2 = TestVolume("/dev/sdd", True, "TestDisk", 20)
        benchmark_volumes = [vol1, vol2]

        extra_assets = ["test-asset"]

        cloud = TestCloud("Cloud", "m1.test", "loc/1", "loc", benchmark_volumes)

        api_client = TestAPIClient()

        assets = create_api_assets(cloud, api_client, benchmark_volumes, extra_assets)

        self.assertEqual(1, len(api_client.providers.objects))
        provider = list(api_client.providers.objects.values())[0]

        self.assertEqual(1, len(api_client.locations.objects))
        location = list(api_client.locations.objects.values())[0]
        self.assertEqual(provider, location["provider"])

        self.assertEqual(5, len(api_client.abstract_assets.objects))  # Instance, Disk, Size 1, Size 2, Extra


        found_assets = set()
        for abstract_asset in api_client.abstract_assets.objects.values():
            found_assets.add(abstract_asset["name"])

        self.assertEqual(set(("TestDisk", "m1.test", "15 GB", "20 GB", "test-asset")), found_assets)

        self.assertEqual(5, len(api_client.physical_assets.objects))
        for physical_asset in api_client.physical_assets.objects.values():
            self.assertIn(physical_asset["asset"], api_client.abstract_assets.objects.values())

        self.assertEqual(5, len(assets))
        expected = {"TestDisk": 2, "m1.test": 1, "15 GB": 1, "20 GB": 1, "test-asset": 1}
        for physical_asset, quantity in assets:
            expected_quantity = expected[physical_asset["asset"]["name"]]
            self.assertEqual(expected_quantity, quantity)

    def test_report_benchmark(self):
        api_client = TestAPIClient()

        configuration = api_client.configurations.create(mode="rw", block_size="4", io_depth=4)

        asset1 = api_client.physical_assets.create(asset={"name": "asset1"})
        asset2 = api_client.physical_assets.create(asset={"name": "asset2"})
        assets = [(asset1, 1), (asset2, 2)]

        job_report = TestJobReport()

        report_benchmark(api_client, assets, configuration, job_report)

        self.assertEqual(5, len(api_client.measurements.objects))
        for measurement in api_client.measurements.objects.values():
            self.assertEqual(configuration, measurement["configuration"])
            self.assertEqual(measurement["metric"].lower(), measurement["value"])
            self.assertFalse(measurement["committed"])


        # Check we have the right number of measurement assets
        self.assertEqual(10, len(api_client.measurement_assets.objects))

        # Check the quantity is correct
        assets_with_quantity = [(measurement_asset["asset"]["asset"]["name"], measurement_asset["quantity"])
                                for measurement_asset in api_client.measurement_assets.objects.values()]
        self.assertEqual(sorted([("asset1", 1), ("asset2", 2)]), sorted(set(assets_with_quantity)))

        # Check the assets are properly assigned
        count = collections.Counter()
        for measurement_asset in api_client.measurement_assets.objects.values():
            count[measurement_asset["measurement"]["metric"]] += 1

        self.assertEqual(5, len(count))  # 5 different metrics
        for _, count in count.most_common():
            self.assertEqual(2, count)  # 2 assets per metric

        # Check that the initial write isn't committed

        # Check that we have a commit
        self.assertEqual(5, len(api_client.updates))
        for update in api_client.updates:
            self.assertTrue(update["committed"])
