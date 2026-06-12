"""
Tests for the modes documented in RULES.md:
- merge (default): Combines built-in + custom rules, with disabled_rules option
- replace: Uses only custom rules, ignores built-in
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scan import load_yaml, load_rules


class TestMergeMode(unittest.TestCase):
    """Tests for merge mode (default)"""

    def setUp(self):
        """Set up environment for each test"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.fixtures_dir = Path(__file__).parent / "fixtures"

    def tearDown(self):
        """Clean up resources"""
        self.temp_dir.cleanup()

    @patch.dict(os.environ, {
        "GITHUB_ACTION_PATH": str(Path(__file__).parent.parent),
        "RULES_MODE": "merge",
        "RULES_FILE": ""
    })
    def test_merge_mode_no_custom_rules(self):
        """Merge mode without custom rules: should return only default rules"""
        rules = load_rules()

        # Verify default rules are loaded
        self.assertGreater(len(rules), 0)

        # Verify expected rules are present
        rule_ids = {rule.get("id") for rule in rules}
        self.assertIn("npm-package-scripts", rule_ids)
        self.assertIn("npm-native-bindings", rule_ids)
        self.assertIn("github-workflows", rule_ids)
        self.assertIn("devcontainers", rule_ids)

    @patch.dict(os.environ, {
        "GITHUB_ACTION_PATH": str(Path(__file__).parent.parent),
        "RULES_MODE": "merge",
    })
    def test_merge_mode_with_custom_rules(self):
        """Merge mode with custom rules: should combine built-in + custom"""
        custom_rules_file = self.fixtures_dir / "custom-rules-merge.yml"
        os.environ["RULES_FILE"] = str(custom_rules_file)

        rules = load_rules()

        rule_ids = {rule.get("id") for rule in rules}

        # Should contain default rules
        self.assertIn("npm-package-scripts", rule_ids)

        # Should contain custom rule
        self.assertIn("company-custom-mcp", rule_ids)

    @patch.dict(os.environ, {
        "GITHUB_ACTION_PATH": str(Path(__file__).parent.parent),
        "RULES_MODE": "merge",
    })
    def test_merge_mode_with_disabled_rules(self):
        """Merge mode: disabled_rules should remove default rules"""
        custom_rules_file = self.fixtures_dir / "custom-rules-disabled.yml"
        os.environ["RULES_FILE"] = str(custom_rules_file)

        rules = load_rules()

        rule_ids = {rule.get("id") for rule in rules}

        # npm-package-scripts should be disabled
        self.assertNotIn("npm-package-scripts", rule_ids)

        # Other default rules should be present
        self.assertIn("npm-native-bindings", rule_ids)
        self.assertIn("github-workflows", rule_ids)

        # Custom rule should be present
        self.assertIn("company-custom-mcp", rule_ids)

    @patch.dict(os.environ, {
        "GITHUB_ACTION_PATH": str(Path(__file__).parent.parent),
        "RULES_MODE": "merge",
    })
    def test_merge_mode_disable_multiple_rules(self):
        """Merge mode: can disable multiple rules"""
        custom_rules_file = self.fixtures_dir / "custom-rules-disable-multiple.yml"
        os.environ["RULES_FILE"] = str(custom_rules_file)

        rules = load_rules()

        rule_ids = {rule.get("id") for rule in rules}

        # Disabled rules should not be present
        self.assertNotIn("npm-package-scripts", rule_ids)
        self.assertNotIn("npm-native-bindings", rule_ids)

        # Other rules should be present
        self.assertIn("github-workflows", rule_ids)
        self.assertIn("devcontainers", rule_ids)

    @patch.dict(os.environ, {
        "GITHUB_ACTION_PATH": str(Path(__file__).parent.parent),
    })
    def test_merge_mode_is_default(self):
        """Without specifying RULES_MODE, should use merge by default"""
        # Remove RULES_MODE if it exists
        os.environ.pop("RULES_MODE", None)

        custom_rules_file = self.fixtures_dir / "custom-rules-merge.yml"
        os.environ["RULES_FILE"] = str(custom_rules_file)

        rules = load_rules()

        rule_ids = {rule.get("id") for rule in rules}

        # Should behave as merge: combine rules
        self.assertIn("npm-package-scripts", rule_ids)
        self.assertIn("company-custom-mcp", rule_ids)


class TestReplaceMode(unittest.TestCase):
    """Tests for replace mode"""

    def setUp(self):
        """Set up environment for each test"""
        self.fixtures_dir = Path(__file__).parent / "fixtures"

    @patch.dict(os.environ, {
        "GITHUB_ACTION_PATH": str(Path(__file__).parent.parent),
        "RULES_MODE": "replace",
    })
    def test_replace_mode_with_custom_rules(self):
        """Replace mode: should use ONLY custom rules, ignore built-in"""
        custom_rules_file = self.fixtures_dir / "custom-rules-replace.yml"
        os.environ["RULES_FILE"] = str(custom_rules_file)

        rules = load_rules()

        rule_ids = {rule.get("id") for rule in rules}

        # Should contain ONLY custom rules
        self.assertIn("custom-rule-1", rule_ids)
        self.assertIn("custom-rule-2", rule_ids)

        # Should NOT contain default rules
        self.assertNotIn("npm-package-scripts", rule_ids)
        self.assertNotIn("npm-native-bindings", rule_ids)
        self.assertNotIn("github-workflows", rule_ids)
        self.assertNotIn("devcontainers", rule_ids)

    @patch.dict(os.environ, {
        "GITHUB_ACTION_PATH": str(Path(__file__).parent.parent),
        "RULES_MODE": "replace",
    })
    def test_replace_mode_ignores_disabled_rules(self):
        """Replace mode: ignores disabled_rules (not processed)"""
        custom_rules_file = self.fixtures_dir / "custom-rules-replace-with-disabled.yml"
        os.environ["RULES_FILE"] = str(custom_rules_file)

        rules = load_rules()

        rule_ids = {rule.get("id") for rule in rules}

        # In replace mode, disabled_rules has NO effect, all custom rules are loaded
        self.assertIn("custom-rule-1", rule_ids)
        self.assertIn("custom-rule-2", rule_ids)

        # Number of rules should be exactly 2 (the 2 custom rules)
        self.assertEqual(len(rules), 2)

    @patch.dict(os.environ, {
        "GITHUB_ACTION_PATH": str(Path(__file__).parent.parent),
    })
    def test_replace_mode_explicit(self):
        """Replace mode explicitly configured"""
        os.environ["RULES_MODE"] = "replace"
        custom_rules_file = self.fixtures_dir / "custom-rules-replace.yml"
        os.environ["RULES_FILE"] = str(custom_rules_file)

        rules = load_rules()

        # Should be only the 2 custom rules
        self.assertEqual(len(rules), 2)


class TestInvalidRulesMode(unittest.TestCase):
    """Tests for handling invalid modes"""

    def setUp(self):
        """Set up environment for each test"""
        self.fixtures_dir = Path(__file__).parent / "fixtures"

    @patch.dict(os.environ, {
        "GITHUB_ACTION_PATH": str(Path(__file__).parent.parent),
        "RULES_MODE": "invalid_mode",
        "RULES_FILE": str(Path(__file__).parent / "fixtures" / "custom-rules-merge.yml")
    })
    def test_invalid_rules_mode_raises_error(self):
        """An invalid RULES_MODE should return error"""
        with self.assertRaises(SystemExit):
            load_rules()


class TestMissingCustomRulesFile(unittest.TestCase):
    """Tests for missing custom rules file"""

    @patch.dict(os.environ, {
        "GITHUB_ACTION_PATH": str(Path(__file__).parent.parent),
        "RULES_FILE": "/path/nonexistent/custom-rules.yml"
    })
    def test_missing_custom_rules_file_exits(self):
        """Non-existent custom rules file should cause exit"""
        with self.assertRaises(SystemExit):
            load_rules()


class TestLoadYaml(unittest.TestCase):
    """Tests for the load_yaml function"""

    def test_load_existing_yaml(self):
        """Should load an existing YAML file"""
        yaml_file = Path(__file__).parent / "fixtures" / "custom-rules-merge.yml"
        config = load_yaml(yaml_file)

        self.assertIsInstance(config, dict)
        self.assertIn("rules", config)

    def test_load_nonexistent_yaml(self):
        """Non-existent YAML file should return empty dict"""
        yaml_file = Path("/path/nonexistent/file.yml")
        config = load_yaml(yaml_file)

        self.assertEqual(config, {})

    def test_load_empty_yaml(self):
        """Empty YAML file should return empty dict or None"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("")
            f.flush()
            yaml_file = Path(f.name)

        try:
            config = load_yaml(yaml_file)
            self.assertIn(config, ({}, None))
        finally:
            yaml_file.unlink()


class TestRulesStructure(unittest.TestCase):
    """Tests for the structure of loaded rules"""

    @patch.dict(os.environ, {
        "GITHUB_ACTION_PATH": str(Path(__file__).parent.parent),
        "RULES_MODE": "merge",
        "RULES_FILE": ""
    })
    def test_rules_have_required_fields(self):
        """All rules should have required fields"""
        rules = load_rules()

        for rule in rules:
            # Required fields
            self.assertIn("id", rule)
            self.assertIn("name", rule)
            self.assertIn("paths", rule)

            # Fields should be of correct type
            self.assertIsInstance(rule["id"], str)
            self.assertIsInstance(rule["name"], str)
            self.assertIsInstance(rule["paths"], list)

    @patch.dict(os.environ, {
        "GITHUB_ACTION_PATH": str(Path(__file__).parent.parent),
        "RULES_MODE": "merge",
        "RULES_FILE": ""
    })
    def test_rules_have_patterns_field(self):
        """Rules should have patterns field"""
        rules = load_rules()

        for rule in rules:
            self.assertIn("patterns", rule)
            self.assertIsInstance(rule["patterns"], list)

    @patch.dict(os.environ, {
        "GITHUB_ACTION_PATH": str(Path(__file__).parent.parent),
        "RULES_MODE": "merge",
    })
    def test_merge_mode_order_custom_after_default(self):
        """In merge mode, custom rules should appear after default rules"""
        custom_rules_file = Path(__file__).parent / "fixtures" / "custom-rules-merge.yml"
        os.environ["RULES_FILE"] = str(custom_rules_file)

        rules = load_rules()

        # Get IDs in order
        rule_ids = [rule.get("id") for rule in rules]

        # Default rules should come before custom
        npm_scripts_idx = rule_ids.index("npm-package-scripts")
        company_mcp_idx = rule_ids.index("company-custom-mcp")

        self.assertLess(npm_scripts_idx, company_mcp_idx)


if __name__ == "__main__":
    unittest.main()
