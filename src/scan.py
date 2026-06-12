import os
import re
import sys
import subprocess
from pathlib import Path

import yaml


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
    rules_file = Path(os.environ.get("RULES_FILE", "security/supply-chain-rules.yml"))
    base_ref = os.environ.get("BASE_REF")

    if not base_ref:
        print("BASE_REF is empty. This Action is intended to run on pull_request events.")
        return 1

    if not rules_file.exists():
        print(f"Rules file not found: {rules_file}")
        return 1

    run(["git", "fetch", "origin", base_ref, "--depth=1"])

    base_sha = run(["git", "merge-base", f"origin/{base_ref}", "HEAD"])
    changed_files_raw = run(["git", "diff", "--name-only", f"{base_sha}...HEAD"])
    changed_files = [line for line in changed_files_raw.splitlines() if line.strip()]

    rules_data = yaml.safe_load(rules_file.read_text()) or {}
    rules = rules_data.get("rules", [])

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