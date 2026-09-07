# Agent Control Plane — Customer Demo

This directory is a simulated customer repository for demonstrating ACP to a buyer or engineering team. It shows the major customer-facing flows end to end: normal authority-safe behavior, an authority violation, and a historical incident turned into a regression gate.

## Run the demo

```bash
cd agent-control-plane
bash demo.sh
```

The script tells this story automatically:

1. **Safe flow** — the customer-support test emits tool-call traces and `acp check` passes.
2. **Authority violation** — the application test still passes, but the agent calls `delete_customer`; ACP sees the current trace, applies the authority contract, and exits `2`.
3. **Incident creation** — a historical duplicate-email trace is imported with `acp incident import`, then the customer records the business invariant with `acp incident assert ... --max-occurrences send_email --max 1`. No JSON editing is required.
4. **Fixed behavior** — the historical incident remains stored under `.acp/incidents/`, but the current test run sends one email, so the incident regression passes.
5. **Regression returns** — the application test still passes and `send_email` is still allowed by the authority policy, but the current run sends it twice. ACP evaluates the committed incident invariant against the current observed trace and exits `2`.

## Customer-shaped files

- `customer_agent.py` — simulated application/tool code.
- `tests/test_customer_agent.py` — ordinary application test that deliberately does not encode ACP policy.
- `.acp/authority.json` — authority boundary: lookup/email allowed, customer deletion denied.
- `.acp/config.json` — trace and incident discovery configuration.
- `incidents/raw-duplicate-email.json` — example historical production incident trace.
- `.acp/incidents/` — generated durable incident regression fixtures during the demo.
- `demo.sh` — repeatable customer/sales acceptance path.

## What the demo proves

ACP catches two different classes of failure that ordinary application tests may miss:

- **Authority regression:** the agent performs an action it is not authorized to perform.
- **Incident regression:** an action may still be authorized in general, but a specific previously observed bad behavior returns. In this demo, one retention email is allowed; sending it twice violates the learned incident invariant.

The important distinction is that incident fixtures preserve the historical incident as evidence, while CI evaluates their invariants against the **current run's observed tool-call events**. A past incident therefore does not fail forever; only recurrence in current behavior fails the build.

## Acceptance

The repository workflow `.github/workflows/acp-demo.yml` runs `bash demo.sh` on every relevant push or pull request. ACP is customer-demo `VERIFIED` only when this external, customer-shaped workflow passes in addition to the product's own internal CI.
