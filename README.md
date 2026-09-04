# Codex WIP Skill

<div align="center">

**Durable checkpoint · Handoff · Forensic recovery · Resume for OpenAI Codex**

<a href="#zh-cn">中文</a> | <a href="#english">English</a>

<br/>

<a href="https://muzhicoder.github.io/codex-wip-skill/">🌐 Interactive Demo / 动画演示</a>
&nbsp;·&nbsp;
<a href="https://github.com/openai/codex/issues/42725">📣 Codex Curated Marketplace Review</a>

</div>

---

<a id="zh-cn"></a>

## 中文说明

`Codex WIP` 是一个面向 OpenAI Codex 长任务的持久化工作连续性 Skill / Plugin，用于在**额度耗尽、账号或 Provider 切换、旧会话无法访问、崩溃、上下文丢失、换电脑**等情况下保存、恢复并继续工程工作。

核心原则：

> Conversation 不是连续性的边界。真正可靠的连续性来源应当是 **Git 仓库 + 可验证的 WIP 状态**。

### 支持的模式

| 命令 | 说明 |
| --- | --- |
| `$wip checkpoint` | 当前 Session 正常时创建轻量检查点 |
| `$wip handoff` | 准备切换账号、Provider、Session 或机器 |
| `$wip recover` | 原会话不可访问时，从 Git、测试、代码关系等证据恢复工作状态 |
| `$wip resume` | 验证检查点与当前仓库是否一致，并继续已确认的下一步 |
| `$wip status` | 检查 WIP 新鲜度与仓库漂移，不修改业务代码 |

### 推荐安装方式：Codex Plugin Marketplace

仓库现在已经是一个可直接添加的公开 Codex Marketplace：

```bash
codex plugin marketplace add MuzhiCoder/codex-wip-skill --ref main
codex plugin add codex-wip@codex-wip-skill
```

安装后请**新建 Codex 会话**，然后验证：

```text
$wip status
```

Codex App 中也可以进入 **Plugins → Add Marketplace**，填写：

```text
MuzhiCoder/codex-wip-skill
```

然后安装 `Codex WIP`。

### 兼容方式：直接安装 Skill

Windows：

```powershell
git clone https://github.com/MuzhiCoder/codex-wip-skill.git
cd codex-wip-skill
.\scripts\install.ps1
```

脚本会把正式打包版本中的：

```text
plugins/codex-wip/skills/wip
```

安装到：

```text
%USERPROFILE%\.codex\skills\wip
```

### 典型场景：额度耗尽后切换 API Key

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
        ↓
$wip recover
        ↓
$wip resume
```

`recover` 会先冻结业务代码修改，再根据仓库指令、Git 状态、历史、changed tests、生产代码、CodeGraph/代码关系、定向构建测试、ADR/TODO/FIXME，以及用户提供的截图或旧 Agent 输出进行恢复。

重要结论使用以下证据等级：

- `VERIFIED`
- `INFERRED`
- `REPORTED`
- `UNKNOWN`

工作项使用以下状态：

- `VERIFIED_DONE`
- `IMPLEMENTED_UNVERIFIED`
- `PARTIAL`
- `BLOCKED`
- `NOT_STARTED`
- `UNKNOWN`

### 持久化状态

```text
.codex/wip/
├── current.md
├── state.json
└── checkpoints/
    └── <timestamp>.json
```

- `current.md`：面向用户和新 Codex Session 的可读任务状态；
- `state.json`：branch、HEAD、changed paths、worktree fingerprint 等机器可读元数据；
- `checkpoints/`：历史检查点。

### 安全设计

默认快照是 metadata-only，不持久化完整 diff、业务文件正文、环境变量值、API Key、Access Token、Cookie、密码或 Authorization Header。

Skill 不会在恢复流程中自动执行：

- `git reset --hard`
- `git clean`
- force push
- Git 历史重写
- 未经用户明确要求的 `git commit` / `git push`

### Codex 社区发布状态

当前项目已经具备原生 Codex Plugin / Marketplace 结构，并且任何用户都可以通过本仓库公开 Marketplace 安装。

同时已经向 OpenAI Codex 官方仓库提交 curated marketplace review 请求：

**https://github.com/openai/codex/issues/42725**

公开 Plugin Directory / 官方 curated marketplace 是否收录由 OpenAI 审核决定；提交 review 不代表已经被官方目录收录。

### 动画演示

**https://muzhicoder.github.io/codex-wip-skill/**

页面源文件：`docs/index.html`。

### 仓库结构

```text
.
├── .agents/plugins/marketplace.json
├── .github/workflows/
│   ├── test.yml
│   └── pages.yml
├── docs/
│   └── index.html
├── plugins/
│   └── codex-wip/
│       ├── .codex-plugin/plugin.json
│       ├── README.md
│       └── skills/
│           └── wip/
│               ├── SKILL.md
│               ├── agents/
│               ├── references/
│               └── scripts/
├── SKILL.md                 # legacy direct-skill mirror
├── agents/                  # legacy mirror
├── references/              # legacy mirror
└── scripts/
    ├── install.ps1
    ├── wip_snapshot.py
    ├── wip_validate.py
    ├── test_wip_snapshot.py
    ├── test_wip_validate.py
    └── test_plugin_package.py
```

### 推荐工作流

不要等到额度已经耗尽才第一次保存 WIP。建议在 RED、GREEN、重要 blocker 解决、架构决策变化、迁移阶段完成、上下文压缩前、Provider/机器切换前，以及剩余额度已经可能影响连续性时执行：

```text
$wip checkpoint
```

<div align="center"><a href="#english">Go to English ↓</a></div>

---

<a id="english"></a>

## English

`Codex WIP` is a durable continuity Skill / Plugin for long-running OpenAI Codex coding work. It helps preserve, reconstruct, and resume engineering state when usage limits are exhausted, authentication or providers change, the original conversation becomes inaccessible, a crash occurs, context is lost, or development moves to another machine.

Core principle:

> Conversation identity is not the continuity boundary. Reliable continuity should come from the **Git repository + verifiable WIP state**.

### Modes

| Command | Purpose |
| --- | --- |
| `$wip checkpoint` | Persist a lightweight checkpoint while the current session is healthy |
| `$wip handoff` | Prepare for a provider/account/session/machine handoff |
| `$wip recover` | Reconstruct interrupted work from Git, tests, code relationships, and other evidence |
| `$wip resume` | Validate checkpoint freshness and continue from the first verified next action |
| `$wip status` | Report checkpoint freshness and repository drift without changing business code |

### Recommended install: Codex Plugin Marketplace

This repository is now a public Codex marketplace:

```bash
codex plugin marketplace add MuzhiCoder/codex-wip-skill --ref main
codex plugin add codex-wip@codex-wip-skill
```

Start a **new Codex thread** after installation and verify:

```text
$wip status
```

In the Codex App you can also open **Plugins → Add Marketplace**, enter:

```text
MuzhiCoder/codex-wip-skill
```

and install `Codex WIP`.

### Compatibility install: direct Skill

On Windows:

```powershell
git clone https://github.com/MuzhiCoder/codex-wip-skill.git
cd codex-wip-skill
.\scripts\install.ps1
```

The installer copies the canonical packaged skill from `plugins/codex-wip/skills/wip` into `%USERPROFILE%\.codex\skills\wip`.

### Typical scenario: usage exhausted, then switch provider

```text
ChatGPT Account Codex
        ↓
Long-running coding task
        ↓
Usage exhausted / original thread unavailable
        ↓
CC Switch / API Key / Custom Provider
        ↓
New Codex Session
        ↓
$wip recover
        ↓
$wip resume
```

Recovery freezes business-code edits first, then reconstructs state from repository instructions, Git state/history, changed tests, production code, CodeGraph or other code-intelligence evidence, targeted build/test results, ADRs/TODOs/FIXMEs, and user-provided screenshots or previous-agent output.

Evidence labels:

- `VERIFIED`
- `INFERRED`
- `REPORTED`
- `UNKNOWN`

Work-item states:

- `VERIFIED_DONE`
- `IMPLEMENTED_UNVERIFIED`
- `PARTIAL`
- `BLOCKED`
- `NOT_STARTED`
- `UNKNOWN`

### Durable state

```text
.codex/wip/
├── current.md
├── state.json
└── checkpoints/
    └── <timestamp>.json
```

Git remains the source of truth for code. `current.md` stores durable intent, decisions, verification state, blockers, and exact next actions.

### Security

Snapshots are metadata-only by default. They do not persist raw diffs, business file contents, environment-variable values, API keys, access tokens, cookies, passwords, or authorization headers.

The recovery workflow does not automatically run destructive Git operations, force pushes, history rewrites, commits, or pushes without explicit user intent.

### Codex community publishing status

The project now ships a native Codex plugin manifest and a public marketplace that anyone can add directly from this repository.

A curated marketplace review request has also been submitted to the official OpenAI Codex repository:

**https://github.com/openai/codex/issues/42725**

Submission for review does not mean the plugin is already listed in the universal public Plugin Directory or official curated marketplace; inclusion is controlled by OpenAI review.

### Interactive demo

**https://muzhicoder.github.io/codex-wip-skill/**

Source: `docs/index.html`.

### Validation

```powershell
python scripts/test_wip_snapshot.py
python scripts/test_wip_validate.py
python scripts/test_plugin_package.py
```

GitHub Actions runs the suite on Windows and Linux with Python 3.11–3.13.

### Recommended workflow

Checkpoint at meaningful milestones: after RED, after GREEN, after removing a blocker, after an architectural decision, before expected context compaction, before switching providers/machines, or when the remaining usage limit becomes operationally risky.

<div align="center"><a href="#zh-cn">↑ 返回中文 / Back to Chinese</a></div>
