# ACP demo：客服 Agent 发邮件，CI 检查越权和重复发送

客户场景：查询 `CUST-42`，发送一封挽留邮件。允许查询和发邮件，禁止删除客户；曾发生的“重复发邮件”不能复发。

**[运行 CI / 查看结果](https://github.com/myfastcat/demo/actions/workflows/acp-demo.yml)** · [workflow 源码](../.github/workflows/acp-demo.yml) · [ACP 使用说明](https://github.com/myfastcat/ACP)

## 客户做什么，生成什么

| 操作 | 输入 → 产出 |
|---|---|
| `acp init . --ci --test-command 'python -m pytest -q'` | 客户工具代码 → `.acp/authority.json`、`.acp/config.json`、`.github/workflows/acp.yml`；incident 只建空目录 |
| 审阅权限：`cp customer-policy.json .acp/authority.json` | 客户确认的权限 → 允许查客户/发邮件，禁止删除，其他操作要求审批 |
| `acp incident import incidents/raw-duplicate-email.json --incident-id INC-DUPLICATE-EMAIL` | 客户提供的历史 trace → `.acp/incidents/INC-DUPLICATE-EMAIL.json` |
| `acp incident assert .acp/incidents/INC-DUPLICATE-EMAIL.json --max-occurrences send_email --max 1` | 客户指定“最多发一次” → 写入 fixture；CI 还添加必须查询、禁止删除两条 invariant |

**实跑记录（2026-09-08）：[8/8 场景验收通过](https://github.com/myfastcat/demo/actions/runs/34181213535)，VERIFIED。** Demo commit `709fa8c`；固定安装 ACP `1d8690a`。下表 case 链接直达本次 job。

## 每次改代码后自动做什么

```sh
python -m agent_control_plane.zero_code_runner -- sh -c 'python -m pytest -q'
acp check --config .acp/config.json --json
```

复用现有测试，生成当前行为 `.acp/traces/customer-support.json`；ACP 按权限和 incident invariant 检查它。历史 trace 保留作证据，不充当本次行为。

| CI case | 本次操作 / 输入 | 本次实际效果 |
|---|---|---|
| [safe](https://github.com/myfastcat/demo/actions/runs/34181213535/job/101920539477) | 正常运行：查询 + 发一封邮件 | **PASS / 0** |
| [authority-deny](https://github.com/myfastcat/demo/actions/runs/34181213535/job/101920539317) | `DEMO_VIOLATION=1`：额外删除客户 | **BLOCK / 2**，权限 DENY |
| [incident-fixed](https://github.com/myfastcat/demo/actions/runs/34181213535/job/101920539375) | 历史有重复邮件，本次只发一封 | **PASS / 0**，修复有效 |
| [incident-regression](https://github.com/myfastcat/demo/actions/runs/34181213535/job/101920539416) | `DEMO_REGRESSION=1`：本次发两封 | **BLOCK / 2**，虽有发信权限，仍违反“最多一次” |
| [approval](https://github.com/myfastcat/demo/actions/runs/34181213535/job/101920539451) | workflow 注入未审阅的 `update_customer` | **APPROVAL / 3**，CI 阻断 |
| [missing-trace](https://github.com/myfastcat/demo/actions/runs/34181213535/job/101920539434) | workflow 删除本次 trace | **ERROR / 4**，不把历史证据当通过 |
| [malformed-trace](https://github.com/myfastcat/demo/actions/runs/34181213535/job/101920539420) | workflow 增加损坏 JSON | **ERROR / 4**，不忽略坏文件 |
| [empty-trace](https://github.com/myfastcat/demo/actions/runs/34181213535/job/101920539364) | workflow 将本次 trace 改成 `[]` | **ERROR / 4**，没有行为证据 |

打开 CI 的 **Summary** 看每个 case 的实际退出码、PASS/BLOCK/ERROR 和失败原因。展开 **Customer CI gate and acceptance of exact result** 看原始输出；下载 `customer-<case>` artifact 看 `check.json`、`check.stderr`、`exit-code.txt` 及生成的配置/fixture。

**验收 CI 绿色 = 每个场景得到了应有结果，包括成功拦截坏行为。** 此 demo 使用模拟客户数据和已有 JSON 导出；不是实际发送邮件、删除客户或真实客户采用证明。没有 `demo.sh`。
