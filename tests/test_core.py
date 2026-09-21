import json
import tempfile
import unittest
from pathlib import Path

from agent_log_viewer.core import filter_entries, parse_line, read_entries, summarize

class CoreTests(unittest.TestCase):
    def test_jsonl_parsing(self):
        row = parse_line(json.dumps({"timestamp":"2026-09-21T10:00:00Z","level":"error","agent":"planner","event":"tool_error","message":"failed"}))
        self.assertEqual(row.level, "ERROR")
        self.assertEqual(row.agent, "planner")
        self.assertEqual(row.event, "tool_error")

    def test_text_and_plain_parsing(self):
        self.assertEqual(parse_line("2026-09-21T10:00:00Z [WARN] slow tool").level, "WARN")
        self.assertEqual(parse_line("unstructured message").message, "unstructured message")

    def test_filtering(self):
        rows = [parse_line('{"level":"INFO","agent":"a","message":"ok"}'), parse_line('{"level":"ERROR","agent":"b","message":"Timeout calling tool"}')]
        result = list(filter_entries(rows, min_level="WARN", query="timeout", agent="b"))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].level, "ERROR")

    def test_regex_and_time_filter(self):
        rows = [parse_line('{"timestamp":"2026-09-20T10:00:00Z","message":"tool=search 200"}'), parse_line('{"timestamp":"2026-09-22T10:00:00Z","message":"tool=fetch 500"}')]
        result = list(filter_entries(rows, query=r"fetch\s+500", regex=True, since="2026-09-21T00:00:00Z"))
        self.assertEqual(len(result), 1)

    def test_summary(self):
        rows = [parse_line('{"level":"INFO","agent":"a","event":"start","message":"x"}'), parse_line('{"level":"ERROR","agent":"a","event":"fail","message":"y"}')]
        data = summarize(rows)
        self.assertEqual(data["total"], 2)
        self.assertEqual(data["agents"]["a"], 2)
        self.assertEqual(data["levels"]["ERROR"], 1)

    def test_file_reader_tracks_source_and_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "agent.jsonl"
            path.write_text('{"message":"one"}\n\n{"message":"two"}\n', encoding="utf-8")
            rows = list(read_entries([path]))
            self.assertEqual([r.line for r in rows], [1, 3])
            self.assertEqual(rows[0].source, str(path))

    def test_invalid_since_is_rejected(self):
        with self.assertRaises(ValueError):
            list(filter_entries([parse_line("hello")], since="yesterday"))

if __name__ == "__main__": unittest.main()
