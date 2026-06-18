import os
import re
import sys
import subprocess
from pathlib import Path

import yaml


MAX_FILE_SIZE_BYTES = 1024 * 1024
CONTENT_PATTERN_FLAGS = re.IGNORECASE | re.MULTILINE


def compile_pattern(
    pattern: str,
    rule_name: str,
    field_name: str,
    flags: int = 0,
) -> re.Pattern[str] | None:
    try:
        return re.compile(pattern, flags)
    except re.error as exc:
        print(
            f"[WARNING] Skipping invalid regex in rule '{rule_name}' "
            f"({field_name}): {pattern!r} ({exc})"
        )
        return None


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}

    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_rules() -> list[dict]:
    github_action_path = Path(os.environ["GITHUB_ACTION_PATH"])

    default_rules_path = (
        github_action_path / "rules" / "default-rules.yml"
    )

    custom_rules_file = os.environ.get("RULES_FILE", "")
    rules_mode = os.environ.get("RULES_MODE", "merge").lower()

    default_config = load_yaml(default_rules_path)
    default_rules = default_config.get("rules", [])

    # No custom file provided → use defaults only
    if not custom_rules_file:
        return default_rules

    custom_rules_path = Path(custom_rules_file)

    if not custom_rules_path.exists():
        print(f"Custom rules file not found: {custom_rules_path}")
        sys.exit(1)

    custom_config = load_yaml(custom_rules_path)

    custom_rules = custom_config.get("rules", [])
    disabled_rules = set(custom_config.get("disabled_rules", []))

    if rules_mode == "replace":
        return custom_rules

    if rules_mode != "merge":
        print(
            f"Unsupported rules mode '{rules_mode}'. "
            "Valid values are: merge, replace"
        )
        sys.exit(1)

    merged_rules = [
        rule
        for rule in default_rules
        if rule.get("id") not in disabled_rules
    ]

    merged_rules.extend(custom_rules)

    return merged_rules


def prepare_rules(rules: list[dict]) -> list[dict]:
    prepared_rules: list[dict] = []

    for rule in rules:
        if not isinstance(rule, dict):
            continue

        prepared_rule = dict(rule)
        rule_name = prepared_rule.get("name", "unnamed rule")

        compiled_paths = []
        for pattern in prepared_rule.get("paths", []):
            if not isinstance(pattern, str):
                continue

            compiled_pattern = compile_pattern(pattern, rule_name, "paths")
            if compiled_pattern is not None:
                compiled_paths.append(compiled_pattern)

        compiled_content_patterns = []
        for pattern in prepared_rule.get("patterns", []):
            if not isinstance(pattern, str):
                print(f"[WARNING] Skipping non-string pattern in rule '{rule_name}': {pattern!r}")
                continue

            compiled_pattern = compile_pattern(
                pattern,
                rule_name,
                "patterns",
                CONTENT_PATTERN_FLAGS,
            )
            if compiled_pattern is not None:
                compiled_content_patterns.append(compiled_pattern)

        prepared_rule["paths"] = compiled_paths
        prepared_rule["patterns"] = compiled_content_patterns
        prepared_rules.append(prepared_rule)

    return prepared_rules

def run(command: list[str]) -> str:
    result = subprocess.run(
        command,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def main() -> int:
    base_ref = os.environ.get("BASE_REF")

    if not base_ref:
        print("BASE_REF is empty. This Action is intended to run on pull_request events.")
        return 1

    run(["git", "fetch", "origin", base_ref, "--depth=1"])

    base_sha = run(["git", "merge-base", f"origin/{base_ref}", "HEAD"])
    changed_files_raw = run(["git", "diff", "--name-only", f"{base_sha}...HEAD"])
    changed_files = [line for line in changed_files_raw.splitlines() if line.strip()]

    rules = load_rules()
    rules = prepare_rules(rules)

    print(f"Loaded {len(rules)} rules.")
    print(f"Changed files: {len(changed_files)}")
    
    findings = []

    for file in changed_files:
        path = Path(file)

        for rule in rules:
            rule_name = rule.get("name", "unnamed rule")
            path_patterns = rule.get("paths", [])
            content_patterns = rule.get("patterns", [])

            if not any(
                pattern.search(file)
                for pattern in path_patterns
            ):
                continue

            findings.append(f"[SENSITIVE FILE CHANGED] {file} matched rule '{rule_name}'")

            if not path.exists() or not path.is_file():
                continue

            try:
                file_size = path.stat().st_size
            except OSError as exc:
                print(f"[WARNING] Skipping {file}: could not read file metadata ({exc})")
                continue

            if file_size > MAX_FILE_SIZE_BYTES:
                print(
                    f"[WARNING] Skipping {file}: file too large ({file_size} bytes)"
                )
                continue

            try:
                content = path.read_text(errors="ignore")
            except OSError as exc:
                print(f"[WARNING] Skipping {file}: could not read file content ({exc})")
                continue

            for pattern in content_patterns:
                if pattern.search(content):
                    findings.append(
                        f"[RISKY PATTERN] {file} matched '{pattern.pattern}' in rule '{rule_name}'"
                    )

    if findings:
        print("Potential supply chain risks detected:\n")
        for finding in findings:
            print(f"- {finding}")

        print("\nManual security review required.")
        return 1

    print("No risky supply chain patterns detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())