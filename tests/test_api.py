"""Regression tests for the generated public v1 API contract."""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class StaticApiBuildTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix=".test-api-", dir=ROOT)
        self.output = pathlib.Path(self.temp_dir.name) / "site"
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_api.py"), "--out", str(self.output)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def read_json(self, relative_path):
        return json.loads((self.output / relative_path).read_text(encoding="utf-8"))

    def test_existing_v1_all_records_shape_is_preserved(self):
        payload = self.read_json("api/v1/protests.json")
        self.assertEqual(set(payload), {"meta", "records"})
        self.assertIn("generated", payload["meta"])
        self.assertIn("count", payload["meta"])
        self.assertIn("counts_by_group", payload["meta"])
        self.assertIn("intensity_scale", payload["meta"])
        self.assertIsInstance(payload["records"], list)

    def test_version_and_dataset_metadata_are_published(self):
        payload = self.read_json("api/v1/protests.json")
        meta = payload["meta"]
        self.assertEqual(meta["api_version"], "1.0.0")
        self.assertEqual(meta["schema_version"], "1.0.0")
        self.assertRegex(meta["dataset_revision"], r"^sha256:[0-9a-f]{64}$")
        self.assertEqual(meta["generated"], meta["generated_at"])

    def test_index_keeps_existing_endpoint_templates(self):
        index = self.read_json("api/v1/index.json")
        self.assertEqual(index["endpoints"]["all"], "api/v1/protests.json")
        self.assertEqual(index["endpoints"]["year"], "api/v1/years/{YYYY}.json")
        self.assertEqual(index["endpoints"]["month"], "api/v1/months/{YYYY-MM}.json")
        self.assertEqual(index["endpoints"]["group"], "api/v1/groups/{group}.json")
        self.assertEqual(index["endpoints"]["record"], "api/v1/records/{id}.json")
        self.assertEqual(index["api_version"], "1.0.0")

    def test_year_month_group_and_record_endpoints_exist(self):
        index = self.read_json("api/v1/index.json")
        self.assertTrue(index["years"])
        self.assertTrue(index["months"])
        self.assertTrue(index["groups"])

        year_payload = self.read_json(f"api/v1/years/{index['years'][0]}.json")
        month_payload = self.read_json(f"api/v1/months/{index['months'][0]}.json")
        group_payload = self.read_json("api/v1/groups/students.json")

        self.assertEqual(set(year_payload), {"year", "count", "records"})
        self.assertEqual(set(month_payload), {"month", "count", "records"})
        self.assertEqual(set(group_payload), {"group", "count", "records"})

        record_id = self.read_json("api/v1/protests.json")["records"][0]["id"]
        record = self.read_json(f"api/v1/records/{record_id}.json")
        self.assertEqual(record["id"], record_id)

    def test_generated_record_count_matches_source(self):
        source = json.loads((ROOT / "data" / "protests.json").read_text(encoding="utf-8"))
        payload = self.read_json("api/v1/protests.json")
        self.assertEqual(payload["meta"]["count"], len(source["records"]))
        self.assertEqual(len(payload["records"]), len(source["records"]))

    def test_map_and_host_headers_are_included(self):
        self.assertTrue((self.output / "index.html").is_file())
        headers = (self.output / "_headers").read_text(encoding="utf-8")
        self.assertIn("Access-Control-Allow-Origin: *", headers)
        self.assertIn("X-Content-Type-Options: nosniff", headers)


if __name__ == "__main__":
    unittest.main()
