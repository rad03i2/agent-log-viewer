import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from agent_log_viewer.cli import main

class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "run.jsonl"
        self.path.write_text('\n'.join([json.dumps({"timestamp":"2026-09-21T10:00:00Z","level":"INFO","agent":"planner","event":"start","message":"started"}), json.dumps({"timestamp":"2026-09-21T10:01:00Z","level":"ERROR","agent":"worker","event":"tool_error","message":"timeout"})]) + '\n', encoding="utf-8")
    def tearDown(self): self.tmp.cleanup()

    def test_view_json(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(["view", str(self.path), "--level", "ERROR", "--json"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output.getvalue())["message"], "timeout")

    def test_stats_json(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(["stats", str(self.path), "--json"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output.getvalue())["total"], 2)

    def test_missing_file(self):
        error = io.StringIO()
        with contextlib.redirect_stderr(error):
            code = main(["view", str(Path(self.tmp.name) / "missing.log")])
        self.assertEqual(code, 2)

if __name__ == "__main__": unittest.main()
