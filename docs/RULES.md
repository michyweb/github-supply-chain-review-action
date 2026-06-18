# Rule format

This document describes how to configure custom rules for the action.

## Baseline

By default, the action enforces the built-in baseline from `rules/default-rules.yml`.

Custom configuration is applied on top of this baseline depending on the selected mode.

## Modes

The action supports two modes:

- `merge`: start from the default baseline, optionally disable some built-in rules, then add custom rules.
- `replace`: ignore the default baseline and evaluate only the custom rules from your `rules-file`.

### `merge` (default)

In `merge`, the baseline is kept and your custom rules are layered on top.

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

Workflow usage example:

```yaml
- uses: michyweb/github-supply-chain-review-action@<FULL_COMMIT_SHA>
  with:
    rules-file: security/supply-chain-rules.yml
    rules-mode: merge
```

Custom `rules-file` example for `merge`:

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

### `replace`

In `replace`, the baseline is ignored and only your custom rules are evaluated.

1. Ignore the built-in rules.
2. Load only the custom rules provided by the caller repository.
3. Evaluate the custom rule set.

```text
custom rules
      =
final rule set
```

Workflow usage example:

```yaml
- uses: michyweb/github-supply-chain-review-action@<FULL_COMMIT_SHA>
  with:
    rules-file: security/custom-executable-script.yml
    rules-mode: replace
```

Custom `rules-file` example for `replace`:

```yaml
rules:
  - id: company-custom-executable-script
    name: Company custom executable script detection
    paths:
      - "(^|/)package\.json$"
      - "(^|/)scripts/.*\.(sh|bash|zsh|ps1)$"
    patterns:
      - "curl\\s+[^|\\n]+\\|\\s*(bash|sh)"
      - "wget\\s+[^|\\n]+-O-\\s*\\|\\s*(bash|sh)"
      - "Invoke-WebRequest\\s+.*\\|\\s*iex"
```

Behavior on findings:

- The workflow still starts and this action runs normally.
- If findings are detected, the action exits with code `1` and marks the step/job as failed.
- Other jobs only continue if your workflow explicitly allows it (for example with `if: always()`).

## Disable selected default rules

Use `disabled_rules` to turn off specific built-in checks while keeping `merge` mode.

```yaml
disabled_rules:
  - npm-package-scripts
  - npm-native-bindings

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
