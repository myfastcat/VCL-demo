from __future__ import annotations

import json
import os
from pathlib import Path


def lookup_customer(customer_id: str) -> dict:
    return {"id": customer_id, "plan": "pro", "status": "active"}


def send_email(customer_id: str, template: str) -> dict:
    return {"customer_id": customer_id, "template": template, "sent": True}


def delete_customer(customer_id: str) -> dict:
    return {"customer_id": customer_id, "deleted": True}


def run_support_case(customer_id: str = "CUST-42") -> list[dict]:
    events: list[dict] = []

    lookup_customer(customer_id)
    events.append({"action": "lookup_customer", "context": {"customer_id": customer_id}})

    send_email(customer_id, "retention_offer")
    events.append(
        {
            "action": "send_email",
            "context": {"customer_id": customer_id, "template": "retention_offer"},
        }
    )

    if os.getenv("DEMO_VIOLATION") == "1":
        delete_customer(customer_id)
        events.append({"action": "delete_customer", "context": {"customer_id": customer_id}})

    trace_path = Path(".acp/traces/customer-support.json")
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    trace_path.write_text(json.dumps(events, indent=2) + "\n", encoding="utf-8")
    return events
