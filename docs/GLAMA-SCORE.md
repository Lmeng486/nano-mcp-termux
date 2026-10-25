# Glama 评分核验报告

> 本文件记录 `nano-mcp-termux` 在 [Glama.ai](https://glama.ai/mcp/servers/Lmeng486/nano-mcp-termux) 上的评分快照、版本元数据核验过程与结论。
> 目的是：**下次对 Glama 评分有疑问时，先看这里，不必从头排障。**

- 快照时间：**2026-10-25 10:30（Glama 侧评分时间戳）**
- 抓取时间：2026-10-25
- 核验对象：`Lmeng486/nano-mcp-termux`（PyPI: `nano-mcp-termux`，官方 Registry: `io.github.Lmeng486/nano-mcp-termux`）
- 核验仓库状态：本地 `HEAD = 46cbb5e`，远端 `main` 同提交
- 数据来源：Glama 页面 HTML（公开 API 需 API key，返回 401）

---

## 一、结论速览

| 项目 | 结果 | 判定 |
|---|---|---|
| Quality Grade | **A** | ✅ |
| Maintenance Grade | **A** | ✅ |
| License Grade | **A** | ✅ |
| TDQS 总分 | **A · 4.1 / 5.0**（4 个工具聚合） | ✅ 上等区间 |
| Server Coherence | 4 / 3 / 4 / 3（四维度） | ⚠️ 主要拖累项 |
| ⚠️ UI 告警 | **无** | ✅ 已核实排除 |
| 认领状态 | `author:claimed` | ✅ 已认领 |
| 版本 `1.1.2` / `1.1.3` 疑点 | Glama 内部 release 编号自增，非发布物 | ✅ 无需处理 |

**一句话总结**：服务器状态健康，评分扎实，此前担心的两个问题（页面 ⚠️ 告警、版本号不一致）**均不成立**。

---

## 二、评分明细

### 2.1 四工具 TDQS 全量明细

| 工具 | 等级 | 总分 | Behavioral<br>Transparency (20%) | Conciseness<br>(10%) | Contextual<br>Completeness (10%) | Parameter<br>Semantics (15%) | Purpose<br>Clarity (25%) | Usage<br>Guidelines (20%) |
|---|---|---|---|---|---|---|---|---|
| `device_status` | A | **4.4** | 5 | 5 | 5 | 4 | 4 | 4 |
| `path_adapter` | A | **4.4** | 4 | 4 | 5 | 4 | 5 | 4 |
| `resolve_path` | A | **4.4** | 5 | 4 | 5 | **3** | 4 | 5 |
| `server_health` | A | **4.3** | 4 | 4 | 4 | 4 | 5 | 4 |

- 极差仅 **0.1**，四份描述质量均衡，无短板工具。
- 唯一 **3 分**：`resolve_path` 的 Parameter Semantics。
- 唯一两项 4.3 以下维度集中在 `server_health` 的 Behavioral Transparency / Conciseness / Contextual Completeness（均 4 分）。

**TDQS 聚合口径**（已用官方开源仓库 spec 的整数原语 + 精确有理数运算，100% 复现页面全部五个分数）：

```
单工具分 = Σ(维度分 × 权重) / 100      # 结果落在 0.1 网格
Q       = 0.6 × mean(单工具分) + 0.4 × min(单工具分)
C       = mean(coherence 四维)
总分     = 0.7 × Q + 0.3 × C
```

代入实测值：单工具 `4.4 / 4.4 / 4.4 / 4.3` → `mean = 4.375`、`min = 4.3` →
`Q = 0.6×4.375 + 0.4×4.3 = 4.345 → 4.3`；`C = (4+3+4+3)/4 = 3.5`；
`总分 = 0.7×4.3 + 0.3×3.5 = 4.06 → 4.1`。**与页面徽章、`overallScore 4.1`、`coherenceScore 3.5` 全部一致。**

**官方 spec 原文的整数实现（照抄这三行即可复现，权威性高于任何页面反解）**：

```
descriptionQualityScore = round1(6 × Σ tdqs + 4 × n × min(tdqs), 100 × n)
coherenceScore          = round1(disambiguation + namingConsistency
                                 + toolCountAppropriateness + completeness, 4)
overallScore            = round1(7 × descriptionQualityScore + 3 × coherenceScore, 100)
```

其中 `tdqs` 是单工具的十分位整数（10–50，即 `4.4 → 44`），`n` 是工具数，`round1` 是整数 half-up 原语
`round1(num, den) = (2 × num + den) // (2 × den)`。
代入 `Σtdqs = 44+44+44+43 = 175`、`n = 4`、`min = 43`：
`(6×175 + 4×4×43) / (100×4) = (1050 + 688) / 400 = 1738/400 = 4.345 → 4.3`；
`C = (4+3+4+3)/4 = 3.5`；`(7×43 + 3×35)/100 = 406/100 = 4.06 → 4.1`。
与上面的分数式写法结果完全等价，但整数写法不会踩浮点。

> 注：若把 `Q` 简化为纯均值 `4.4`，总分也是 `4.1`（`0.7×4.4+0.3×3.5=4.13`），仅凭页面总分无法区分两种口径；此处采用官方 spec 的 `60/40` 定义，因为它能同时解释 `min` 项的存在意义。
> 旧版本文档写的「w = 0.70 反解、无最小值参与」是当时未拿到 spec 时的推测，已废弃。

> **来源更正**：`https://glama.ai/spec`、`/mcp/spec`、`/spec/tdqs`、`/docs/tdqs` 四个地址当前**全部 404**。
> 权威来源已迁移到 GitHub 开源仓库 `glama-ai/tool-definition-quality-score` 与 `tdqs.dev`（v1.2 规范）。
> 本节公式取自该仓库原文，不是页面反解。

**⚠️ 量纲陷阱（复现时最容易踩的坑）**：必须全程用整数 tenths/hundredths 运算并显式 half-up。
实测 Python 内置 `round()` 采用银行家舍入，会把 `4.25 → 4.2`、`4.85 → 4.8`，直接把 `server_health` 从 4.3 算成 4.2、总分算错。
正确 half-up：`def hu(p,q): return (2*p+q)//(2*q)`。

官方 spec 对此有三条明确警告，逐条都是会真扣 0.1 分的实操陷阱：

1. **`mean` 必须是精确的 `Σtdqs / n`，不能用已发布的保留一位小数的 `meanTdqs`。**
   本条实测踩中：先把 `mean` 取整成 `4.4`，再算 `0.6×4.4 + 0.4×4.3 = 4.36 → 4.4`，
   `Q` 被错算成 `4.4`（正确 `4.3`），总分随之错算成 `4.1` 之外的值。必须用 `4.375`。
2. **Python 的 `round` 与 `Math.round` 在半值上方向相反。**
   coherence 四维之和为奇数时均值必然落在半值上，这类平局并不罕见，故一律显式 half-up。
3. **浮点累积会跨档。** 官方举例 `0.7 × 3.0 + 0.3 × 4.5` 在 double 下累加到略小于 `3.45`，
   于是把一个按公式应属 A 的服务器发布成 B。整数原语就是为消除这条而存在。

**⚠️ 80% 覆盖率门槛（官方新增规则）**：聚合只在**至少 80% 的工具已完成评分**时才计算，
否则部分覆盖会误报服务器质量。本仓库当前 4 个工具全部已评分，不受影响；
但若新增第 5 个工具，必须等它也被评分后聚合才会刷新 —— 即「加工具 → 立刻涨分」之间有一次评分延迟。

**TDQS 权重**：purpose clarity 25% / usage guidelines 20% / behavioral transparency 20% / parameter semantics 15% / conciseness 10% / contextual completeness 10%。
**总分构成**：TDQS 占 70%，Server Coherence 占 30%。

### 2.2 Server Coherence 四维度

| 维度 | 得分 | 评语要点 |
|---|---|---|
| Disambiguation（消歧） | **4 / 5** | `device_status` 与 `server_health` 靠 "host device vs server process" 区分清晰；`resolve_path` 与 `path_adapter` 靠 "单路径 vs 环境总览" 区分清晰 |
| Naming Consistency（命名一致） | **3 / 5** | 三种命名模式并存：名词式 `device_status` / `server_health`、动宾式 `resolve_path`、名词+agent 式 `path_adapter`，**无统一约定** |
| Tool Count（工具数量） | **4 / 5** | 4 个工具精简，匹配只读诊断定位 |
| Completeness（完整性） | **3 / 5** | 评语原话：**"a dead end for action"** — 能诊断不能操作，无法列目录、批量解析或在解析后执行动作 |

### 2.3 逐工具评语中的扣分原因（可直接转改进项）

| 工具 | 维度 | 扣分原因（评语要点） |
|---|---|---|
| `resolve_path` | Parameters (3) | "Schema coverage is 100% and the single parameter is fully documented there, so the baseline is 3. The description restates the same facts ... without adding format or syntax detail beyond the schema" |
| `resolve_path` | Purpose (4) | "it never mentions the sibling `path_adapter`, so an agent cannot distinguish the two from this text alone" |
| `server_health` | Usage (4) | "It doesn't explicitly route the agent away from a sibling" |
| `device_status` | Purpose (4) | "no sibling is named, so an agent must infer the boundary" |
| `device_status` | Usage (4) | "No explicit when-not or named alternative (e.g., use `server_health` for the remote server vs. this for local hardware)" |
| `path_adapter` | Behavior (4) | "the 'side effects: none' sentence is somewhat redundant" |
| `path_adapter` | Conciseness (4) | "Minor waste in restating read-only/idempotent already covered by annotations" |

**共性诊断**：绝大多数扣分都指向同一个根因 —— **描述里没有点名兄弟工具、没有 "use X instead of Y when Z" 的路由语**。加一句即可同时抬升 Purpose（25%）与 Usage Guidelines（20%）。

### 2.4 评语中的正面评价（摘录）

`server_health` Purpose 得 5 分的理由：

> "States a specific verb and object — 'read-only self-diagnostics for this MCP server process' — and enumerates exactly what it inspects (pid/ppid, uptime, counters, children, RSS, Phantom Process Killer)"

说明现有描述已相当扎实，每句都 "earns its place"。

---

## 三、版本疑点 `1.1.2` / `1.1.3`：已定论

### 3.1 现象

Glama 页面 RSC flight 数据中出现 `"version": "1.1.2"`，但 PyPI / GitHub 上最新版本是 `1.1.1`，一度被误判为"版本不一致"。

> 后续复查时该字段已自增为 `"version": "1.1.3"`（见 3.6），**这是同一字段的正常自增，不是新问题**。

### 3.2 全渠道交叉验证结果

| 渠道 | 实测结果 | 是否含 1.1.2 |
|---|---|---|
| PyPI JSON | `latest: 1.1.1`，`all: ['1.1.0', '1.1.1']`，`1.1.2` 上传记录为空 | ❌ |
| GitHub Releases | 仅 2 条：`v1.1.1`(2026-10-16)、`v1.1.0`(2026-10-12)，均非 draft/prerelease | ❌ |
| GitHub Tags | 仅 `v1.1.1`(e853af5)、`v1.1.0`(2cdecca) | ❌ |
| 源码常量 | `SERVER_VERSION = "1.1.1"`（`nano_mcp_termux.py` 第 40 行） | ❌ |
| `server.json` | 两处均 `"version": "1.1.1"` | ❌ |
| `pyproject.toml` | `version = "1.1.1"` | ❌ |
| 仓库全文 grep | `grep -rn '1\.1\.2'`（排除 `.git`）**零命中** | ❌ |
| MCP 官方 Registry | 仅 `1.1.0` 与 `1.1.1` 两条记录 | ❌ |
| Glama 页面**可见文本** | `1.1.2` 零出现；只出现 `1.1.0`(6 次)、`1.1.1`(5 次) | ❌ |

### 3.3 唯一出现位置

`1.1.2` **仅**出现在 Glama 页面 RSC flight 数据（不可见的 React Server Components 序列化数据）中：

```
"inspectable","latestRelease",{...},"version","1.1.2","maintainers",[1963],
"defaultBranch","main","githubTreeId",54483022,1814941
```

### 3.4 关键区分（此前误判的根源）

页面里有两个语义完全不同的 `version` 字段：

| 字段 | 值 | 语义 |
|---|---|---|
| `"releaseVersion": "1.1.1"` | 1.1.1 | **Tool Schema Changelog 的变更记录**，对应页面可见的 "4 tool updates v1.1.1" |
| `"latestRelease": {..., "version": "1.1.2"}` | 1.1.2 | **Glama 自己的 release 对象**，是其内部对"最近一次成功构建"的编号 |

把两者当成同一个"版本"才产生矛盾。**`1.1.2` 不是用户发布的版本，不影响 PyPI/GitHub 一致性，无需采取任何动作。**

### 3.5 为什么 Glama 的 `releaseVersion` 停在 1.1.1

`v1.1.1..HEAD` 之间有 **6 个未发版提交**，全部是 docs/build/test 性质，**没有任何提交改过 `SERVER_VERSION`**：

```
46cbb5e docs: document verify_glama_build.sh exit codes in README
b8ac908 fix: pin index url and classify build failures in verify script
8b8912e test: add script reproducing Glama uv build locally
d0b4369 build: add pyproject.toml for reproducible packaging
6ad9793 docs: link Dev.to announcement article in README Links
87014a3 docs: add MCP client connection guide and release zip
```

所以 Glama 侧停在 1.1.1 是**准确的**。

> 附带解答一个历史疑问：早前查 `6ad9793` 时发现它没有 `pyproject.toml`，是因为 `pyproject.toml` 是更晚的 `d0b4369` 才加入的 —— 不是仓库残缺。

### 3.6 后续演变：`1.1.3`（同一字段自增，同样无需处理）

2026-10-25 晚复查时，该字段从 `1.1.2` 变为 `1.1.3`，位置与结构完全一致：

```
"inspectable","latestRelease",{...},[422],"licenseExpression",66,
"version","1.1.3","maintainers",[1963],"defaultBranch","main",
"githubTreeId",54483022,1814941
```

本轮复核结果：

| 检查项 | 实测 |
|---|---|
| 全页 `"version"` 键出现次数 | **1 次**（即这一处，pos 241407） |
| 所在标签 | `<script nonce="...">window.__reactRouterContext.streamControl`（171401–245632）内部 |
| 剔除 `<script>`/`<style>` 后可见文本中 `1.1.3` 命中 | **0 次** |
| 可见文本版本号分布 | `1.0.0`×2、`1.1.0`×3、`1.1.1`×1，**无 1.1.2 / 1.1.3** |
| `"releaseVersion"` | 仍为 `"1.1.1"`（Tool Schema Changelog 字段） |
| GitHub Releases | 仍为 2 条（`v1.1.1`、`v1.1.0`），**无 1.1.2 / 1.1.3** |
| 仓库 `grep '1\.1\.3'` | **零命中**（rc 1） |
| Tags | 仍为 `v1.1.0`、`v1.1.1` |
| `server.json` / `pyproject.toml` | 均 `1.1.1` |

**结论**：`1.1.3` 与当年的 `1.1.2` 完全同类——Glama 内部 release 对象的自增编号，随其内部构建次数递增，**与 PyPI / GitHub 发布版本无关**，普通浏览器视图里也看不到。

**关键认知（下次不必再查）**：

- 这个数字会持续往上走：`1.1.2` → `1.1.3` → ……，**看到它不等于仓库有新版本**。
- 它和页面快照是**解耦**的：本轮内部编号涨到 `1.1.3`，但 `observedAt` 仍是 `2026-10-25T10:23:00.951684Z`、`scoredAt` 仍是 `2026-10-25T10:30:22.058725Z`，**采集与评分时间戳一点没动**。说明「内部构建计数器自增」不等于「重新抓取了最新代码」。
- 因此：**要判断 Glama 是否真的重抓，只看 `observedAt` / `scoredAt` 是否推进，不看 `githubProject.version`。**


### 3.7 抓取源定论：页面快照对应 GitHub `46cbb5e`，不是 PyPI 包

本节回答一个此前一直悬着的问题：Glama 页面上的四段工具描述，究竟抓自仓库哪个提交？是不是抓的 PyPI 上的 `nano-mcp-termux 1.1.1` 包？

**结论：抓自 GitHub 仓库提交 `46cbb5e`（2026-10-25 09:10:34 +0000，`SERVER_VERSION = "1.1.1"`），不是 PyPI 包。** 四条独立证据共同锁定，每条单独成立即可排除其余候选。

**证据一：四段描述归一化后 4/4 完全一致。**

从页面提取四个 `<details>` 工具块内的最长 `<p>`，`html.unescape` + 去标签后，与各提交 `nano_mcp_termux.py` 中对应描述字符串逐字符比对。**原始比对只有 2/4 命中**，差异经逐字符定位为**提取/渲染噪声而非版本差异**：

| 工具 | 页面 vs 源码差异 | 归因 |
|---|---|---|
| `resolve_path` | `` `path` `` → `path` | HTML 渲染剥掉反引号 |
| `device_status` | `\"unavailable\"` → `"unavailable"` | 源码 `\"` 转义在提取时未还原 |

统一归一化（去反引号、还原 `\"`、压缩空白）后重跑：

| 提交 | 归一化匹配 | `SERVER_VERSION` | 结论 |
|---|---|---|---|
| `00df8af` | 4/4 | 1.1.0 | 描述相同但版本号不符（证据三排除） |
| `5ac7e96` | 4/4 | 1.1.1 | 描述相同，靠证据二排除 |
| **`46cbb5e`** | **4/4** | **1.1.1** | **唯一同时满足全部证据** |
| `ee60620` | 0/4 | 1.1.1 | 已改写 |
| `bb0448c` / `92a9489` / HEAD | 0/4 | 1.1.1 | 已改写 |

页面四工具描述长度基线：`device_status` 542 / `server_health` 482 / `resolve_path` 779 / `path_adapter` 545；对应源码为 544 / 482 / 781 / 545，差 2 的两项已归因为上表的渲染/转义。

**证据二：README 章节标记矩阵（决定性）。**

三个候选在描述上完全相同、无法靠描述区分；但 README 长度与章节差异极大，且章节名会原样出现在页面里：

| 标记 | 页面 | `00df8af` | `5ac7e96` | `87014a3` | `6ad9793` | **`46cbb5e`** | HEAD |
|---|---|---|---|---|---|---|---|
| `Connect to your MCP client` | 2 | 0 | 0 | 1 | 1 | **1** | 1 |
| `Dev.to` | 2 | 0 | 0 | 0 | 1 | **1** | 1 |
| `verify_glama_build` | 4 | 0 | 0 | 0 | 0 | **2** | 2 |
| README 字节数 | — | 5477 | 5530 | 8293 | 8478 | **9698** | 9827 |

`5ac7e96` 三项全 0，与页面 2 / 2 / 4 完全不符；`46cbb5e` 是**第一个同时具备三项标记**的提交（更早的 `b8ac908` README 尚无 `verify_glama_build`）。页面计数是源码的 2 倍，属同一章节在 JSON-LD / `<details>` / tab 等多处重复渲染，**只可比「有/无」，不可比绝对值**。

**证据三：版本号排除 `00df8af`。** 页面 `releaseVersion` 为 `"1.1.1"`，而 `00df8af` 的 `SERVER_VERSION` 是 `"1.1.0"`。

**证据四：时间线排除其后提交。** 页面 `observedAt = 2026-10-25T10:23:00.951684Z`、`scoredAt = 2026-10-25T10:30:22.058725Z`。`46cbb5e` 提交于 09:10:34，早于抓取；而 `98b68a2`（10:53:11）、`d050cfa`（10:54:08）、`ee60620`（11:02:38）均晚于 `observedAt`，物理上不可能被本次抓取。其中 `98b68a2` 与 `46cbb5e` 的 README 完全相同（`git diff --stat` 只增 `docs/GLAMA-SCORE.md` 381 行），故只能靠时间排除。

**机制旁证：Glama 从仓库构建镜像自省，不拉 PyPI。**

- `Dockerfile` 由 `00df8af`（2026-10-15 11:43:29）引入，内容为 `FROM python:3.12-alpine` + `WORKDIR /app` + `COPY nano_mcp_termux.py .` + `RUN chmod +x` + `CMD ["python3","nano_mcp_termux.py"]`
- 页面出现原文 `"Container-ready: Dockerfile at repo root for Glama introspection"`
- 页面机制关键词计数：`Dockerfile 2 / docker 6 / uvx 13 / pip install 9 / pypi 4 / nixpacks 0 / buildCommand 0`
- `nixpacks 0` 说明不是自动探测构建，`buildCommand 0` 说明不是自定义命令构建
- `server.json` 里的 `registryType: pypi` / `runtimeHint: uvx` 只是 MCP 官方 Registry 的元数据，**不能当作 Glama 行为依据**

**提取正则的坑（复现必看）**：页面工具块写作 `<details class="hvOeJT ..." id="device_status">`，**`class` 在 `id` 之前**。用 `<details id="...">` 会全部失配并返回长度 0——本轮首次复现即踩此坑，误得「四段全不匹配」的假结论。正确写法：

```python
m = re.search(r'<details[^>]*\bid="%s"[^>]*>' % tool, page)
```

**影响**：

1. 改描述只需 `push` 到 GitHub 并让 Glama 重抓，**无需发布新 PyPI 版本**。
2. `bb0448c` 已 push 到 `main`，动作正确且充分；当前缺的只是「触发重抓」这一步。
3. 判定「是否真的重抓」只看 `observedAt` / `scoredAt` 是否推进，不看 `githubProject.version`（见 3.6）。


---

## 四、可执行的优化建议（按投入产出排序）

### 优先级 1 — 抬升 Usage Guidelines（权重 20%，四工具均有空间）

给每个工具补一句 "use X instead of Y when Z" 的路由语。示例（`device_status`）：

> "For the MCP server process itself (uptime, children, RSS) use `server_health` instead; this tool reports the host hardware."

`server_health`、`resolve_path` 同理，明确指向兄弟工具。
**这一句话能同时抬升 Purpose（25%）和 Usage Guidelines（20%）两项。**

### 优先级 2 — 抬升 `resolve_path` 的 Parameter Semantics（唯一 3 分，权重 15%）

在描述里补具体格式/语法示例：`$PREFIX/bin`、`/sdcard/Download`、`~/storage/shared`，并说明 `~` / `$HOME` / `$PREFIX` / `$TMPDIR` 的展开规则。
目标：让描述在 schema 之外提供**格式或语法细节**。

### 优先级 3 — 命名一致性（3 / 5）

统一为动宾式（考虑 `resolve_path` / `path_adapter` 都是动作类）：
`device_status` → `get_device_status`，`server_health` → `get_server_health`。

⚠️ **这是 breaking change**，需同步改 README、`server.json`、测试和 release。成本明显高于前两项，建议评估是否值得。

### 优先级 4 — Completeness（3 / 5，"dead end for action"）

评语认为"只能诊断不能操作"是结构性问题。可选方案：
- 加只读 `list_dir`（列目录，带深度和过滤）
- 加批量 `resolve_paths`

⚠️ 这是**新增工具**，会改变 Tool Count 的评分逻辑。建议先完成优先级 1、2，观察总分变化后再决定。

### 收尾提醒

改完描述后需重新点 **Build & Release** 触发 Glama 重新 introspect，评分页要等它重跑完才更新。

---

## 五、核验方法与复现

### 5.1 为什么只能解析 HTML

- Glama 公开 API `https://glama.ai/api/mcp/v1/servers/Lmeng486/nano-mcp-termux` 返回 **HTTP 401**：
  `{"error":{"code":"unauthorized","message":"This endpoint requires an API key..."}}`
- 因此所有评分数据均来自页面 HTML 解析。

### 5.2 `/score` 已重定向到主页

`/score` 子路径已重定向，`score.html`、`now_main.html`、`now_score.html` 三份独立落盘文件完全一致：

| 指标 | 三份文件实测值 |
|---|---|
| Python 读取长度 | 均 **246826** 字符（= 247030 字节，差异来自 UTF-8 多字节字符） |
| `latestRelease` 计数 | 均 **1** |
| `1.1.0 / 1.1.1 / 1.1.2` 计数 | 均 **6 / 5 / 1** |

**后续核验直接抓主页即可，不必再试 `/score`。**

### 5.3 HTML 提数一律走 Python 正则

`grep` 在多重转义的 RSC 数据上不可靠，实测以下全部返回空或残缺：

```bash
grep -o '"tdqs",[0-9.]\{1,6\}'          # 空
grep -o '"tier","[A-F]"'                # 空
grep -o "\\\"toolName\\\",\\\"$t"       # 空
grep -o 'toolName[^,]*'                 # 仅 1 个残缺匹配
```

**可用方法**（Python）：

```python
# 1. 定位四个工具评分卡起点
[s.start() for s in re.finditer(r'TDQS</a></h4>', html)]
# → [64424, 76036, 88118, 99700]

# 2. 取等级与总分
re.search(r'padding:4px 8px">([A-F])</span><span class="czikZZ jrPWok">([0-9.]+)', seg)

# 3. 取六维度
re.findall(r'<span>([A-Za-z ]+)</span><span class="czikZZ">([0-9.]+)<!-- -->/5</span>', seg)
```

**`grep` 只用于计数与存在性判断，不用于提值。**

### 5.4 正文还原（无需 tavily / 浏览器即可读全文）

```python
t = re.sub(r'<script[^>]*>.*?</script>', '', s, flags=re.S)
t = re.sub(r'<style[^>]*>.*?</style>',  '', t, flags=re.S)
t = re.sub(r'<[^>]+>', '\n', t)
t = html.unescape(t)
# 去空行 → 784 行纯文本
```

按行号可精确定位：**工具评分卡 358-526**、**Tool Schema Changelog 574-589**、**TDQS 总分 597-599**。

### 5.5 RSC flight 数据只能靠原始字符串定位

标准 Next.js flight 提取正则在本页**失效**：

```python
re.findall(r'self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)', s)
# → chunks 0 / len 0
```

该页不使用标准 `self.__next_f.push` 包装（或转义层级不同）。
**正确做法**：`s.find('latestRelease')` 后切片 + `print(repr(...))` 观察上下文，不要试图把整段 JSON 化。

---

## 六、⚠️ 告警排查记录

`grep -c 'warning'` 在页面返回 **4**，一度被误认为存在 UI 告警。逐条核对后确认**全部是正文词汇**：

1. `quoting warnings` — `resolve_path` 描述中的措辞说明
2. `Deprecation warnings about project.license` — README 两处
3. `warnings` — `resolve_path` 的返回字段名

**结论：页面无 ⚠️ UI 告警，症状彻底解除。**
教训：`grep -c 'warning'` 非零 **不等于** 页面有告警。

---

## 七、已排除的排查路径（避免重复踩坑）

以下路径均已实测证伪，**不要再试**：

| # | 已排除的假设/做法 | 实测结论 |
|---|---|---|
| 1 | PEP 639 classifier 冲突会硬失败 | 不会 |
| 2 | `tools/list` 为空 | 不成立，4 工具正常 |
| 3 | 安装后入口点无法启动 | 可启动 |
| 4 | uv 比 pip 更严格导致失败 | 非根因 |
| 5 | 在 `glama.json` 写 build spec | 无效，该字段不支持 |
| 6 | 为 Glama 把 stdio 改 Streamable HTTP | 不必要 |
| 7 | 从公开页静态 HTML 反推评分 | 可行但需正则，见 5.3 |
| 8 | 安装 Glama GitHub App | 非必需 |
| 9 | 免鉴权调 Glama MCP API | 401，不可行 |
| 10 | 仓库缺 `Dockerfile` / `glama.json` | `glama.json` 已存在 |
| 11 | 页面版本 ≠ PyPI 当异常 | 见第三节，语义不同 |
| 12 | 本地 distutils/uv 硬链接报错当仓库问题 | 是本地环境问题 |
| 13 | GitHub 工具 401 ≠ token 失效 | 是工具侧问题 |
| 14 | `/tmp/lictest` 首测零警告是 403 假阴性 | 是假阴性 |
| 15 | `git log` 断字 ≠ 提交信息脏 | 显示问题 |
| 16 | `raw.githubusercontent.com` 返回 000 ≠ 未推送 | 网络问题 |
| 17 | contents API `KeyError:'mode'` ≠ 权限位丢失 | 字段缺失 |
| 18 | `visit_web` 超时 ≠ 站点故障 | 抓取侧问题 |
| 19 | tavily 抓 admin 页永远未登录视图 | 会话问题 |
| 20 | 本地 `uv pip install -e .` 在 proot 下失败 ≠ 仓库装不上 | 环境问题 |
| 21 | 旧博客 404 | 已失效链接 |
| 22 | admin 子路径 404 | 路径不存在 |
| 23 | Wayback 不可用 | 无快照 |
| 24 | tavily 搜索结果文件无 build spec | 无此内容 |
| 25 | 仓库 Dockerfile 对 Glama 构建有效 | 无效 |
| 26 | "首次抓取时仓库不完整" | 被 git 历史证伪 |
| 27 | Playwright 在 glama.ai 可用 | 被 CSP `unsafe-eval` 禁令废掉 |
| 28 | 按钮名称是 `Build` | 实际是 `Build` / `Build & Release` |
| 29 | `am start` 返回 exitCode=0 代表在前台 | 不代表 |
| 30 | `tavily_extract` 抓 `/score` 的 D 级评级是本服务器分数 | 是 Related Servers 的评级，**绝不能当本服务器分数** |
| 31 | `6ad9793` 是落后 4 提交、无 `pyproject.toml` 的旧快照 | 是历史快照，正常 |
| 32 | uv 构建处方 | 已被 `python3 nano_mcp_termux.py` 方案取代并验证成功 |
| 33 | `/score` 子路径可区分 | 已重定向到主页 |
| 34 | `grep -c 'warning'` 非零代表有告警 | 见第六节 |
| 35 | `1.1.2` 是发布版本 | 是 Glama 内部 `latestRelease` 编号 |
| 36 | `self.__next_f.push` 正则能取 flight 数据 | 本页失效 |

---

## 八、限制说明

1. **评分是快照**，非实时值。记录的是 Glama 在 **2026-10-25 10:30** 的抓取结果，后续变化需重新抓页面确认。
2. **Glama 公开 API 需 API key**（401），故全部数据来自页面 HTML 解析。解析已用三份独立落盘文件做同一性核对（见 5.2）。
3. **`1.1.2` 的归因基于排除法** —— 所有官方渠道零命中 + 可见文本零出现。Glama 未公开说明该字段语义，但结论对实际操作无影响。
4. **评语原文来自页面提取**，可能存在 HTML 转义残留；引用时以页面实际显示为准。

---

## 九、附：四工具描述原文（改写后基线）

> 本节记录**改写后**的描述原文（提交前的当前工作树版本），供评分回收时逐条比对。
> 改写前的原始基线已随 `d050cfa` 存入 git 历史，可用 `git show d050cfa:docs/GLAMA-SCORE.md` 取回。
> 本轮又做了一次**措辞级**改写（仅删去强制调用顺序的指令句，见下节），基线已同步更新。

### 官方 spec 措辞红线核查（本轮改写依据）

抓取 `https://tdqs.dev/spec` 原文（`len 284960`）后定位到一条**此前未纳入文档的硬性措辞约束**：

> The tell is the other kind of cross-reference, the kind that tries to *enforce* an ordering:
> "always call this first", "do not compute this yourself". A boundary is describable; a priority is not.
> Reach for the second and you have a tool-set problem wearing a description problem's clothes.
> Either make the purposes disjoint and say so in both descriptions, or collapse them into one tool.

同时官方给出了**正例**与**边界说明的正确写法**：

> "List ALL calls in date range, no user filtering. To filter by user, use search_calls_extensive instead."
> … naming a sibling to mark a boundary still earns full marks on Usage Guidelines.

**核查结论：原描述命中反模式，必须改写。** 命中位置两处：

| 位置 | 原句 | 问题 |
| --- | --- | --- |
| `resolve_path` | "so call it first on an unfamiliar device, then resolve_path per candidate path" | 直接下达调用顺序，即 "always call this first" 的同类写法 |
| `path_adapter` | "Call it once when starting work on an unfamiliar device, before constructing paths for other tools" | 同样在指定时序（"once / before"），只是换成无参工具的口吻 |

`resolve_path` 另有一句 `Call it before handing a path to a shell command or another tool`，属同类时序指令，一并改为「何时有用」的陈述。

**改写策略**：保留点名兄弟工具（官方明确这是满分写法），把「先后顺序」换成「问题分工」——两个工具回答两个不同问题（环境 vs 单路径），互斥而非有序。改写后三处禁用句式计数均为 0（`call it first` / `Call it once` / `before constructing paths`），`tools/list` 实测四工具描述均正常输出、annotations 四项不变。

### `device_status`
```
Read-only snapshot of the host hardware and OS: battery level, storage usage,
CPU architecture and memory. Use it when the answer depends on the physical
device: free space before a download, battery before a long job, arch before
picking a binary. Not for process or server state: use `server_health` for
pid/uptime/counters of this MCP server, `resolve_path` to validate one path,
and `path_adapter` for the runtime's path environment. Never raises: a field
that cannot be read is reported with source unavailable. Returns {battery,
storage, arch, memory}.
```
### `path_adapter`
```
Report the runtime's path environment so you can translate host paths
correctly: detected env class (termux/proot/android/linux),
HOME/PREFIX/TMPDIR, each Android shared-storage root with its real mount,
all noexec mounts that block in-place script execution, and runtime-specific
notes. Takes no arguments. Sibling boundary: this answers the environment
question (env class, HOME/PREFIX/TMPDIR, mount roots); `resolve_path`
answers the per-path question (expansion, mount, alternatives for one path).
Use `path_adapter` when the environment itself is unknown, `resolve_path` to
validate a single candidate path. Returns {env, home, prefix, tmpdir,
python, platform, android_roots, noexec_mounts, notes}.
```
### `resolve_path`
```
Resolve and validate one filesystem path in the runtime this server runs in:
expands ~/$HOME/$PREFIX/$TMPDIR, follows symlinks, reports the mount backing
the path, and lists every Android-equivalent spelling (/sdcard <->
/storage/emulated/0 <-> $HOME/storage/shared). Equivalent inputs:
/sdcard/Download/x.txt, $HOME/storage/shared/Download/x.txt,
~/storage/shared/Download/x.txt, and relative docs/report.md (against cwd).
Expansion: ~ and $HOME become the server's HOME; $PREFIX is the install
prefix (e.g. /data/data/com.termux/files/usr); $TMPDIR is the server's own
temp dir, never the client's. Useful when a path has to be handed to a shell
command or another tool; not needed for paths already known-good on plain
Linux. Sibling boundary: `path_adapter` reports the environment map itself
(env class, HOME/PREFIX/TMPDIR, mount roots) and takes no arguments;
`resolve_path` reports one concrete path. Use `path_adapter` for the
environment, `resolve_path` for a candidate path. Returns {input, expanded,
resolved, env, exists, is_dir, is_file, is_symlink, readable, writable,
executable, mount, alternatives, warnings}.
```
### `server_health`
```
Read-only self-diagnostics for this MCP server process: pid/ppid, runtime
class, uptime, request and tool-call counters, tracked live child processes,
RSS, and the Android Phantom Process Killer risk assessment. Use it to verify
the server is alive, to debug client-side disconnects, or to check whether
orphaned children are accumulating on Android. Not for the device itself: use
`device_status` for battery, storage, arch and memory. Returns {server,
children, memory, phantom_process}.
```

---

## 十、提分路径与天花板（量化验证）

> 本节所有数字均由官方整数原语实测得出（`round1(num, den) = (2 × num + den) // (2 × den)`，全程 tenths 整数运算），
> 可用第 2.1 节三行公式逐项复算。**不是估算，是可复现的精确值。**
> 自检锚点：`Σtdqs=175, n=4, min=43` → `1738/400 = 4.345 → 4.3`；`C=3.5` → `406/100 = 4.06 → 4.1`，与页面一致。

### 10.1 反解表：给定 Q，打到目标总分所需的最小 C

| Q \ 目标 | 4.2 | 4.3 | 4.4 | 4.5 |
|---|---|---|---|---|
| **4.1** | C≥4.3 | C≥4.6 | C≥5.0 | 不可能 |
| **4.2** | C≥4.1 | C≥4.4 | C≥4.7 | 不可能 |
| **4.3**（当前） | **C≥3.8** | C≥4.2 | C≥4.5 | C≥4.8 |
| **4.4** | C≥3.6 | C≥3.9 | C≥4.3 | C≥4.6 |
| **4.5** | C≥3.4 | C≥3.7 | C≥4.0 | C≥4.4 |
| **4.6** | C≥3.1 | C≥3.5 | C≥3.8 | C≥4.1 |
| **4.7** | 3.0 即可 | C≥3.2 | C≥3.6 | C≥3.9 |
| **4.8** | 3.0 即可 | 3.0 即可 | C≥3.3 | C≥3.7 |
| **4.9** | 3.0 即可 | 3.0 即可 | C≥3.1 | C≥3.4 |

读法：当前 `Q=4.3`、`C=3.5`。**要把总分从 4.1 抬到 4.2，只需 C 从 3.5 涨到 3.8** —— 也就是 Coherence 四维里任意一个 +1 分即可。这是全表最关键的一格。

注意表里 `Q=4.1` 行：若 Q 掉到 4.1，到 4.2 要 C≥4.3（几乎要 C 全满），**说明 Q 掉一档的代价远大于 C 涨一档的收益**，任何改动都不能让 `min(tdqs)` 变差。

### 10.2 单杆阶梯：只改一件事

| 杠杆 | 具体改动 | Q | C | 总分 | 相对 4.1 |
|---|---|---|---|---|---|
| **A** Naming Consistency 3→4 | 统一动宾式命名（纯描述层，**零代码**） | 4.3 | **3.8** | **4.2** | **+0.1 ✅** |
| **B** `resolve_path` Parameter 3→4 | 补 `$PREFIX/bin`、`/sdcard/Download` 等格式示例 | **4.4** | 3.5 | **4.1** | **0 ❌** |
| **C** Completeness 3→4 | 加只读 `list_dir`（消除 "dead end for action"） | 4.3 | **3.8** | **4.2** | **+0.1 ✅** |
| **D** Tool Count 4→5 | 加第 5 个工具 | 4.3 | **3.8** | **4.2** | **+0.1 ✅** |
| **E** Disambiguation 4→5 | 把兄弟边界写进描述首句 | 4.3 | **3.8** | **4.2** | **+0.1 ✅** |

**这张表推翻了「补 `resolve_path` 参数示例最划算」的直觉**：B 把 Q 从 4.3 抬到 4.4（`resolve_path` 单项 4.4→4.5），但因为 C 仍卡在 3.5，
`(7×44 + 3×35)/100 = 413/100 = 4.13 → 4.1`，**一分没涨**。
根因有二：一是 `min(tdqs)` 仍是 43（`server_health`），60/40 口径下 Q 的增益被最小值项稀释；二是 C 不动就过不了 4.15 的 half-up 门槛。

### 10.3 组合阶梯：到 4.2 / 4.3 / 4.4 的最短路径

| 组合 | Q | C | 总分 |
|---|---|---|---|
| A + B | 4.4 | 3.8 | **4.2** |
| A + B + C | 4.4 | 4.0 | **4.3** |
| A + B + C + D | 4.4 | 4.3 | **4.4** |
| A + B + C + D + E | 4.4 | 4.5 | **4.4**（饱和） |

- **到 4.2 有四条独立路径**（A / C / D / E 任一即可），其中 A 最便宜：只改描述与命名，不动一行逻辑。
- **到 4.3 必须组合**：`Q` 得进到 4.4（靠 B），`C` 得进到 4.0（A + C）。
- **到 4.4 要 A+B+C+D**：除 Disambiguation 外四维全提，且必须真的加工具（Tool Count 只能靠加工具涨）。
- **E 在 4.4 之后是白送的**：A+B+C+D 已到 4.4，再补 Disambiguation 到 5 仍停在 4.4（`(7×44+3×45)/100 = 443/100 = 4.43 → 4.4`），说明 4.4 之后 C 已不是瓶颈，Q 才是。

### 10.4 天花板

| 情形 | 单工具上限 | 计算 |
|---|---|---|
| Parameter Semantics 停在 **3** | **4.7** | `[5,5,5,3,5,5]` = 470/100 → 4.7 |
| Parameter Semantics 停在 **4** | **4.9** | `[5,5,5,4,5,5]` = 490/100 → 4.9（当前四工具均受此限） |
| Parameter Semantics 到 **5** | **5.0** | 只有 schema 本身能拿满，光写描述拿不到 5 |

**结论**：本仓库四个工具的 Parameter Semantics 分别是 4 / 4 / 3 / 4，因此**单工具天花板 4.9，`resolve_path` 的天花板是 4.7**。
即使把其余五个维度全部写满，`resolve_path` 也到不了 5.0 —— 这是 schema 决定的硬顶，不是文案问题。
四工具全拉满（param=4）时 `Q=4.9`、`C=5.0`、总分 **4.9**，即**本仓库在不改 schema 前提下的绝对上限**。

### 10.5 三条可直接引用的判断

1. **4.1 不是天花板，4.9 才是**；但从 **4.1 到 4.2 的成本几乎为零**（改命名即可），从 4.4 往上才需要动代码。
2. **单改描述涨不动分**：B 实验证明「只补 `resolve_path` 参数示例」在 C 不变时**一分不涨**，必须先动 C。
3. **C 是 4.1→4.2 的唯一钥匙**：Q 已经 4.3，C 只差 0.3；而 C 的四个维度里三个都能靠「加一句路由语 / 加一个只读工具」解决，不需要改 schema。

---

## 十一、变更记录

| 日期 | 版本 | 说明 |
|---|---|---|
| 2026-10-25 | — | 首次核验并建档。快照对应 TDQS 4.1 / 4 工具 / `HEAD 46cbb5e` |
| 2026-10-25 | — | 工具描述改写（兄弟工具路由 + 格式示例），四段描述基线同步更新；仅改 description，schema/行为未变 |
| 2026-10-25 | — | 补入官方整数三行公式、三条警告、80% 覆盖率门槛；来源更正为 GitHub 开源 spec（原 `/spec` 等四地址已 404） |
| 2026-10-25 | — | 新增第十章「提分路径与天花板」：反解表、单杆阶梯、组合阶梯、天花板，全部经整数原语实测 |
| 2026-10-25 | — | 抓取 `tdqs.dev/spec` 原文，发现官方明确把 "always call this first" 列为 enforce-an-ordering 反模式；改写 `resolve_path` 与 `path_adapter` 三处时序指令句，改为「问题分工」表述，第九章新增措辞红线核查小节 |
| 2026-10-25 | — | 合并两版文档：保留官方整数原语口径（弃用旧 70:30 反解写法），补回 `1.1.3` 自增证据（3.6） |
| 2026-10-25 | — | 新增 3.7「抓取源定论」：四段描述归一化 4/4 + README 标记矩阵 + 版本号 + 时间线，四证锁定快照对应 GitHub `46cbb5e`，非 PyPI 包；记录提取正则 `class` 在 `id` 前的坑 |
