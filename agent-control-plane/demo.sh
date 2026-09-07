#!/usr/bin/env bash
set -euo pipefail

python -m pip install -U pip
python -m pip install pytest
python -m pip install "git+https://github.com/myfastcat/VCL.git#subdirectory=agent-control-plane"

rm -rf .acp/traces .acp/incidents
mkdir -p .acp/incidents

# 1) Normal customer flow: application tests and ACP both pass.
pytest -q
acp validate .acp/authority.json
acp check --config .acp/config.json

echo
echo "SAFE FLOW: PASS"

# 2) Authority violation: app test still passes, ACP blocks delete_customer.
echo
echo "Injecting a simulated authority violation..."
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

echo "AUTHORITY FLOW: ACP BLOCKED delete_customer as expected"

# 3) Historical incident -> durable regression rule.
# The incident was a duplicate retention email. send_email is ALLOW, so this
# demonstrates regression protection independently from the authority gate.
echo
echo "Importing a historical incident and creating a regression invariant..."
acp incident import incidents/raw-duplicate-email.json --incident-id INC-DUPLICATE-EMAIL
acp incident assert .acp/incidents/INC-DUPLICATE-EMAIL.json --max-occurrences send_email --max 1

# Fixed behavior should pass even though the historical fixture records the old incident.
rm -rf .acp/traces
pytest -q
acp check --config .acp/config.json

echo "INCIDENT FIXED FLOW: PASS"

# Re-introduce the old behavior. Application test remains green; authority still
# allows send_email, but the committed incident invariant must fail the CI gate.
echo
echo "Re-introducing the historical duplicate-email regression..."
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

echo "INCIDENT REGRESSION FLOW: ACP BLOCKED recurrence as expected"
echo
echo "CUSTOMER DEMO: VERIFIED ALL MAJOR ACP FLOWS"
