# Supply Chain Review Action

## What this action does

This Action helps review pull requests for risky supply chain changes before they are merged. It scans changed files against a configurable rule set and fails the check when it detects sensitive files or suspicious patterns.

The motivation is to catch common supply chain attack paths early, especially in files like package manifests, workflows, devcontainers, MCP configs, and repository automation settings. That gives maintainers a fast signal that a PR may need manual security review.

## Example

The following workflow runs the action on every pull request using a custom rules file in `merge` mode:

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

Where `security/supply-chain-rules.yml` contains a custom rule like:

```yaml
rules:
	- id: company-custom-mcp
		name: Company custom MCP configuration
		paths:
			- "(^|/)custom-mcp\\.json$"
		patterns:
			- command
			- args
			- docker
```

If a pull request modifies a file named `custom-mcp.json` with content like:

```json
{
	"server": {
		"command": "python",
		"args": ["server.py"],
		"runtime": "docker"
	}
}
```

The action will fail the check with the following output:

```
Loaded 7 rules.
Changed files: 4

Potential supply chain risks detected:

- [SENSITIVE FILE CHANGED] custom-mcp.json matched rule 'Company custom MCP configuration'
- [RISKY PATTERN] custom-mcp.json matched 'command' in rule 'Company custom MCP configuration'
- [RISKY PATTERN] custom-mcp.json matched 'args' in rule 'Company custom MCP configuration'
- [RISKY PATTERN] custom-mcp.json matched 'docker' in rule 'Company custom MCP configuration'

Manual security review required.
```

This signals that the PR introduces changes to a sensitive file containing risky patterns, and requires a manual security review before merging.

## Additional documentation

- [Rule format](docs/RULES.md)
- [Protecting the configuration with CODEOWNERS](docs/CODEOWNERS.md)
- [Requiring the action with a repository ruleset](docs/RULESETS.md)
- [Threat model](docs/THREAT_MODEL.md)
- [Background: Miasma and Human-in-the-Loop Supply Chain Attacks](docs/MIASMA.md)