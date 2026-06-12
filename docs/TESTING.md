# Test Suite for Supply Chain Review Action

I have created a comprehensive test suite that covers all modes documented in `docs/RULES.md`.

## 📋 Summary

Created **26 tests** that fully validate the behavior of both modes:

- **`merge` mode** (7 tests): Combines built-in + custom rules, with support for `disabled_rules`
- **`replace` mode** (3 tests): Uses only custom rules, ignores built-in
- **Validations** (4 tests): Rule structure, error handling
- **Pattern Matching** (6 tests): Detection of patterns in paths and content
- **Rule Combinations** (3 tests): Different integration scenarios

## 📁 Created File Structure

```
tests/
├── test_rules_modes.py           # Main tests for merge/replace
├── test_scanning.py              # Integration tests and pattern matching
├── requirements.txt              # Dependencies (PyYAML)
├── README.md                     # Detailed execution guide
└── fixtures/                     # Example configurations for tests
    ├── custom-rules-merge.yml
    ├── custom-rules-disabled.yml
    ├── custom-rules-disable-multiple.yml
    ├── custom-rules-replace.yml
    └── custom-rules-replace-with-disabled.yml
```

## ✅ Tests by Mode

### `merge` Mode (default)

1. **Without custom rules** → Returns only default rules
2. **With custom rules** → Combines built-in + custom
3. **With disabled_rules** → Removes specified rules
4. **Multiple disabled** → Can disable several rules
5. **Default mode** → merge is used without specifying RULES_MODE
6. **Correct order** → Default rules before custom

### `replace` Mode

1. **Only custom rules** → Loads ONLY custom rules
2. **Ignores disabled_rules** → disabled_rules has no effect
3. **Excludes built-in** → No default rules included

### Pattern Matching

1. **Paths at any level** → Detects package.json in root and subdirectories
2. **Workflows in .github/** → Detects YAML/YML files correctly
3. **Case-insensitive on content** → preinstall, PREINSTALL, PreInstall
4. **curl|bash patterns** → Detects dangerous piped commands
5. **Devcontainer patterns** → postCreateCommand, initializeCommand, etc.

## 🚀 Running Tests

### Install dependencies
```bash
cd tests
pip install -r requirements.txt
```

### Run all tests
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### Result
```
Ran 26 tests in 0.175s
OK
```

### Run specific tests
```bash
# Only merge mode
python -m unittest tests.test_rules_modes.TestMergeMode -v

# Only replace mode
python -m unittest tests.test_rules_modes.TestReplaceMode -v

# Only pattern matching
python -m unittest tests.test_scanning.TestPatternMatching -v
```

## 🎯 Coverage of Cases

### Merge Mode - Combination 1: Only built-in
```
Default rules (4): npm-package-scripts, npm-native-bindings, 
                   github-workflows, devcontainers
```

### Merge Mode - Combination 2: Built-in + Custom
```
Default rules (4) + company-custom-mcp = 5 rules
```

### Merge Mode - Combination 3: Built-in (no disabled) + Custom
```
Default rules (3) - npm-package-scripts + company-custom-mcp = 4 rules
```

### Replace Mode
```
Only custom-rule-1 + custom-rule-2 = 2 rules (no built-in)
```

## 🧪 Tested Configuration Examples

### Configuration 1: Merge with Disabled Rules
```yaml
disabled_rules:
  - npm-package-scripts

rules:
  - id: company-custom-mcp
    name: Company custom MCP configuration
    paths:
      - "(^|/)custom-mcp\\.json$"
    patterns:
      - command
      - args
```
✅ Result: Built-in (without npm-package-scripts) + company-custom-mcp

### Configuration 2: Replace Mode
```yaml
rules:
  - id: custom-rule-1
    name: Custom Rule One
    paths:
      - "(^|/)custom-one\\.json$"
    patterns:
      - pattern1
```
✅ Result: Only custom-rule-1 (no built-in rules)

## 📊 Validations

Tests validate:
- ✅ Loading YAML files (existing, empty, non-existent)
- ✅ Correct rule structure (id, name, paths, patterns)
- ✅ Merge and replace behavior
- ✅ Processing of disabled_rules
- ✅ Rule order in merge mode
- ✅ Case-sensitive pattern matching on paths
- ✅ Case-insensitive pattern matching on content
- ✅ Error handling (invalid mode, missing file)

## 🔍 Available Fixtures

| File | Purpose |
|------|---------|
| `custom-rules-merge.yml` | Merge mode with 1 custom rule |
| `custom-rules-disabled.yml` | Merge mode with 1 disabled rule |
| `custom-rules-disable-multiple.yml` | Merge mode with 2 disabled rules |
| `custom-rules-replace.yml` | Replace mode with 2 custom rules |
| `custom-rules-replace-with-disabled.yml` | Replace mode with disabled_rules (ignored) |

