GitHub Enterprise supports Required reviewers for environments  [GitHub documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments). This feature does not prevent malicious workflows from being triggered. Instead, jobs targeting protected environments are paused and remain in a waiting state until explicitly approved by a designated reviewer. Environment secrets are not injected into the runner while the job is awaiting approval, preventing unauthorized access to sensitive credentials despite the workflow having already started execution.

The protection only applies to Environment secrets and only when:

The workflow references an environment using environment: <name>.
Sensitive credentials are stored as Environment secrets.
The environment has Required reviewers configured.

Without approval, secrets are not injected into the runner.

This protection does not apply to:

Repository secrets;
Organization secrets;
Secrets inherited through reusable workflows;
Repository or environment variables;
Credentials committed directly into the repository.

These secrets remain accessible to any workflow that is allowed to run.

In private repositories using GitHub Free, Pro or Team, environments and environment secrets are available, but Required reviewers are not supported. Consequently, jobs referencing an environment execute automatically and environment secrets are injected without any manual approval step. Therefore, environment secrets in these plans should not be considered a security boundary against malicious workflow execution, as a malicious workflow could access and exfiltrate them.

Organizations using GitHub Team or lower with private repositories have no native mechanism to prevent the automatic execution of workflows before environment secrets are exposed.

For this reason, the rule that detects modifications to files under .github/workflows/ is currently disabled. Although changes to workflows may represent a supply chain risk, simply detecting their presence does not provide meaningful protection in environments where workflows are executed automatically. In practice, a malicious workflow introduced through a pull request would still run and could access repository, organization, or environment secrets (when environment reviewers are unavailable).

As a result, enabling this rule would generate findings that users may not be able to effectively mitigate without upgrading to GitHub Enterprise or redesigning their secret management strategy. To avoid producing recommendations that cannot be enforced in common GitHub configurations, the workflow detection rule remains commented out by default.