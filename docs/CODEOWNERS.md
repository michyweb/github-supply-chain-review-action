## Protecting the configuration with CODEOWNERS

This Action helps detect suspicious changes, but the protection itself should also be protected.

Recent campaigns such as **Miasma** have shown that attackers increasingly target trust relationships rather than software vulnerabilities. A compromised account or automated tool could attempt to:

- modify the caller workflow;
- disable existing rules;
- replace the rule set with a weaker one;
- introduce exceptions that hide malicious changes.

To reduce this risk, it is recommended to protect both the workflow and the rule file with `CODEOWNERS`.

Example:

```text
# Require security review for supply chain review configuration
security/supply-chain-rules.yml @michyweb/supply-chain-security-reviewers

# Require security review for the caller workflow
.github/workflows/supply-chain-review.yml @michyweb/supply-chain-security-reviewers
```

With branch protection enabled and "Require review from Code Owners" turned on, changes to these files will require approval from the designated security team.

This creates an additional layer of defence against Human-in-the-Loop Supply Chain Attacks and helps prevent a Miasma-like variant from silently weakening the controls intended to detect it.

### Why this matters

Without CODEOWNERS:

```text
Attacker
    ↓
Modify workflow or rules
    ↓
Reduce detection
    ↓
Merge changes
```

With CODEOWNERS:

```text
Attacker
    ↓
Modify workflow or rules
    ↓
Security review required
    ↓
Suspicious changes detected before merge
```

While CODEOWNERS alone is not sufficient, it significantly raises the difficulty of tampering with the protection mechanisms themselves.
