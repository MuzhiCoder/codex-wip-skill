# Codex WIP Skill

**中文 | English**

一个面向 OpenAI Codex 长任务的持久化工作连续性 Skill：支持**检查点（checkpoint）**、**交接（handoff）**、**灾难恢复（forensic recovery）**与**继续执行（resume）**。

A durable work-continuity Skill for long-running OpenAI Codex coding sessions, providing **checkpoint**, **handoff**, **forensic recovery**, and **resume** workflows.

---

## 中文说明

### 它解决什么问题

长时间运行的 Codex 编码任务，往往会形成大量只存在于当前会话中的上下文，例如：已经确认的设计决策、正在处理的缺口、测试状态、失败方案、下一步行动等。

当以下情况发生时，原会话可能无法继续打开：

- Codex 使用额度耗尽；
- 从 ChatGPT 账号登录切换到 API Key / 自定义 Provider；
- 使用 CC Switch 切换 Provider；
- 原 Codex conversation/thread 无法访问；
- Codex、终端或机器异常退出；
- 切换到另一台电脑继续开发；
- 长任务发生上下文压缩或上下文丢失。

此时，**代码通常还在，但“任务状态”可能丢失**。

`$wip` 的目标就是把这些关键工程状态持久化到仓库中，让新的 Codex Session 不依赖旧 conversation，也能够安全恢复并继续开发。

### 核心理念

> Conversation 不是连续性的边界。真正可靠的连续性来源应当是：**Git 仓库 + 可验证的 WIP 状态**。

Git 仍然是代码事实来源；`.codex/wip/current.md` 用于保存当前任务目标、确认过的决策、验证状态、阻塞项和精确的下一步行动。

### 支持的模式

| 命令 | 说明 |
| --- | --- |
| `$wip checkpoint` | 当前 Session 正常时创建轻量检查点 |
| `$wip handoff` | 准备切换账号、Provider、Session 或机器 |
| `$wip recover` | 原会话已经不可访问时，从 Git、测试、代码关系等证据恢复工作状态 |
| `$wip resume` | 验证现有检查点与当前仓库是否一致，并从已确认的下一步继续 |
| `$wip status` | 只检查 WIP 是否过期、是否发生仓库漂移，不修改业务代码 |

### 持久化状态

Skill 会在项目中使用：

```text
.codex/wip/
├── current.md
├── state.json
└── checkpoints/
    └── <timestamp>.json
```

其中：

- `current.md`：面向人和新 Codex Session 的任务状态说明；
- `state.json`：仓库、分支、HEAD、变更文件、worktree fingerprint 等机器可读元数据；
- `checkpoints/`：历史检查点记录。

### 安装

在 Windows 上：

```powershell
git clone https://github.com/MuzhiCoder/codex-wip-skill.git
cd codex-wip-skill
.\scripts\install.ps1
```

也可以手工复制仓库内容到：

```text
%USERPROFILE%\.codex\skills\wip
```

如果设置了 `CODEX_HOME`，安装脚本会使用：

```text
$env:CODEX_HOME\skills\wip
```

否则使用：

```text
$HOME\.codex\skills\wip
```

安装后，新建一个 Codex Session，并执行：

```text
$wip status
```

用于确认 Skill 已被发现。

### 典型场景：额度耗尽后切换 API Key

例如：

```text
ChatGPT Account Codex
        ↓
长时间开发任务
        ↓
额度耗尽 / 原会话无法继续
        ↓
CC Switch / API Key / Custom Provider
        ↓
新 Codex Session
```

如果旧 Session 已经无法继续，在**同一个代码仓库**中新建 Codex Session，然后执行：

```text
$wip recover
```

恢复流程会先禁止继续修改业务代码，然后检查：

1. 仓库中的 `AGENTS.md` 等项目指令；
2. 已存在的 `.codex/wip/` 状态；
3. `git status`、Git 历史和 diff 结构；
4. 新增或修改的测试；
5. 生产代码变更；
6. CodeGraph 或其他可用代码关系工具；
7. 定向构建与测试结果；
8. ADR、计划文件、TODO / FIXME；
9. 用户提供的截图或旧 Agent 输出作为辅助证据。

工作项会被分类为：

- `VERIFIED_DONE`
- `IMPLEMENTED_UNVERIFIED`
- `PARTIAL`
- `BLOCKED`
- `NOT_STARTED`
- `UNKNOWN`

恢复完成并检查报告后，再执行：

```text
$wip resume
```

### 跨 Provider / 跨机器交接

在准备切换 Provider、账号、Session 或机器之前运行：

```text
$wip handoff
```

如果迁移到另一台电脑，需要同时迁移：

1. **代码状态**；
2. **`.codex/wip/` 状态**。

推荐使用用户明确批准的 WIP Git 分支或 WIP commit 进行传输。

Skill **不会自动执行**以下操作：

- `git commit`
- `git push`
- `git reset --hard`
- `git clean`
- force push
- Git 历史重写

这些高影响操作始终应由用户明确决定。

### 证据模型

`current.md` 中的重要结论应标记为：

- `VERIFIED`：由测试、可执行行为、代码或权威项目文档直接支持；
- `INFERRED`：由 diff、调用关系或代码结构强烈推断，但尚未完全证明；
- `REPORTED`：来自旧 Agent、用户或截图，但尚未独立验证；
- `UNKNOWN`：当前证据不足。

这可以避免新的 Codex Session 把旧 handoff 中的推测误当成事实。

### 安全设计

`wip_snapshot.py` 默认只保存元数据，不持久化：

- 完整 diff 内容；
- 业务文件正文；
- 环境变量值；
- API Key；
- Access Token；
- Cookie；
- 密码；
- Authorization Header。

`wip_validate.py` 还会检查 `current.md` 中若干常见 Secret 标记。

### 测试

本地执行：

```powershell
python scripts/test_wip_snapshot.py
python scripts/test_wip_validate.py
```

GitHub Actions 会在 Windows 和 Linux 上，使用 Python 3.11–3.13 运行同一套测试。

### 仓库结构

```text
.
├── .github/workflows/test.yml
├── SKILL.md
├── agents/
│   └── openai.yaml
├── examples/
│   └── codex-wip.example.md
├── references/
│   ├── handoff-protocol.md
│   ├── recovery-protocol.md
│   └── wip-contract.md
└── scripts/
    ├── install.ps1
    ├── wip_snapshot.py
    ├── wip_validate.py
    ├── test_wip_snapshot.py
    └── test_wip_validate.py
```

### 推荐使用方式

不要等到额度已经耗尽才第一次保存 WIP。

建议在以下里程碑运行：

```text
$wip checkpoint
```

例如：

- RED 测试已经建立目标行为；
- GREEN 实现已经通过；
- 一个重要 blocker 已解决；
- 架构决策发生变化；
- 一个迁移/重构阶段完成；
- 准备进行长时间、高风险操作；
- 准备切换 Provider；
- 准备切换电脑；
- 剩余额度已经低到可能影响任务连续性。

这样，即使之后发生硬中断，也只需要恢复“最后一个 checkpoint 之后”的少量工作。

---

## English

### What problem does it solve?

Long-running Codex coding tasks accumulate valuable session-only context: confirmed design decisions, unfinished gaps, test status, rejected approaches, blockers, and exact next actions.

The original conversation may become unavailable when:

- Codex usage limits are exhausted;
- authentication changes from a ChatGPT account to an API key or custom provider;
- CC Switch is used to change providers;
- the original Codex conversation/thread becomes inaccessible;
- Codex, the terminal, or the machine crashes;
- development moves to another computer;
- a long task loses context or undergoes context compaction.

In these cases, **the code may still exist while the task state is lost**.

`$wip` persists that engineering state inside the repository so a fresh Codex session can recover and continue without depending on the original conversation.

### Core idea

> Conversation identity is not the continuity boundary. Reliable continuity should come from the **Git repository + verifiable WIP state**.

Git remains the source of truth for code. `.codex/wip/current.md` stores the durable task goal, confirmed decisions, verification state, blockers, and exact next actions.

### Modes

| Command | Purpose |
| --- | --- |
| `$wip checkpoint` | Persist a lightweight checkpoint while the current session is healthy |
| `$wip handoff` | Prepare for a provider/account/session/machine handoff |
| `$wip recover` | Reconstruct state from Git, tests, code relationships, and other evidence after a hard interruption |
| `$wip resume` | Validate checkpoint freshness against the repository and continue from the first verified next action |
| `$wip status` | Report checkpoint freshness and repository drift without changing business code |

### Durable project state

The skill stores continuity metadata under:

```text
.codex/wip/
├── current.md
├── state.json
└── checkpoints/
    └── <timestamp>.json
```

- `current.md`: human-readable continuity record for users and new Codex sessions;
- `state.json`: machine-readable repository metadata such as branch, HEAD, changed paths, and worktree fingerprint;
- `checkpoints/`: historical checkpoint metadata.

### Install

On Windows:

```powershell
git clone https://github.com/MuzhiCoder/codex-wip-skill.git
cd codex-wip-skill
.\scripts\install.ps1
```

Or copy the repository contents manually to:

```text
%USERPROFILE%\.codex\skills\wip
```

If `CODEX_HOME` is set, the installer uses:

```text
$env:CODEX_HOME\skills\wip
```

Otherwise it uses:

```text
$HOME\.codex\skills\wip
```

After installation, start a fresh Codex session and verify discovery with:

```text
$wip status
```

### Typical scenario: usage exhausted, then switch to API key

Example:

```text
ChatGPT Account Codex
        ↓
Long-running development task
        ↓
Usage exhausted / original session unavailable
        ↓
CC Switch / API Key / Custom Provider
        ↓
New Codex Session
```

If the previous session can no longer continue, open a new Codex session in the **same repository** and run:

```text
$wip recover
```

Recovery first freezes business-code edits, then inspects:

1. repository instructions such as `AGENTS.md`;
2. existing `.codex/wip/` state;
3. `git status`, Git history, and diff structure;
4. changed or added tests;
5. changed production code;
6. CodeGraph or other available code-intelligence tools;
7. targeted build and test evidence;
8. ADRs, plan files, TODOs, and FIXMEs;
9. user-provided screenshots or previous-agent output as supporting evidence.

Work items are classified as:

- `VERIFIED_DONE`
- `IMPLEMENTED_UNVERIFIED`
- `PARTIAL`
- `BLOCKED`
- `NOT_STARTED`
- `UNKNOWN`

After reviewing the recovery report, continue with:

```text
$wip resume
```

### Cross-provider / cross-machine handoff

Before switching provider, account, session, or machine, run:

```text
$wip handoff
```

For another machine, transfer both:

1. **code state**; and
2. **`.codex/wip/` state**.

A user-approved WIP Git branch or WIP commit is the preferred transport when practical.

The skill does **not** automatically run:

- `git commit`
- `git push`
- `git reset --hard`
- `git clean`
- force push
- Git history rewrites

High-impact Git actions remain explicit user decisions.

### Evidence model

Important claims in `current.md` are labeled as:

- `VERIFIED` — directly supported by tests, executable behavior, code, or authoritative project documentation;
- `INFERRED` — strongly suggested by code, diff, or call graph but not yet fully proven;
- `REPORTED` — supplied by a previous agent, user, or screenshot but not independently verified;
- `UNKNOWN` — insufficient evidence.

This prevents a recovered session from blindly trusting stale or speculative handoff notes.

### Security

`wip_snapshot.py` is metadata-only by default. It does not persist:

- raw diff contents;
- business file contents;
- environment-variable values;
- API keys;
- access tokens;
- cookies;
- passwords;
- authorization headers.

`wip_validate.py` also checks `current.md` for several common secret markers.

### Tests

Run locally:

```powershell
python scripts/test_wip_snapshot.py
python scripts/test_wip_validate.py
```

GitHub Actions runs the same test suite on Windows and Linux with Python 3.11–3.13.

### Repository layout

```text
.
├── .github/workflows/test.yml
├── SKILL.md
├── agents/
│   └── openai.yaml
├── examples/
│   └── codex-wip.example.md
├── references/
│   ├── handoff-protocol.md
│   ├── recovery-protocol.md
│   └── wip-contract.md
└── scripts/
    ├── install.ps1
    ├── wip_snapshot.py
    ├── wip_validate.py
    ├── test_wip_snapshot.py
    └── test_wip_validate.py
```

### Recommended workflow

Do not wait until usage is fully exhausted before creating the first WIP record.

Run:

```text
$wip checkpoint
```

at meaningful milestones such as:

- a RED test establishes target behavior;
- the GREEN implementation passes;
- an important blocker is removed;
- an architectural decision changes;
- a migration/refactor phase completes;
- before a long or risky operation;
- before switching providers;
- before switching machines;
- when remaining usage becomes operationally risky.

With periodic checkpoints, a hard interruption only requires recovering the small amount of work performed after the latest checkpoint.
