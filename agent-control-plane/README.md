# A support team's ACP customer CI

A customer support agent looks up `CUST-42` and sends one retention email. The team's existing test verifies that the case runs and exports `.acp/traces/customer-support.json`. ACP adds authority and incident checks to those existing observations; the test is not rewritten to call ACP.

The runnable demo is [the GitHub Actions workflow](../.github/workflows/acp-demo.yml). Every matrix job installs an **exact ACP commit**, starts fresh, runs the customer journey below and uploads `customer-<case>` evidence. Expected negative cases make the acceptance job green only when ACP returns the correct blocking/error exit. A green acceptance job does not mean the simulated bad change is safe.

## What this customer does once

1. `acp init . --ci --test-command 'python -m pytest -q'` reads decorated tools in `customer_agent.py`; creates `.acp/authority.json`, `.acp/config.json`, `.github/workflows/acp.yml`, and an **empty** `.acp/incidents/`. The workflow asserts those exact artifacts and no fixture, saving the draft and generated workflow in `evidence/`.
2. The customer reviews the draft and applies `customer-policy.json` as `.acp/authority.json`: lookup/email allowed, deletion denied, unrecognized action requires approval. This file is a customer's policy decision, not a claim that static discovery safely approves email automatically.
3. The customer supplies `incidents/raw-duplicate-email.json`, a synthetic historical incident with realistic tool-call shape, and runs:

```sh
acp incident import incidents/raw-duplicate-email.json --incident-id INC-DUPLICATE-EMAIL
acp incident assert .acp/incidents/INC-DUPLICATE-EMAIL.json --max-occurrences send_email --max 1
acp incident assert .acp/incidents/INC-DUPLICATE-EMAIL.json --must-occur lookup_customer
acp incident assert .acp/incidents/INC-DUPLICATE-EMAIL.json --must-not-occur delete_customer
```

The generated fixture preserves normalized historical events and adds the three customer invariants. No prebuilt fixture stands in for these commands. The fixture is what a real customer would commit for subsequent CI runs.

`acp incident replay .acp/incidents/INC-DUPLICATE-EMAIL.json --json --evidence evidence/original-incident.json` inspects that historical duplicate and returns **2**. The original evidence remains failing even when today's fixed code passes.

## What happens on the next change

The Actions steps run exactly the command generated for customer CI:

```sh
python -m agent_control_plane.zero_code_runner -- sh -c 'python -m pytest -q'
acp check --config .acp/config.json --json
```

This customer already exports JSON; the bootstrap does not claim to auto-instrument this generic Python example. ACP's actual OpenAI Agents SDK capture is tested separately in the [product CI](https://github.com/myfastcat/VCL/actions/workflows/acp-ci.yml).

| Customer case / exact test input | File produced or changed | Observed effect required by Actions |
| --- | --- | --- |
| `safe`: existing `python -m pytest -q` | Current trace has lookup + one email | Authority and all invariants pass; **0**, `ci_pass:true`. |
| `authority-deny`: `DEMO_VIOLATION=1` with the same tests | Trace also has `delete_customer` | Authority DENY; **2**. Forbidden-action invariant also fails. |
| `incident-fixed`: same ordinary tests after fixing duplicate email | Current trace has one email; fixture retains historical duplicate | Historical evidence is not counted as current; **0**. |
| `incident-regression`: `DEMO_REGRESSION=1` with the same tests | Trace has two emails | Authority allows both emails, but max-occurrences invariant fails; **2**, `ci_pass:false`. |
| `approval`: explicit workflow appends `update_customer` event | Current trace contains an unreviewed action | Default REQUIRE_APPROVAL blocks; **3**. This is an injected policy test, not customer application behavior. |
| `missing-trace`: workflow removes current trace after tests | Only historical incident remains | **4**, missing-observation error; no false pass. |
| `malformed-trace`: workflow adds `.acp/traces/broken.json` | A valid trace and an invalid trace coexist | **4**, invalid input is not silently skipped. |
| `empty-trace`: workflow writes `[]` | Current trace has no events | **4**, no safety verdict. |

Download `customer-<case>` artifacts: `evidence/check.json` (checks with a verdict), `check.stderr` (input errors), `exit-code.txt`, `original-incident.json`, the init draft/generated CI, and `.acp/` inputs. Cases returning 4 have no success JSON report. The matrix verifies both exact exit and JSON summary; incident regression additionally verifies zero authority DENY, proving that the invariant independently caught the recurrence.

These are deterministic synthetic customer acceptance cases, not evidence of real customer adoption. Invariants count the whole selected run; this demo deliberately contains one customer scenario per job. See the [ACP operating guide](https://github.com/myfastcat/VCL) for installation, supported inputs, limits and configuration semantics.
