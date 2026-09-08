# ACP customer demo

A support agent looks up `CUST-42` and sends one retention email. Customer policy allows lookup/email, forbids deletion, and requires approval for other actions. A past duplicate-email incident becomes a regression rule.

**[Customer CI: real green/red jobs](https://github.com/myfastcat/demo/actions/workflows/acp-customer-ci.yml)** · [Workflow source](../.github/workflows/acp-customer-ci.yml) · [ACP guide](https://github.com/myfastcat/ACP)

## Setup → generated files

| Customer action | Input → artifact |
|---|---|
| `acp init . --ci --test-command 'python -m pytest -q'` | Tool source → `.acp/authority.json`, `.acp/config.json`, `.github/workflows/acp.yml`; creates an empty incident directory |
| `cp customer-policy.json .acp/authority.json` | Customer-reviewed policy → authority rules |
| `acp incident import incidents/raw-duplicate-email.json --incident-id INC-DUPLICATE-EMAIL` | Historical trace → `.acp/incidents/INC-DUPLICATE-EMAIL.json` |
| `acp incident assert .acp/incidents/INC-DUPLICATE-EMAIL.json --max-occurrences send_email --max 1` | Customer decision → “send at most once” invariant; the workflow also requires lookup and forbids deletion |

**Verified run (2026-09-08): [2 green / 6 red customer jobs](https://github.com/myfastcat/demo/actions/runs/34181738343).** All six failures occurred at the ACP gate with the intended exit 2/3/4; setup and existing tests passed. [Engineering acceptance: 8/8 passed](https://github.com/myfastcat/demo/actions/runs/34181738356). Both ran demo commit `946b223`, installing ACP `1d8690a`.

## What the customer sees in CI

```sh
python -m agent_control_plane.zero_code_runner -- sh -c 'python -m pytest -q'
acp check --config .acp/config.json --json
```

Existing tests export `.acp/traces/customer-support.json`. ACP checks these current events against authority and incident rules. Historical events do not replace current observations.

| Case | Simulated change / input | Customer CI result |
|---|---|---|
| [safe](https://github.com/myfastcat/demo/actions/runs/34181738343/job/101922038386) | Lookup + one email | **Green — PASS, exit 0** |
| [authority-deny](https://github.com/myfastcat/demo/actions/runs/34181738343/job/101922038531) | `DEMO_VIOLATION=1`: also delete the customer | **Red — BLOCK, exit 2**, authority DENY |
| [incident-fixed](https://github.com/myfastcat/demo/actions/runs/34181738343/job/101922038396) | Historical duplicate; current run sends once | **Green — PASS, exit 0** |
| [incident-regression](https://github.com/myfastcat/demo/actions/runs/34181738343/job/101922038288) | `DEMO_REGRESSION=1`: send twice | **Red — BLOCK, exit 2**, `send_email occurred 2 > 1` |
| [approval](https://github.com/myfastcat/demo/actions/runs/34181738343/job/101922038416) | Workflow injects unreviewed `update_customer` | **Red — approval required, exit 3** |
| [missing-trace](https://github.com/myfastcat/demo/actions/runs/34181738343/job/101922038551) | Workflow removes the current trace | **Red — ERROR, exit 4**, no observations |
| [malformed-trace](https://github.com/myfastcat/demo/actions/runs/34181738343/job/101922038474) | Workflow adds invalid JSON | **Red — ERROR, exit 4**, invalid input |
| [empty-trace](https://github.com/myfastcat/demo/actions/runs/34181738343/job/101922038480) | Workflow replaces the trace with `[]` | **Red — ERROR, exit 4**, no events |

The customer gate returns ACP's actual exit code: no `continue-on-error`, no conversion of BLOCK to success. This demo runs all eight changes as separate jobs, so its overall run is intentionally red when the unsafe/error cases are blocked. A real customer runs the gate against their current change.

Open **Summary** for the verdict and reason, or the **ACP customer gate** step for raw output. Download `real-customer-<case>` for `check.json`, `check.stderr`, `exit-code.txt`, and generated configuration/fixtures.

[Engineering acceptance](https://github.com/myfastcat/demo/actions/workflows/acp-demo.yml) is separate: it checks expected exits and may be green when blocking works. Its green status is not the customer's CI result.

Synthetic data; no real emails or customer deletion. This example uses an existing JSON exporter. No `demo.sh`.
