# Supply Chain Review Action

Detects changes to sensitive files and patterns commonly associated with supply chain attacks, including:

- package lifecycle hooks
- CI/CD workflows
- build scripts
- devcontainers
- IDE workspace configurations
- AI agent instruction files
- MCP configurations

## Usage

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

      - uses: michyweb/github-supply-chain-review-action@v0.1.0
        with:
          rules-file: security/supply-chain-rules.yml
```

## Example rules

```yaml
rules:
  - name: npm package scripts
    paths:
      - '(^|/)package\.json$'
    patterns:
      - preinstall
      - postinstall
      - prepare
```

## Why?

Recent campaigns such as Miasma have demonstrated that the attack surface extends beyond source code and includes any file capable of influencing automated tools or developers.

This emerging class of threats is often referred to as Human-in-the-Loop Supply Chain Attacks.

## What this Action does not do

This Action is not a malware scanner and does not replace:

- Code review
- Dependency scanning
- Secret scanning
- SAST tools
- Human review