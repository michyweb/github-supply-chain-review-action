# Workflow Configuration

## Coverage Requirements

The workflow enforces **80% minimum test coverage**. This is configured in `tests.yml`:

```yaml
coverage report -m --fail-under=80
```

To check coverage locally:

```bash
# Install coverage tool
pip install coverage

# Run tests with coverage tracking
coverage run -m unittest discover -s tests -p "test_*.py"

# Display coverage report
coverage report -m

# Generate HTML report (optional)
coverage html
# Open htmlcov/index.html in browser
```

## Python Version Matrix

Tests run on 3 Python versions to ensure compatibility:

| Version | Status | Notes |
|---------|--------|-------|
| 3.10 | ✅ Tested | End of support: Oct 2026 |
| 3.11 | ✅ Tested | End of support: Oct 2027 |
| 3.12 | ✅ Tested | Latest stable (Oct 2028) |

If a test fails on one version, the PR check will fail.

## Dependency Caching

The workflow uses pip caching to speed up dependency installation:

```yaml
cache: 'pip'
```

This caches `requirements.txt` based on its hash. When dependencies don't change, installation is instant.

## Artifact Retention

Test results are kept for 7 days:

```yaml
retention-days: 7
```

Access artifacts in the `Actions` tab under each workflow run.

## Concurrent Runs

The workflow runs on a matrix of Python versions:
- Each version runs independently
- Tests on 3.10, 3.11, 3.12 run in parallel
- Coverage job waits for all tests to complete
- Lint job runs independently

Total workflow time: ~2-3 minutes

## Environment

- **OS**: Ubuntu Latest (Ubuntu 24.04 LTS)
- **Shell**: bash
- **Python**: Multiple versions (3.10, 3.11, 3.12)
- **Permissions**: Minimal (read contents, write PR comments)
