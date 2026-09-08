# Shared customer demos

One product per directory; product source lives in its own repository. Each demo's GitHub Actions workflow is the customer CI example and acceptance harness. There is no `demo.sh`.

| Product | Customer case | Acceptance workflow |
| --- | --- | --- |
| [Agent Control Plane](agent-control-plane/) | Support agent: authorized retention email, accidental deletion, duplicate-email regression, approval, missing/invalid observations | [ACP customer acceptance](.github/workflows/acp-demo.yml) |

The requested rename from `myfastcat/VCL-demo` to `myfastcat/demo` is pending a settings-capable authenticated session. This remains the shared demo repository at its current URL until confirmed; no completed rename is implied.
