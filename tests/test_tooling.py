#!/usr/bin/env python3
"""Dependency-free regression tests for the skill's offline tooling."""
from __future__ import annotations

import csv
import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def run(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


class LibraryIndexTests(unittest.TestCase):
    def test_index_shape_and_verified_statuses(self) -> None:
        with (ROOT / "references/library-index.csv").open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(521, len(rows))
        self.assertEqual(521, len({row["name"] for row in rows}))
        self.assertEqual({"200"}, {row["http_status"] for row in rows})
        self.assertEqual(7, sum(row["latest_http_status"] == "404" for row in rows))


class CommandLineTests(unittest.TestCase):
    def test_shell_exact_alias_and_latest_fallback(self) -> None:
        result = run("./bin/ahelp", "--offline", "++")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue(result.stdout.startswith("append\tcollections\t"))

        result = run("./bin/ahelp", "--offline", "--latest", "accept")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("latest=404; stable fallback", result.stdout)
        self.assertIn("/documentation/library/sockets/accept", result.stdout)

    def test_shell_unknown_symbol_fails_cleanly(self) -> None:
        result = run("./bin/ahelp", "--offline", "definitely-not-a-symbol")
        self.assertEqual(1, result.returncode)
        self.assertIn("No indexed match", result.stderr)

    def test_python_helper(self) -> None:
        result = run(sys.executable, "scripts/arturo_help.py", "map")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertTrue(result.stdout.startswith("map\titerators\t"))


class McpTests(unittest.TestCase):
    def test_initialize_list_and_alias_url(self) -> None:
        requests = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "arturo_doc_url",
                    "arguments": {"symbol": "++", "channel": "stable"},
                },
            },
        ]
        result = run(
            sys.executable,
            "mcp/server.py",
            input_text="".join(json.dumps(item) + "\n" for item in requests),
        )
        self.assertEqual(0, result.returncode, result.stderr)
        responses = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual("arturo-language-help", responses[0]["result"]["serverInfo"]["name"])
        self.assertEqual(3, len(responses[1]["result"]["tools"]))
        text = responses[2]["result"]["content"][0]["text"]
        self.assertTrue(text.endswith("/documentation/library/collections/append"))


if __name__ == "__main__":
    unittest.main()
