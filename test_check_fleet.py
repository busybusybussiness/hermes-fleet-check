#!/usr/bin/env python3
"""Tests for check_fleet.py. Run: python test_check_fleet.py  (exit 0 = all pass)."""
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_fleet  # noqa: E402

EX = os.path.join(HERE, "examples")


def load(name):
    with open(os.path.join(EX, name), encoding="utf-8") as f:
        return json.load(f)


class ChecksTest(unittest.TestCase):
    def test_good_fixture_passes(self):
        self.assertEqual(check_fleet.check(load("good_fleet.json")), [])

    def test_bad_fixture_catches_every_planted_fault(self):
        f = check_fleet.check(load("bad_fleet.json"))
        text = "\n".join(f)
        self.assertIn("oversight-review: no fallback model", text)
        self.assertIn("operator-planner: same model appears twice", text)
        self.assertIn("volume-scout: chain uses disabled model", text)
        self.assertIn("volume-scout: cadence 15", text)
        self.assertIn("risk-monitor: no-llm role must not name a model", text)
        self.assertIn("queue-worker: unknown tier", text)
        self.assertIn("queue-worker: no cadence_minutes", text)

    def test_missing_roles_is_a_finding(self):
        self.assertTrue(check_fleet.check({"roles": []}))
        self.assertTrue(check_fleet.check([]))

    def test_cli_exit_codes(self):
        script = os.path.join(HERE, "check_fleet.py")
        good = subprocess.run([sys.executable, script, os.path.join(EX, "good_fleet.json")],
                              capture_output=True, text=True)
        bad = subprocess.run([sys.executable, script, os.path.join(EX, "bad_fleet.json")],
                             capture_output=True, text=True)
        missing = subprocess.run([sys.executable, script, os.path.join(EX, "nope.json")],
                                 capture_output=True, text=True)
        self.assertEqual(good.returncode, 0)
        self.assertEqual(bad.returncode, 1)
        self.assertEqual(missing.returncode, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
