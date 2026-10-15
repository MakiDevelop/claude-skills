"""Regression checks. Run: python -m unittest discover -s tests -v"""
import base64
import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


db = module("query_script", "skills/db-eda/scripts/query.py")
image = module("image_script", "skills/generate-image/scripts/generate.py")
strict_json = module("strict_json", "skills/json-validate/scripts/validate_json.py")
validator = module("skill_validator", "tools/validate.py")


class MetadataTests(unittest.TestCase):
    def check_content(self, content):
        with tempfile.TemporaryDirectory() as temp:
            skill = Path(temp) / "example"
            skill.mkdir()
            (skill / "SKILL.md").write_text(content, encoding="utf-8")
            return validator.validate_skill(skill)

    def test_non_mapping_yaml_is_reported_not_crashed(self):
        errors = self.check_content("---\n- item\n---\n")
        self.assertTrue(any(item.level == "ERROR" for item in errors))

    def test_wrong_description_type_is_reported_not_crashed(self):
        content = "---\nname: example\ndescription: 12\nallowed-tools: Read\nauthor: Maki\nversion: '1.0.0'\ntags: []\nrequired_env: []\n---\n## Quality Gates\n"
        errors = self.check_content(content)
        self.assertTrue(any("description" in item.msg for item in errors))


class SQLiteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "input ?#.db"
        with sqlite3.connect(self.path) as conn:
            conn.execute("CREATE TABLE items (id INTEGER)")
            conn.executemany("INSERT INTO items VALUES (?)", [(1,), (2,), (3,), (4,)])
        self.conn = db.open_database(self.path, "sqlite", 5)

    def tearDown(self):
        self.conn.close()
        self.temp.cleanup()

    def test_inner_limit_cannot_bypass_output_bound(self):
        result = db.query(self.conn, "SELECT * FROM (SELECT * FROM items LIMIT 4)", "sqlite", 2)
        self.assertEqual(len(result["rows"]), 2)
        self.assertTrue(result["truncated"])

    def test_semicolon_literal_and_trailing_comment(self):
        result = db.query(self.conn, "SELECT ';' AS value -- trailing comment", "sqlite", 2)
        self.assertEqual(result["rows"], [(";",)])
        self.assertFalse(result["truncated"])

    def test_multiple_statements_and_writes_fail(self):
        for sql in ("SELECT 1; DELETE FROM items", "DELETE FROM items RETURNING id"):
            with self.subTest(sql=sql), self.assertRaises(sqlite3.Error):
                db.query(self.conn, sql, "sqlite", 2)
        self.assertEqual(self.conn.execute("SELECT count(*) FROM items").fetchone()[0], 4)

    def test_missing_file_is_not_created(self):
        absent = self.path.parent / "absent.db"
        with self.assertRaises(FileNotFoundError):
            db.open_database(absent, "sqlite", 5)
        self.assertFalse(absent.exists())


class JsonTests(unittest.TestCase):
    def test_duplicate_nested_keys_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            strict_json.parse('{"outer": {"a": 1, "a": 2}}')

    def test_nonstandard_numbers_rejected(self):
        for text in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                strict_json.parse(text)

    def test_jsonl_physical_line_and_no_schema_claim(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "data.jsonl"
            path.write_text('{}\n\n{"ok": true}\n', encoding="utf-8")
            result = strict_json.validate(path, jsonl=True)
        self.assertFalse(result["valid"])
        self.assertEqual(result["errors"][0]["line"], 2)
        self.assertEqual(result["checked_valid_records"], 2)
        self.assertEqual(result["schema"], "not checked")


class ImageTests(unittest.TestCase):
    def test_actual_mime_controls_extension(self):
        result = {"candidates": [{"content": {"parts": [
            {"text": "response"},
            {"inlineData": {"mimeType": "image/jpeg",
                            "data": base64.b64encode(b"image").decode()}}
        ]}}]}
        self.assertEqual(image.first_image(result), (b"image", ".jpg"))

    def test_no_image_or_bad_base64_fails(self):
        with self.assertRaises(ValueError):
            image.first_image(None)
        with self.assertRaises(ValueError):
            image.first_image({"candidates": []})
        with self.assertRaises(ValueError):
            image.first_image({"candidates": [{"content": {"parts": [
                {"inlineData": {"mimeType": "image/png", "data": "!!"}}
            ]}}]})


@unittest.skipUnless(importlib.util.find_spec("duckdb"), "duckdb not installed")
class DuckDBTests(unittest.TestCase):
    def test_full_aggregation_before_visual_limits(self):
        import duckdb
        chart = module("chart_script", "skills/csv-to-chart/scripts/chart.py")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "it's data.csv"
            path.write_text("category,value\n" + "A,1\n" * 6000 + "B,4000\n",
                            encoding="utf-8")
            with duckdb.connect() as conn:
                rows, stats = chart.prepare(conn, path, "pie", "category", "value")
        self.assertEqual(dict(rows), {"A": 6000.0, "B": 4000.0})
        self.assertFalse(stats["sampled"])
        self.assertEqual(stats["used_rows"], 6001)

    def test_negative_pie_rejected_and_invalid_rows_reported(self):
        import duckdb
        chart = module("chart_script", "skills/csv-to-chart/scripts/chart.py")
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "data.csv"
            path.write_text("category,value\nA,-1\nB,3\nC,bad\n", encoding="utf-8")
            with duckdb.connect() as conn:
                with self.assertRaisesRegex(ValueError, "negative"):
                    chart.prepare(conn, path, "pie", "category", "value")
            with duckdb.connect() as conn:
                rows, stats = chart.prepare(conn, path, "bar", "category", "value")
        self.assertEqual(stats["rejected_rows"], 1)
        self.assertEqual(dict(rows), {"B": 3.0, "A": -1.0})

    def test_external_access_and_multiple_statements_blocked(self):
        import duckdb
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "data.duckdb"
            with duckdb.connect(str(path)) as conn:
                conn.execute("CREATE TABLE items AS SELECT 1 AS id")
            conn = db.open_database(path, "duckdb", 5)
            try:
                self.assertEqual(db.query(conn, "SELECT * FROM items", "duckdb", 1)["rows"], [(1,)])
                with self.assertRaises(ValueError):
                    db.query(conn, "SELECT 1; SELECT 2", "duckdb", 1)
                with self.assertRaises(duckdb.Error):
                    db.query(conn, "SELECT * FROM read_text('missing-file.txt')", "duckdb", 1)
            finally:
                conn.close()


if __name__ == "__main__":
    unittest.main()
