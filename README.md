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

### Default configuration

By default, the Action uses the built-in rules shipped with the Action itself.

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
      - uses: actions/checkout@<<REPLACE-VERSION>>
        with:
          fetch-depth: 0

      - uses: michyweb/github-supply-chain-review-action@v0.1.0
```

---

### Merge custom rules with the default rules

Additional rules can be defined in the caller repository and merged with the built-in rules.

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
      - uses: actions/checkout@<<REPLACE-VERSION>>
        with:
          fetch-depth: 0

      - uses: michyweb/github-supply-chain-review-action@v0.1.0
        with:
          rules-file: security/supply-chain-rules.yml
          rules-mode: merge
```

---

### Replace the default rules

Repositories can completely replace the built-in rules with their own rule set.

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
      - uses: actions/checkout@<<REPLACE-VERSION>>
        with:
          fetch-depth: 0

      - uses: michyweb/github-supply-chain-review-action@v0.1.0
        with:
          rules-file: security/supply-chain-rules.yml
          rules-mode: replace
```

---

## Rule evaluation logic

The Action supports two modes:

### `merge` (default)

1. Load the built-in rules shipped with the Action.
2. Load the custom rules from the caller repository.
3. Remove any rules listed in `disabled_rules`.
4. Append the custom rules.
5. Evaluate the resulting rule set.

```
built-in rules
       +
custom rules
       -
disabled rules
       =
final rule set
```

### `replace`

1. Ignore the built-in rules.
2. Load only the custom rules provided by the caller repository.
3. Evaluate the custom rule set.

```
custom rules
      =
final rule set
```

---

## Example custom configuration

```yaml
disabled_rules:
  - npm-package-scripts

rules:
  - id: company-custom-mcp
    name: Company custom MCP configuration

    paths:
      - '(^|/)custom-mcp\.json$'

    patterns:
      - command
      - args
      - docker
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