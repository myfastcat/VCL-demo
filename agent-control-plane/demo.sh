#!/usr/bin/env bash
set -euo pipefail

python -m pip install -U pip
python -m pip install pytest
python -m pip install "git+https://github.com/myfastcat/VCL.git#subdirectory=agent-control-plane"

rm -rf .acp/traces
pytest -q
acp validate .acp/authority.json
acp check --config .acp/config.json

echo
echo "SAFE FLOW: PASS"
echo
echo "Now injecting a simulated authority violation..."
rm -rf .acp/traces
DEMO_VIOLATION=1 pytest -q
set +e
acp check --config .acp/config.json
status=$?
set -e

if [ "$status" -ne 2 ]; then
  echo "Expected ACP exit code 2 for DENY, got $status"
  exit 1
fi

echo
echo "VIOLATION FLOW: ACP BLOCKED delete_customer as expected"
