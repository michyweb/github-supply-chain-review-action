# Background: Miasma and Human-in-the-Loop Supply Chain Attacks

## Summary of Miasma

Miasma is a campaign family that highlights a shift from exploiting software bugs to exploiting trust relationships in development workflows.

## Why these rules exist

The rule set is designed to flag sensitive file changes and risky patterns in areas that can modify delivery pipelines, developer behavior, or automation outcomes.

## Trust surfaces

The most relevant trust surfaces include source code, build files, CI/CD workflows, IDE workspace configuration, AI instruction files, and MCP configuration.

## AI instructions

AI instruction files can silently influence how coding assistants reason, what they modify, and which safeguards they skip.

## MCP

MCP configuration can alter available tools and execution contexts for AI-enabled workflows, so tampering may expand attacker capabilities.

## Devcontainers

Devcontainers define development runtime behavior and can be abused to introduce malicious dependencies, startup commands, or execution hooks.
