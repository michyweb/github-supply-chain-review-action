# Requiring the Action with a Repository Ruleset

GitHub repository rulesets do not run the action themselves. Instead, they make the pull request unmergeable until the workflow that runs this action finishes successfully.

## How it works

1. Add a workflow that runs `michyweb/github-supply-chain-review-action` on `pull_request` events.
2. Make sure the workflow appears in the PR checks list.
3. Create a repository ruleset that targets the protected branch, such as `main`.
4. Add a rule that requires the workflow status check to pass before merge.
5. Disable bypasses if you want the check to be mandatory for everyone.

## Example workflow

```yaml
name: Supply Chain Review

on:
  pull_request:

permissions:
  contents: read

jobs:
  review:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: michyweb/github-supply-chain-review-action@v0.1.4
        with:
          rules-file: security/supply-chain-rules.yml
          rules-mode: merge
```

## Example ruleset configuration

In the repository ruleset for `main`, require the status check created by the workflow above. The exact name shown in the PR checks list depends on your workflow and job names.

A typical setup looks like this:

- Target branch: `main`
- Required status checks: the check produced by the "Supply Chain Review" workflow
- Bypass: disabled, if the check should be mandatory for all contributors

## What happens on a risky change

If the PR changes a sensitive file like `custom-mcp.json` and matches one of your rules, the action will fail the check and the ruleset will block the merge.

Example output:

```text
Loaded 7 rules.
Changed files: 4

Potential supply chain risks detected:

- [SENSITIVE FILE CHANGED] custom-mcp.json matched rule 'Company custom MCP configuration'
- [RISKY PATTERN] custom-mcp.json matched 'command' in rule 'Company custom MCP configuration'
- [RISKY PATTERN] custom-mcp.json matched 'args' in rule 'Company custom MCP configuration'
- [RISKY PATTERN] custom-mcp.json matched 'docker' in rule 'Company custom MCP configuration'

Manual security review required.
```

That means the ruleset is doing its job: the PR cannot be merged until the security review passes.

## Recommended checklist

- The action runs on `pull_request`.
- The rules file covers the sensitive paths you care about.
- The ruleset targets the correct branch.
- The status check required by the ruleset matches the workflow check name.
- Bypass is disabled if enforcement is required.
