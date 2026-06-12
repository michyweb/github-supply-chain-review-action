# Threat model

This action focuses on pull request changes that can alter trust boundaries and software delivery behavior.

## Source code

Application code can contain malicious logic, but many campaigns avoid direct code-only signals and instead tamper with adjacent control files.

## Build files

Build scripts and manifests can execute arbitrary commands, download payloads, or alter release artifacts.

## CI/CD

Workflow definitions control what runs in automation and with which permissions. Small edits can bypass security checks or exfiltrate secrets.

## IDE configuration

Workspace-level settings and tasks can influence local developer behavior and execution flows.

## AI instructions

Instruction files for coding agents can redirect automated edits and reviews toward unsafe outcomes.

## MCP

Model Context Protocol configuration can grant tool access and runtime capabilities, making it a high-impact trust surface.
