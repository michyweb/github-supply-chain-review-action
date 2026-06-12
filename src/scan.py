import os
import re
import sys
import subprocess
from pathlib import Path

import yaml


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

    print(f"Loaded {len(rules)} rules.")
    print(f"Changed files: {len(changed_files)}")
    
    findings = []

    for file in changed_files:
        path = Path(file)

        for rule in rules:
            rule_name = rule.get("name", "unnamed rule")
            path_patterns = rule.get("paths", [])
            content_patterns = rule.get("patterns", [])

            if not any(re.search(pattern, file) for pattern in path_patterns):
                continue

            findings.append(f"[SENSITIVE FILE CHANGED] {file} matched rule '{rule_name}'")

            if not path.exists() or not path.is_file():
                continue

            content = path.read_text(errors="ignore")

            for pattern in content_patterns:
                if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                    findings.append(
                        f"[RISKY PATTERN] {file} matched '{pattern}' in rule '{rule_name}'"
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