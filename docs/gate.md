# Gate Command (`gate`)

Check whether an SBOM version passes your organization's policies, and exit
non-zero when it does not. Designed for CI pipelines: run it after `upload`
and the exit code blocks the pull request.

## Usage

```bash
python3 pylynk.py gate --prod <product-name> --env <environment> --ver <version> [OPTIONS]
python3 pylynk.py gate --verId <version-id> [OPTIONS]
```

An explicit version is required (either `--ver` or `--verId`). The
latest-version fallback used by other commands is disabled here because it is
racy when parallel CI runs upload versions concurrently.

Run `gate` after `upload`. The command waits for asynchronous version creation
and policy evaluation, prints the final verdict, and returns an exit code that
CI can use to pass or fail the job.

## Options

| Option | Description |
|--------|-------------|
| `--prod` | Product name |
| `--env` | Environment name (optional, defaults to 'default') |
| `--ver` | Version name (mutually exclusive with `--verId`) |
| `--verId` | Version ID (mutually exclusive with `--ver`) |
| `--fail-on` | Lowest policy severity that blocks: `fail` (default) or `warn` |
| `--policy-name` | Gate on one active policy by exact name (mutually exclusive with `--policy-id`) |
| `--policy-id` | Gate on one active policy by ID (mutually exclusive with `--policy-name`) |
| `--no-wait` | Check the current state once instead of waiting for the policy scan |
| `--timeout` | Total seconds to wait for version resolution and policy scan (default: 600) |
| `--poll-interval` | Seconds between polling attempts (default: 15) |
| `--output` | Output format: `table` (default) or `json` |
| `--token` | Security token (can also use `INTERLYNK_SECURITY_TOKEN` env var) |
| `-v, --verbose` | Enable verbose/debug output |

## Statuses and Exit Codes

| Status | Exit | Meaning |
|--------|------|---------|
| `PASS` | 0 | All active policies evaluated; no blocking violations |
| `NO_POLICIES` | 0 | No active policies configured for the organization (a warning is printed) |
| `FAIL` | 3 | At least one active policy of blocking severity was violated |
| `IN_PROGRESS` | 4 | Scan still queued or running when the timeout was reached |
| `ERROR` | 4 | Evaluation incomplete or errored, such as an interrupted scan |
| `NOT_EVALUATED` | 4 | No policy scan applies, such as vulnerability scanning disabled for the environment |

Two exits carry no status, because the gate never got a verdict:

| Exit | Meaning |
|------|---------|
| `1` | Authentication, network, or resolution failure, including a missing `--verId` or `--prod --ver` combination |
| `2` | Arguments rejected by the parser |

Treat any non-zero exit as blocking in CI. `3` and `4` are separate so you can
alert differently on a real policy failure than on a scan that never completed.
Exit `4` is the fail-closed case: an incomplete scan never passes.

Only policies with severity `fail` block by default. Use `--fail-on warn` to
also block on `warn`-severity policies. Violations of non-blocking severities
are still listed in the output.

Use `--policy-name` or `--policy-id` to gate on a single active policy instead
of all active policies. Policy names are matched case-insensitively, and the
command fails if the name is missing or ambiguous.

When a single policy is selected, the `Policies evaluated` count and the
violating policy table only include that policy.

## How Waiting Works

Policy evaluation runs asynchronously after upload (it is chained after the
vulnerability scan), so `gate` waits by default:

1. If `--prod/--ver` names are given, it retries resolution until the
   uploaded version appears.
2. It then polls the policy verdict until the scan finishes or `--timeout`
   is reached.

Both phases share the single `--timeout` budget. On timeout the gate exits
`4` (fail closed).

## Requirements

- The security token's organization role must grant the `view_policies`
  permission (all built-in roles include it).
- `--ver` must match the primary component version embedded in the uploaded
  SBOM (the same value shown by `pylynk vers`).

## Examples

```bash
# Gate on the version uploaded by this CI run
python3 pylynk.py gate --prod 'my-product' --env 'default' --ver 'v1.2.3'

# Block on warnings too, with a longer budget for large SBOMs
python3 pylynk.py gate --prod 'my-product' --ver 'v1.2.3' --fail-on warn --timeout 900

# Gate on one policy by name
python3 pylynk.py gate --prod 'my-product' --env 'default' --ver 'v1.2.3' --policy-name 'No criticals'

# One-shot check of an existing version, machine-readable
python3 pylynk.py gate --verId 'abc-123' --no-wait --output json
```

## Example Output

Passing gate:

```text
Policy gate: PASS
  Policies evaluated: 3 (passed: 2, failed: 0, warned: 1, skipped: 0, errored: 0)
```

Failing gate:

```text
Policy gate: FAIL
  Policies evaluated: 2 (passed: 1, failed: 1, warned: 0, skipped: 0, errored: 0)

POLICY       | SEVERITY | VIOLATIONS
-------------|----------|-----------
No criticals | fail     | 4
```

Single-policy gate:

```bash
python3 pylynk.py gate \
  --prod fails \
  --env default \
  --ver 4.0.0 \
  --timeout 600 \
  --policy-name 'Highly_Exploitable_EPSS_Vulnerability'
```

```text
Policy scan in progress (run: NOT_STARTED), retrying in 15s... [599s left]
Policy gate: FAIL
  Policies evaluated: 1 (passed: 0, failed: 1, warned: 0, skipped: 0, errored: 0)

POLICY                                | SEVERITY | VIOLATIONS
--------------------------------------|----------|-----------
Highly_Exploitable_EPSS_Vulnerability | fail     | 1
```

JSON output:

```bash
python3 pylynk.py gate --prod 'my-product' --env 'default' --ver 'v1.2.3' --output json
```

```json
{
  "status": "FAIL",
  "policyRunStatus": "FINISHED",
  "evaluatedAt": "2026-08-18T22:31:00Z",
  "counts": {
    "total": 1,
    "failed": 1,
    "warned": 0,
    "passed": 0,
    "errored": 0,
    "skipped": 0
  },
  "violatingPolicies": [
    {
      "policyId": "00000000-0000-0000-0000-000000000000",
      "policyName": "No criticals",
      "resultType": "fail",
      "violationsCount": 4
    }
  ]
}
```

## GitHub Actions Example

```yaml
jobs:
  sbom-policy-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Generate SBOM
        run: |
          # Your SBOM generation command here

      - name: Upload SBOM to Interlynk
        env:
          INTERLYNK_SECURITY_TOKEN: ${{ secrets.INTERLYNK_TOKEN }}
        run: |
          python3 pylynk.py upload --prod 'my-product' --env 'default' --sbom sbom.json

      - name: Policy gate (blocks PR on failure)
        env:
          INTERLYNK_SECURITY_TOKEN: ${{ secrets.INTERLYNK_TOKEN }}
        run: |
          python3 pylynk.py gate --prod 'my-product' --env 'default' \
            --ver "${{ github.sha }}" --timeout 600
```

The upload step automatically attaches PR metadata (PR number, commit SHA,
repository) from the CI environment; see [docs/ci-cd.md](ci-cd.md).

## Testing Locally

```bash
export INTERLYNK_API_URL=http://localhost:3000/lynkapi
export INTERLYNK_SECURITY_TOKEN=your_test_token

# Create a fail-severity policy in the UI that your SBOM violates, then:
python3 pylynk.py upload --prod test --env default --sbom sample.json
python3 pylynk.py gate --prod test --env default --ver <version>; echo "exit: $?"
# expect: exit 3 with the failing policy listed

# Gate on only one active policy
python3 pylynk.py gate --prod test --env default --ver <version> --policy-name 'No criticals'

# Race check: stop the backend's sidekiq worker, re-upload, then
python3 pylynk.py gate --prod test --env default --ver <version> --timeout 30; echo "exit: $?"
# expect: exit 4 (fail closed - never a false pass while the scan is queued)
```
