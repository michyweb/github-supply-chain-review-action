# Rule format

This document describes how to configure custom rules for the action.

## Modes

The Action supports two modes:

### `merge` (default)

1. Load the built-in rules shipped with the Action.
2. Load the custom rules from the caller repository.
3. Remove any rules listed in `disabled_rules`.
4. Append the custom rules.
5. Evaluate the resulting rule set.

```text
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

```text
custom rules
      =
final rule set
```

## Example custom configuration

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
      - docker
```
