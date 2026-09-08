# Customer demos

One directory per product. GitHub Actions shows the actual customer experience: a passing gate is green; a blocking/error gate is red.

| Product | Customer scenario | CI |
|---|---|---|
| [ACP](agent-control-plane/) | Support agent: normal email, unauthorized deletion, duplicate email, approval, and missing traces | [Customer CI — real pass/block](https://github.com/myfastcat/demo/actions/workflows/acp-customer-ci.yml) |

[Engineering acceptance](https://github.com/myfastcat/demo/actions/workflows/acp-demo.yml) separately verifies expected outcomes.
