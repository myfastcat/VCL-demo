# Agent Control Plane — Customer CI Demo

This demo shows ACP exactly from a customer's point of view: **what the customer runs, which files those commands produce, what CI runs afterward, and what the customer sees in concrete cases.**

There is no separate demo script. The GitHub Actions workflow itself is the demo because ACP is meant to be used as a CI gate.

## Customer scenario

The simulated company has a customer-support agent in `customer_agent.py`. Its existing application test is `tests/test_customer_agent.py`.

The agent normally calls:

- `lookup_customer`
- `send_email`

The customer wants two protections:

- `delete_customer` must never be called by this support agent;
- a previous production incident in which the same retention email was sent twice must never recur.

## 1. What the customer would run once during setup

In a real repository the customer would install ACP and initialize the CI integration once:

```bash
python -m pip install "git+https://github.com/myfastcat/VCL.git#subdirectory=agent-control-plane"
acp init . --ci --test-command "pytest -q"
```

That produces the customer-owned ACP files:

```text
.acp/authority.json
.acp/config.json
.github/workflows/acp.yml
.acp/incidents/
```

This demo already contains the equivalent configured files so the repository represents the state **after** that one-time setup:

| Demo file | Customer meaning |
|---|---|
| `.acp/authority.json` | business authority boundary |
| `.acp/config.json` | ACP trace + incident discovery and CI failure policy |
| `.acp/incidents/INC-DUPLICATE-EMAIL.json` | durable regression rule learned from a past incident |
| `.github/workflows/acp-demo.yml` | customer-shaped CI workflow used to demonstrate the behavior |

The demo authority contract specifically says:

```text
lookup_customer  → ALLOW
send_email       → ALLOW
delete_customer  → DENY
```

## 2. What CI runs for each normal code change

A developer does not run ACP by hand for every PR. The CI workflow runs the customer's existing test and then ACP.

In this demo the relevant commands are:

```bash
pytest -q
acp check --config .acp/config.json
```

The first command exercises the customer agent. `customer_agent.py` writes the observed tool-call behavior to:

```text
.acp/traces/customer-support.json
```

The second command consumes that current-run trace plus the committed customer rules:

```text
.acp/authority.json
.acp/incidents/*.json
```

and produces a CI result.

Its summary has this shape:

```text
events=<N> allow=<N> approval=<N> deny=<N> incident_regressions=<N> incident_failures=<N> avg_risk=<...> ci_pass=<true|false>
```

Exit `0` means the PR may continue. Exit `2` means ACP observed either a denied action or a recurrence of a committed incident pattern.

Now look at the actual customer cases.

## Case 1 — normal support-agent change

### Customer/CI command

```bash
pytest -q
acp check --config .acp/config.json
```

### Trace produced by the customer's test

`.acp/traces/customer-support.json` contains the current run's normal behavior:

```text
lookup_customer
send_email
```

### ACP effect

Both actions are `ALLOW`, and the duplicate-email incident rule is also satisfied because `send_email` occurs only once.

Expected result:

```text
customer test → PASS
ACP check     → exit 0 / PASS
```

The concrete workflow job is `safe-change` in `.github/workflows/acp-demo.yml`.

## Case 2 — a PR introduces an unauthorized customer deletion

The demo uses an environment flag only to simulate the bad code change. From ACP's point of view this is simply a PR whose existing customer test now exercises different agent behavior.

### Customer/CI command for this simulated PR

```bash
DEMO_VIOLATION=1 pytest -q
acp check --config .acp/config.json
```

### Trace produced

`.acp/traces/customer-support.json` now includes:

```text
lookup_customer
send_email
delete_customer
```

### ACP effect

The ordinary application test still passes because it is not an authority-policy test. ACP reads `.acp/authority.json`, matches `delete_customer` to `DENY`, and blocks the CI gate.

Expected result:

```text
customer test → PASS
ACP check     → exit 2 / BLOCK
reason        → denied authority action: delete_customer
```

The concrete workflow job is `authority-violation`.

## 3. How this customer learned from a real production incident

The company previously had a production incident in which the same retention email was sent twice.

The raw historical evidence for this demo is:

```text
incidents/raw-duplicate-email.json
```

A real customer would perform this incident-learning step once:

```bash
acp incident import incidents/raw-duplicate-email.json \
  --incident-id INC-DUPLICATE-EMAIL
```

That produces:

```text
.acp/incidents/INC-DUPLICATE-EMAIL.json
```

Then the customer records the business invariant:

```bash
acp incident assert .acp/incidents/INC-DUPLICATE-EMAIL.json \
  --max-occurrences send_email \
  --max 1
```

That updates the same file with the durable rule:

```json
{
  "type": "max_occurrences",
  "action": "send_email",
  "max": 1
}
```

This demo already commits that resulting fixture at `.acp/incidents/INC-DUPLICATE-EMAIL.json`, exactly as a customer would after completing the one-time incident-learning step.

No new per-PR command is added after this. Normal CI keeps running `acp check`, and ACP discovers the incident rule automatically.

## Case 3 — the historical incident is fixed

### Customer/CI command

```bash
pytest -q
acp check --config .acp/config.json
```

### Current trace produced

```text
lookup_customer
send_email
```

### ACP effect

ACP discovers `.acp/incidents/INC-DUPLICATE-EMAIL.json` and checks its invariant against the **current run**. `send_email` occurs once, so the historical incident remains fixed.

Expected result:

```text
customer test → PASS
ACP check     → exit 0 / PASS
incident      → INC-DUPLICATE-EMAIL passed=true
```

The concrete workflow job is `incident-fixed`.

## Case 4 — a later PR reintroduces the duplicate-email incident

Again, the environment flag exists only to simulate a regressing customer code change.

### Customer/CI command for this simulated PR

```bash
DEMO_REGRESSION=1 pytest -q
acp check --config .acp/config.json
```

### Current trace produced

```text
lookup_customer
send_email
send_email
```

### ACP effect

`send_email` itself is still `ALLOW`, so the authority boundary alone would not catch this problem. ACP then applies the committed incident rule and sees two calls where the maximum is one.

Expected result:

```text
customer test → PASS
ACP check     → exit 2 / BLOCK
reason        → INC-DUPLICATE-EMAIL regression: send_email occurred 2 > 1
```

The concrete workflow job is `incident-regression`.

## What this demo proves

The customer's operating model is intentionally small:

```text
ONE TIME
install/init → review authority → commit ACP files
incident happens → import trace → add invariant → commit incident file

EVERY PR
existing customer tests → trace/output artifact → acp check → PASS or BLOCK
```

The demo therefore proves the relationship between **customer command → produced artifact → ACP decision**, rather than presenting ACP as a collection of unrelated commands.

## Where to inspect the concrete implementation

- `.github/workflows/acp-demo.yml` — the actual customer-shaped CI cases.
- `.acp/authority.json` — the exact authority decisions used in the cases.
- `.acp/config.json` — the trace/incident discovery configuration.
- `.acp/incidents/INC-DUPLICATE-EMAIL.json` — the exact committed incident rule.
- `customer_agent.py` — the simulated customer agent and generated trace artifact.
- `tests/test_customer_agent.py` — the ordinary customer application test.

ACP customer-demo status is only `VERIFIED` when this repository's GitHub Actions workflow passes in addition to ACP's own product CI.
