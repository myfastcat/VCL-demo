# Agent Control Plane — Customer CI Demo

This directory imitates how a customer uses ACP in a real engineering workflow. The demo is organized around the customer's journey, not ACP's internal commands.

## 1. Set the boundary

The simulated company has a customer-support agent. Its ordinary tests already exercise actions such as `lookup_customer` and `send_email`.

The customer makes one business decision in `.acp/authority.json`:

- customer lookup is allowed;
- sending the retention email is allowed;
- deleting a customer is denied.

The customer does not create a second ACP-specific test suite. ACP uses the behavior already exercised by the normal application tests.

## 2. Protect every change automatically

After setup, the developer's normal action is just to push code or open a PR.

The acceptance workflow proves this CI path:

```text
Existing customer tests
        ↓
Tool-call behavior is captured/discovered
        ↓
ACP checks authority boundaries
        +
ACP checks known incident regressions
        ↓
PASS or CI BLOCKED
```

The safe scenario calls `lookup_customer` and `send_email`, so both the customer test and ACP pass.

The authority-violation scenario makes the agent call `delete_customer`. The ordinary application test deliberately remains green, but ACP sees the current behavior, matches the `DENY` rule, and blocks the gate.

This is the value ACP adds: the customer keeps the tests they already own, while CI gains a separate safety judgment over the behavior those tests exercised.

## 3. Learn from incidents

The demo also models a real production-learning loop.

The company previously had a duplicate-email incident. `send_email` itself remains allowed, so banning the tool would be the wrong fix. Instead, the historical incident creates a more specific invariant: for this regression scenario, `send_email` may occur at most once.

The historical trace lives in `incidents/raw-duplicate-email.json`; the durable regression rule is created under `.acp/incidents/`.

The acceptance flow proves both sides:

- **fixed behavior:** the current run sends one email, so the historical incident rule passes;
- **incident returns:** the current run sends two emails, the normal application test still passes, but ACP recognizes recurrence and blocks CI.

The important product behavior is that ACP evaluates the incident invariant against the **current run's observed behavior**. The old incident is retained as evidence; it does not make every future build fail forever.

## 4. Understand why CI blocked

A customer should not receive a mysterious red build.

The demo shows two different reasons ACP can block a change:

- **Authority boundary failure:** the agent attempted something it was never authorized to do (`delete_customer`).
- **Incident regression failure:** the underlying action is allowed, but a previously observed bad pattern returned (duplicate `send_email`).

ACP's exit/result semantics let CI distinguish a policy/regression block from invalid or missing evaluation evidence.

## What ACP fits into

The demo intentionally uses systems a customer already has rather than inventing parallel workflow:

- `tests/test_customer_agent.py` — ordinary application tests, not ACP-specific tests;
- `.acp/authority.json` — the customer's business authority decision;
- `.acp/config.json` — how ACP connects to the existing traces and incident rules;
- `incidents/raw-duplicate-email.json` — historical evidence from production observability;
- `.github/workflows/acp-demo.yml` — automated CI acceptance;
- `demo.sh` — the repeatable acceptance harness used to prove the customer journey.

## Acceptance

The repository workflow runs the full customer-shaped journey on push/pull request. It installs ACP from `myfastcat/VCL` main at runtime and verifies safe behavior, authority blocking, fixed incident behavior, and recurrence blocking.

ACP is customer-demo `VERIFIED` only when this external workflow passes in addition to ACP's own internal CI.
