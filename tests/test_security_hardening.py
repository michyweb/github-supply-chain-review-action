"""Tests for security hardening changes."""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scan import compile_pattern, prepare_rules  # noqa: E402


class TestSecurityHardening(unittest.TestCase):
    @patch.dict(os.environ, {"GITHUB_ACTION_PATH": str(Path(__file__).parent.parent)})
    def test_prepare_rules_skips_invalid_regex(self):
        rules = [
            {
                "id": "invalid-regex",
                "name": "invalid regex",
                "paths": ["(risky"],
                "patterns": ["([a-z"],
            }
        ]

        prepared = prepare_rules(rules)

        self.assertEqual(prepared[0]["paths"], [])
        self.assertEqual(prepared[0]["patterns"], [])

    def test_compile_pattern_accepts_valid_regex(self):
        compiled = compile_pattern("command", "example", "patterns")
        self.assertIsNotNone(compiled)
        self.assertTrue(compiled.search('{"command": true}'))

    def test_compile_pattern_rejects_invalid_regex(self):
        compiled = compile_pattern("([a-z", "example", "patterns")
        self.assertIsNone(compiled)