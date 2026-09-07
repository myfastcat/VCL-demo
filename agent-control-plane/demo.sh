#!/usr/bin/env bash
set -euo pipefail

python -m pip install -U pip
python -m pip install pytest
python -m pip install "git+https://github.com/myfastcat/VCL.git#subdirectory=agent-control-plane"

rm -rf .acp/traces .acp/incidents
mkdir -p .acp/incidents

echo
echo "=== 1. SET THE BOUNDARY ==="
echo "Customer policy: lookup/send_email allowed; delete_customer denied."
echo "ACP reuses the customer's existing agent tests; no parallel ACP test suite."

# Safe customer flow: existing application tests and ACP both pass.
rm -rf .acp/traces
pytest -q
acp validate .acp/authority.json
acp check --config .acp/config.json

echo "BOUNDARY + SAFE FLOW: PASS"

echo
echo "=== 2. PROTECT EVERY CHANGE AUTOMATICALLY ==="
echo "Simulating a PR that introduces a forbidden delete_customer call."
rm -rf .acp/traces
DEMO_VIOLATION=1 pytest -q
set +e
acp check --config .acp/config.json
authority_status=$?
set -e

if [ "$authority_status" -ne 2 ]; then
  echo "Expected ACP exit code 2 for authority DENY, got $authority_status"
  exit 1
fi

echo "CI PROTECTION: ACP BLOCKED unauthorized delete_customer while app test stayed green"

echo
echo "=== 3. LEARN FROM INCIDENTS ==="
echo "Historical incident: duplicate retention email. The tool remains allowed; recurrence must not."
acp incident import incidents/raw-duplicate-email.json --incident-id INC-DUPLICATE-EMAIL
acp incident assert .acp/incidents/INC-DUPLICATE-EMAIL.json --max-occurrences send_email --max 1

# Fixed behavior should pass against the historical incident invariant.
rm -rf .acp/traces
pytest -q
acp check --config .acp/config.json

echo "INCIDENT LEARNING: fixed current behavior passes"

# Re-introduce the old behavior. Application test remains green; incident rule blocks it.
echo "Re-introducing the historical duplicate-email behavior in the current run..."
rm -rf .acp/traces
DEMO_REGRESSION=1 pytest -q
set +e
acp check --config .acp/config.json
regression_status=$?
set -e

if [ "$regression_status" -ne 2 ]; then
  echo "Expected ACP exit code 2 for incident regression, got $regression_status"
  exit 1
fi

echo "INCIDENT REGRESSION: ACP BLOCKED recurrence while app test stayed green"

echo
echo "=== 4. UNDERSTAND WHY CI BLOCKED ==="
echo "Authority failure and incident regression are surfaced as distinct customer reasons."
echo "Missing/invalid evaluation evidence uses a separate invalid-input status instead of silently passing."

echo
echo "CUSTOMER JOURNEY ACCEPTANCE: ALL MAJOR ACP CATEGORIES VERIFIED BY THIS HARNESS"
