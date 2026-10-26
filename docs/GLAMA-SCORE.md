# Glama 评分核验报告

> 本文件记录 `nano-mcp-termux` 在 [Glama.ai](https://glama.ai/mcp/servers/Lmeng486/nano-mcp-termux) 上的评分快照、版本元数据核验过程与结论。
> 目的是：**下次对 Glama 评分有疑问时，先看这里，不必从头排障。**

- 快照时间：**2026-10-25 16:55（Glama 侧评分时间戳）**（首次快照 10:30 已被本次重抓覆盖）
- 抓取时间：2026-10-25
- 核验对象：`Lmeng486/nano-mcp-termux`（PyPI: `nano-mcp-termux`，官方 Registry: `io.github.Lmeng486/nano-mcp-termux`）
- 核验仓库状态：本地 `HEAD = f698e91`，远端 `main` 同提交
- 数据来源：Glama 页面 HTML（公开 API 需 API key，返回 401）

---

## 一、结论速览

| 项目 | 结果 | 判定 |
|---|---|---|
| Quality Grade | **A** | ✅ |
| Maintenance Grade | **A** | ✅ |
| License Grade | **A** | ✅ |
| TDQS 总分 | **A · 4.6 / 5.0**（4 个工具聚合） | ✅ 上等区间 |
| Server Coherence | 5 / 4 / 4 / 4（四维度） | ✅ 已无 3 分项 |
| ⚠️ UI 告警 | **无** | ✅ 已核实排除 |
| 认领状态 | `author:claimed` | ✅ 已认领 |
| 版本 `1.1.2` / `1.1.3` 疑点 | Glama 内部 release 编号自增，非发布物 | ✅ 无需处理 |

**一句话总结**：服务器状态健康，评分扎实，此前担心的两个问题（页面 ⚠️ 告警、版本号不一致）**均不成立**；重抓后总分由 `4.1` 升至 `4.6`，Coherence 已无 3 分项。

---

## 二、评分明细

### 2.1 四工具 TDQS 全量明细

| 工具 | 等级 | 总分 | Behavioral<br>Transparency (20%) | Conciseness<br>(10%) | Contextual<br>Completeness (10%) | Parameter<br>Semantics (15%) | Purpose<br>Clarity (25%) | Usage<br>Guidelines (20%) |
|---|---|---|---|---|---|---|---|---|
| `device_status` | A | **4.7** | 4 | 5 | 5 | 4 | 5 | 5 |
| `path_adapter` | A | **4.8** | 5 | 5 | 4 | 4 | 5 | 5 |
| `resolve_path` | A | **4.8** | 5 | 4 | 5 | 4 | 5 | 5 |
| `server_health` | A | **4.7** | 4 | 5 | 5 | 4 | 5 | 5 |

- 极差仅 **0.1**，四份描述质量均衡，无短板工具。
- **已无 3 分维度**：此前 `resolve_path` 的 Parameter Semantics 3 分已升至 4 分（四个工具 Parameters 现均为 4）。
- 四工具 24 个维度中 **16 个为 5 分、8 个为 4 分，无 3 分及以下**。8 个 4 分项是：四工具各自的 Parameters（4 处，零参数工具基线即 4，属规格上限）+ `device_status` Behavior + `path_adapter` Completeness + `resolve_path` Conciseness + `server_health` Behavior。

**TDQS 聚合口径**（已用官方开源仓库 spec 的整数原语 + 精确有理数运算，100% 复现页面全部五个分数）：

```
单工具分 = Σ(维度分 × 权重) / 100      # 结果落在 0.1 网格
Q       = 0.6 × mean(单工具分) + 0.4 × min(单工具分)
C       = mean(coherence 四维)
总分     = 0.7 × Q + 0.3 × C
```

代入实测值：单工具 `4.7 / 4.8 / 4.8 / 4.7` → `mean = 4.75`、`min = 4.7` →
`Q = 0.6×4.75 + 0.4×4.7 = 4.73 → 4.7`；`C = (5+4+4+4)/4 = 4.25 → 4.3`；
`总分 = 0.7×4.7 + 0.3×4.3 = 4.58 → 4.6`。**与页面徽章 `4.6`、`overallScore 4.6`、`coherenceScore 4.3` 全部一致。**

**官方 spec 原文的整数实现（照抄这三行即可复现，权威性高于任何页面反解）**：

```
descriptionQualityScore = round1(6 × Σ tdqs + 4 × n × min(tdqs), 100 × n)
coherenceScore          = round1(disambiguation + namingConsistency
                                 + toolCountAppropriateness + completeness, 4)
overallScore            = round1(7 × descriptionQualityScore + 3 × coherenceScore, 100)
```

其中 `tdqs` 是单工具的十分位整数（10–50，即 `4.4 → 44`），`n` 是工具数，`round1` 是整数 half-up 原语
`round1(num, den) = (20 × num + den) // (2 × den)`（返回**十分位整数**，如 `round1(1892, 400) = 47`，即 `4.7`）。
代入 `Σtdqs = 47+48+48+47 = 190`、`n = 4`、`min = 47`：
`(6×190 + 4×4×47) / (100×4) = (1140 + 752) / 400 = 1892/400 = 4.73 → 4.7`；
`C = (5+4+4+4)/4 = 4.25 → 4.3`；`(7×47 + 3×43)/100 = 458/100 = 4.58 → 4.6`。
与上面的分数式写法结果完全等价，但整数写法不会踩浮点。

> 注：若把 `Q` 简化为纯均值 `4.75`，总分也是 `4.6`（`0.7×4.75+0.3×4.25=4.60`），仅凭页面总分无法区分两种口径；此处采用官方 spec 的 `60/40` 定义，因为它能同时解释 `min` 项的存在意义。
> 旧版本文档写的「w = 0.70 反解、无最小值参与」是当时未拿到 spec 时的推测，已废弃。

> **来源更正**：`https://glama.ai/spec`、`/mcp/spec`、`/spec/tdqs`、`/docs/tdqs` 四个地址当前**全部 404**。
> 权威来源已迁移到 GitHub 开源仓库 `glama-ai/tool-definition-quality-score` 与 `tdqs.dev`（v1.2 规范）。
> 本节公式取自该仓库原文，不是页面反解。

**⚠️ 量纲陷阱（复现时最容易踩的坑）**：必须全程用整数 tenths/hundredths 运算并显式 half-up。
实测 Python 内置 `round()` 采用银行家舍入，会把 `4.25 → 4.2`、`4.85 → 4.8`，直接把 `server_health` 从 4.3 算成 4.2、总分算错。
正确 half-up：`def hu(p,q): return (2*p+q)//(2*q)`。

官方 spec 对此有三条明确警告，逐条都是会真扣 0.1 分的实操陷阱：

1. **`mean` 必须是精确的 `Σtdqs / n`，不能用已发布的保留一位小数的 `meanTdqs`。**
   本条实测踩中：先把 `mean` 取整成 `4.8`，再算 `0.6×4.8 + 0.4×4.7 = 4.76 → 4.8`，
   `Q` 被错算成 `4.8`（正确 `4.7`），总分随之错算成 `4.6` 之外的值。必须用 `4.75`。
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
| Disambiguation（消歧） | **5 / 5** | 评语原话：「Each tool targets a distinct question: device hardware (`device_status`), server process state (`server_health`), one candidate path (`resolve_path`), and the runtime path environment (`path_adapter`). **Descriptions explicitly state sibling boundaries and even tell the agent which tool to use instead**, eliminating misselection.」—— 本轮描述改写的核心成果：兄弟路由语从无到有，此项由 4 分升至满分 |
| Naming Consistency（命名一致） | **4 / 5** | 「All names are snake_case and self-describing, with a clear domain term per tool. **The pattern is noun_noun for three tools (`device_status`, `server_health`, `path_adapter`) and verb_noun for one (`resolve_path`), a minor deviation** that is still highly readable.」—— 仅剩 `resolve_path` 一个动宾式命名的小偏差，不足以扣到 3 分 |
| Tool Count（工具数量） | **4 / 5** | 「Four tools is **on the small side** but each covers a distinct, non-overlapping diagnostic concern, so nothing feels padded or redundant. The surface is tightly scoped to introspection rather than trying to be a general shell wrapper.」—— 数量偏少是此维度的结构性天花板，4 个工具无法自己涨到 5 |
| Completeness（完整性） | **4 / 5** | 「The stated domain — read-only device, server, and path introspection — is well covered, including Android-specific concerns like phantom processes and shared-storage aliases. **Minor gaps remain** (no general process/network/log inspection), **but agents can work around these via other tools or shell commands.**」—— 从 3 分升 4 分的关键是描述里写明了「变通路径」，评审因此不再判定为死路 |

### 2.3 逐工具评语中的扣分原因（可直接转改进项）

24 个维度中已无 3 分及以下，剩余 **8 个 4 分项**，逐条列出（评语原话摘录）：

| 工具 | 维度 | 扣分原因（评语原文要点） | 可改进性 |
|---|---|---|---|
| `device_status` | Behavioral Transparency (4) | 「The annotations already declare `readOnlyHint`, `idempotentHint`, and `destructiveHint=false`, so safety is covered... That partial-failure behavior is the key thing an agent needs, **though it says nothing about freshness/caching of the snapshot or cost of the call**.」 | ✅ 可改：补一句「快照为实时读取、无缓存、单次调用开销极小」 |
| `device_status` | Parameter Semantics (4) | 「**Zero parameters, so there is nothing to disambiguate and the baseline is 4.**」 | ❌ 不可改：零参数工具的结构性上限 |
| `path_adapter` | Contextual Completeness (4) | 「It is complete for a zero-parameter read-only diagnostic tool, **though it could mention whether the reported environment is cached or live**.」 | ✅ 可改：补一句「环境为实时读取，反映调用时刻的进程状态」 |
| `path_adapter` | Parameter Semantics (4) | 同 `device_status`：零参数，基线即 4 | ❌ 不可改 |
| `resolve_path` | Conciseness (4) | 「**It is somewhat dense and run-on in the first sentence**, but the density is justified by the number of path-expansion rules being communicated.」 | ✅ 可改：首句拆成两句 |
| `resolve_path` | Parameter Semantics (4) | 「**Schema coverage is 100%, so the baseline is 3, but the description adds meaningful semantics beyond the schema**: concrete equivalent input forms, relative-path handling against the working directory, and the specific meanings of `~`, `$HOME`, `$PREFIX`, and `$TMPDIR`. The schema already covers required/non-empty behavior, so this is not a full 5.」 | ✅ 已从 3 升 4（本轮唯一升档项）；再涨需描述给出 schema 之外的新信息 |
| `server_health` | Behavioral Transparency (4) | 「Annotations already declare readOnly, idempotent, non-destructive and closed-world... **It stops short of saying anything about cost, frequency, or what an unhealthy result looks like**, but the scope and content disclosure is solid.」 | ✅ 可改：补一句异常形态（`status: "unhealthy"` 时返回哪些字段） |
| `server_health` | Parameter Semantics (4) | 同前：零参数，基线即 4 | ❌ 不可改 |

**共性诊断（本轮已基本消化）**：上一版 7 条扣分里有 5 条指向同一个根因 —— **描述没有点名兄弟工具、没有 "use X instead of Y when Z" 的路由语**。本轮描述改写补入兄弟路由语后，`Disambiguation` 由 4 涨到 5，`device_status` / `server_health` 的 Purpose 与 Usage 全部升到 5，`resolve_path` 的 Purpose 也升到 5 —— **这条根因已不再是扣分项**。

**新浮现的共性根因**：剩余可改的 4 个 4 分项（`device_status` Behavior、`path_adapter` Completeness、`server_health` Behavior、`resolve_path` Conciseness）共同指向 **「运行时语义披露不足」** —— 即「数据是实时还是缓存」「调用代价多大」「异常时返回什么形态」这三类信息。这是下一轮改写的目标，但**受聚合公式与权重门槛限制，单项改写未必能换来分数变化**（见第十节）。

**4 个不可改项**：四工具各自的 Parameter Semantics 均为 4，原因是零参数工具「there is nothing to disambiguate and the baseline is 4」。这是评分规范对零参数工具的硬基线，**除非给工具加参数，否则永远涨不到 5**。

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
2. `bb0448c` 已 push 到 `main`，动作正确且充分。**重抓已于 2026-10-25 16:55 完成**：`observedAt` / `scoredAt` 均已推进，快照由 TDQS 4.1 更新为 **4.6**（四工具 4.7 / 4.8 / 4.8 / 4.7），实测证明「改 description → push → 手动重抓」这条链路端到端可用。
3. 判定「是否真的重抓」只看 `observedAt` / `scoredAt` 是否推进，不看 `githubProject.version`（见 3.6）。


---

## 四、可执行的优化建议（按投入产出排序）
> 前提：当前 `Q=4.7`、`C=4.3`、总分 **4.6**。本章所有排序都以「能否真的让总分进位」为准，
> 而不是以「某个维度看起来差多少分」为准——两者在 half-up 聚合下经常不一致（见第十节）。
### 优先级 1 — 补「运行时语义披露」（唯一能立刻 +0.1 的动作）
当前 `Q=4.7`，**只要 `Q` 涨到 4.8 总分就是 4.7**。而 `Q` 涨到 4.8 并不需要四项全动，
只要 `Σtdqs` 从 190 抬到 192、且 `min(tdqs)` 不下降即可 —— **任意一个 4.7 分的工具升到 4.8 就够了**。

两条等价的单杆路径（二选一，均已实测到 **4.7**）：

| 路径 | 改动 | 具体补什么 |
|---|---|---|
| **D** | `device_status` Behavioral Transparency 4→5 | 「快照为实时读取、无缓存；单次调用开销极小」 |
| **E** | `server_health` Behavioral Transparency 4→5 | 「`status` 为 `unhealthy` 时返回哪些字段、异常形态是什么」 |

评语已经把缺的东西点名到句子级别：
> 「…**it says nothing about freshness/caching of the snapshot or cost of the call**.」（`device_status`）
> 「**It stops short of saying anything about cost, frequency, or what an unhealthy result looks like**…」（`server_health`）

这两句都是**纯描述层改动，零代码、零 schema 变更、无 breaking change**，是全书性价比最高的动作。

⚠️ **`D` 与 `E` 不要同时做**：实测 `D+E` 仍是 4.7（`Q` 卡在 4.8、`C` 未动），第二句是白写的。
先落一条，等 `C` 跟上再看要不要补另一条。
### 优先级 2 — `resolve_path` 首句拆句（不涨分，但降风险）
评语：「**It is somewhat dense and run-on in the first sentence**, but the density is justified…」
把首句按「展开规则 / 相对路径处理 / 等价输入形式」拆成两三句，可读性提升。

⚠️ **实测不涨分**：`F`（`resolve_path` Conciseness 4→5）→ 该工具 4.8→4.9、`Σtdqs` 191、
`Q=round1(6×191+4×4×47,400)=1898/400=4.745→4.7`，**差 0.005 卡在 half-up 门外**，总分不动。
所以这一项只按「可读性债」做，别指望分数。
### 优先级 3 — Coherence 两维 +1（另一条到 4.7 的路，但成本高）
`A`（Naming 4→5）+`C`（Completeness 4→5）→ `C` 由 4.3 到 4.8、`Q` 不变，总分 **4.7**。
- 只动**一维**是无效的：`C` 会停在 4.5，`round1(7×47+3×45,100)=464/100=4.64→4.6`，一分不涨。
- 因为 `C` 只能取 `4.3 / 4.5 / 4.8 / 5.0` 四个离散值（四维和只可能 17/18/19/20），**没有「涨一点」的中间档**。
- 成本上，`A`（改命名）是 breaking change，`C`（加只读 `list_dir`）是新增工具面 —— 都比优先级 1 贵得多。
### 优先级 4 — 4.8 起必须「双轨」
到 **4.8** 需要 `Q=4.8` 且 `C=4.8` 同时成立：
- `Q=4.8` → 优先级 1 的 D 或 E；
- `C=4.8` → 优先级 3 的 A + C 两维同时 +1。

即 `D + A + C` 组合（实测 4.8）。单轨任何一条路都封顶在 4.7。
到 **4.9** 则必须 `Q=4.9`（四工具全部 4.9，即 `D+E+F+G`）**且** `C≥4.8`（`A+C`）—— 五处改动同时落地，性价比陡降。
### 不建议做的事
1. **不要为了 Tool Count 加第 5 个工具**。`B`（加一个同为 4.7 的第 5 工具）只把 `C` 抬到 4.5，总分仍 4.6；
   而它同时扩大了 schema 面、测试面和 release 面。**纯负收益。**
2. **不要改 schema 去追 Parameter Semantics**。四个工具里三个零参数、一个 100% schema 覆盖，
   基线由规范硬定为 4；加参数只会破坏「零参数只读诊断」这个已有加分点。
3. **不要指望单维 Coherence**。`C` 离散，单维 +1 只到 4.5，跨不过 4.64 的门槛。
### 收尾提醒
- 描述改完**不会自动生效**：Glama 无 webhook、无 resync API，只能由仓库所有者登录 GitHub OAuth 后
  在 `Repository syncs` 面板手动点重抓。
- 判断是否真的重抓成功，**只认页面上的 `observedAt` / `scoredAt` 是否推进**，不要看 README 里写的分数
  （README 是仓库侧文本，与评分快照无关；页面抓的 README 可能长期滞后于仓库最新版）。

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
> 自检锚点：`Σtdqs=190, n=4, min=47` → `1892/400 = 4.73 → 4.7`；`C=4.25→4.3` → `458/100 = 4.58 → 4.6`，与页面一致。
### 10.1 反解表：给定 Q，打到目标总分所需的最小 C
| Q \ 目标 | 4.7 | 4.8 | 4.9 | 5.0 |
|---|---|---|---|---|
| **4.5** | C≥5.0 | 不可能 | 不可能 | 不可能 |
| **4.6** | C≥4.8 | 不可能 | 不可能 | 不可能 |
| **4.7**（当前） | **C≥4.6** | C≥4.9 | 不可能 | 不可能 |
| **4.8** | C≥4.3（已满足） | C≥4.7 | C≥5.0 | 不可能 |
| **4.9** | C≥4.1 | C≥4.4 | C≥4.8 | 不可能 |
| **5.0** | C≥3.9 | C≥4.2 | C≥4.5 | C≥4.9 |

⚠️ **这张表必须配合「C 的离散性」读**：Coherence 四维和 `S_c` 只可能是 17 / 18 / 19 / 20，
经 `round1(S_c, 4)` 分别得 **4.3 / 4.5 / 4.8 / 5.0** —— **`C=4.6` 与 `C=4.7` 物理上不可达**。
因此表里所有形如「C≥4.6」「C≥4.7」的格子，实际含义都是「**C 必须直接跳到 4.8**」（两维同时 +1）。

读法：当前 `Q=4.7`、`C=4.3`、总分 4.6。到 4.7 有**两条互相独立**的路：
- **抬 Q**：`Q=4.8` 时只要 `C≥4.3`（现状即满足）→ 见 10.2 的 D 或 E，**改一句描述即可**；
- **抬 C**：`C` 从 4.3 直接到 4.8（两维 +1）→ 见 10.2 的 A+C，**要改命名或加工具**。

**两条路的成本差一个量级，优先级由此确定。**
注意 `Q=4.5` / `4.6` 两行：`Q` 一旦掉档，到 4.7 就必须 `C≥5.0` 或直接不可能 ——
**任何改动都不能让 `min(tdqs)` 变差**，Q 掉一档的代价远大于 C 涨一档的收益。
### 10.2 单杆阶梯：只改一件事（基线 4.6）
| 杠杆 | 具体改动 | 四工具单项 | Q | C | 总分 | 相对 4.6 |
|---|---|---|---|---|---|---|
| **D** `device_status` Behavior 4→5 | 补「实时无缓存、调用开销极小」 | 4.9/4.8/4.8/4.7 | **4.8** | 4.3 | **4.7** | **+0.1 ✅** |
| **E** `server_health` Behavior 4→5 | 补「unhealthy 时返回什么」 | 4.7/4.8/4.8/4.9 | **4.8** | 4.3 | **4.7** | **+0.1 ✅** |
| **F** `resolve_path` Conciseness 4→5 | 首句拆句 | 4.7/4.8/**4.9**/4.7 | 4.7 | 4.3 | 4.6 | 0 ❌ |
| **G** `path_adapter` Contextual 4→5 | 补「环境为实时读取」 | 4.7/**4.9**/4.8/4.7 | 4.7 | 4.3 | 4.6 | 0 ❌ |
| **A** Coherence Naming 4→5 | 统一动宾式（breaking change） | 不变 | 4.7 | **4.5** | 4.6 | 0 ❌ |
| **C** Coherence Completeness 4→5 | 加只读 `list_dir` | 不变 | 4.7 | **4.5** | 4.6 | 0 ❌ |
| **B** Tool Count 4→5 | 加第 5 个工具（同为 4.7） | 4.7/4.8/4.8/4.7/4.7 | 4.7 | **4.5** | 4.6 | 0 ❌ |
| **H** Parameter 全 4→5 | 改 schema（零参数工具不可达） | 5.0/5.0/5.0/5.0 | **5.0** | 4.3 | 4.8 | 不可达 |

**F / G 为什么明明抬了单项却不涨分**：单项 4.8→4.9 让 `Σtdqs` 从 190 到 191、`mean` 从 47.5 到 47.75，
但 `Q = round1(6×191 + 4×4×47, 400) = 1898/400 = 4.745 → 4.7`，**差 0.005 进不了 4.8**。
而 `C` 不动，`7×47 + 3×43 = 458/100 = 4.58 → 4.6`。**「多补几项总会涨」在这里不成立。**
**A / C / B 为什么也不涨**：三者都只动 `C` 一维，`C` 停在 4.5，
`7×47 + 3×45 = 464/100 = 4.64 → 4.6`，仍在档内。**要动 C 就必须一次动两维（到 4.8）。**
### 10.3 组合阶梯：到 4.7 / 4.8 / 4.9 的最短路径
| 组合 | Q | C | 总分 | 备注 |
|---|---|---|---|---|
| **D**（或 **E**） | 4.8 | 4.3 | **4.7** | 最便宜的单步 |
| **A + C** | 4.7 | 4.8 | **4.7** | 另一条独立路径，成本高 |
| **D + E** | 4.8 | 4.3 | **4.7** | **饱和**：第二句 Behavior 白写 |
| **D + E + A** | 4.8 | 4.5 | **4.7** | C 只到 4.5，仍不够 |
| **D + A + C** | 4.8 | 4.8 | **4.8** | **推荐**：到 4.8 的最短路径 |
| **D + E + A + C** | 4.8 | 4.8 | **4.8** | 与 D+A+C 同分，E 多余 |
| **D + E + F + G**（四工具全 4.9） | 4.9 | 4.3 | **4.7** | Q 拉满但 C 拖后腿 |
| **D + E + F + G + A** | 4.9 | 4.5 | **4.8** | C 仍只到 4.5，靠 Q 撑 |
| **D + E + F + G + A + C** | 4.9 | 4.8 | **4.9** | 到 4.9 需五处全动 |
| **D + E + A + C + B** | 4.8 | 5.0 | **4.9** | 用第 5 工具补 C，但多一个工具面 |

- **到 4.7 有两条独立路径**（`D`/`E` 任一，或 `A+C`），前者只改一句话，后者要动命名或加工具。
- **`D + E` 是饱和的**：`Q` 到 4.8 后第二句 Behavior 不再加分，**先做一条即可**。
- **到 4.8 必须双轨**：`Q` 与 `C` 同时进位。`D + A + C` 比 `D+E+F+G+A` 划算得多（三处 vs 五处）。
- **到 4.9 只有两条路**：`Q=4.9` + `C=4.8`（五处改动），或 `Q=4.8` + `C=5.0`（四维全满 + 加工具）。
### 10.4 天花板
| 情形 | 单工具上限 | 计算 | C=4.3 时总分 | C=5.0 时总分 |
|---|---|---|---|---|
| Parameter Semantics 停在 **3** | **4.7** | `[5,5,5,3,5,5]` = 470/100 → 4.70 → 4.7 | 4.6 | 4.8 |
| Parameter Semantics 停在 **4**（**当前四工具均如此**） | **4.9** | `[5,5,5,4,5,5]` = 485/100 → 4.85 → 4.9 | 4.7 | 4.9 |
| Parameter Semantics 到 **5** | **5.0** | `[5,5,5,5,5,5]` = 500/100 → 5.0 | 4.8 | 5.0 |

> 注：`[5,5,5,3,5,5]` 的权重和为 `20×5 + 10×5 + 10×5 + 15×3 + 25×5 + 20×5 = 470`，即 **4.70 → 4.7**（上一版此格计算正确，但把 param=4 行误写成 `490`，正确值是 `485`，已修正）。

**结论**：本仓库四个工具的 Parameter Semantics **均为 4**（三个零参数工具基线 4，`resolve_path` 因 schema 覆盖 100% 基线 3 但描述补足语义后判 4），
因此**单工具天花板统一是 4.9，不是 4.7** —— 上一版「`resolve_path` 天花板 4.7」的结论已失效。
即使把其余五个维度全部写满，也到不了 5.0：**这是 schema 决定的硬顶，不是文案问题。**
四工具全拉满（param=4）时 `Q=4.9`、`C=5.0`、总分 **4.9**，即**本仓库在不改 schema 前提下的绝对上限**。
（`7×49 + 3×50 = 343 + 150 = 493/100 = 4.93 → 4.9`；**5.0 需要 `Q=5.0` 与 `C=5.0` 同时成立，而 `Q=5.0` 要求四个工具全部 param=5，不可达。**）
### 10.5 三条可直接引用的判断
1. **4.6 不是天花板，4.9 才是**；但从 **4.6 到 4.7 的成本几乎为零**（补一句 Behavior 描述），
   从 4.7 到 4.8 才需要动命名/工具面，从 4.8 到 4.9 需要五处同时落地。
2. **单改一个不痛不痒的维度涨不动分**：F / G 把单项抬了 0.1、A / C / B 把 C 抬了 0.2，
   **全部停在 4.6**。原因是 `Q` 卡 half-up（1898/400=4.745）与 `C` 离散（4.5 跨不过 4.64）两个独立的门。
3. **Q 与 C 是两个独立的门，必须分别过**：`Q` 的门槛是「`Σtdqs` 进到 192 且 min 不降」，
   `C` 的门槛是「四维和至少 +2」。**任何一个门没过，另一个门涨了也不进档** ——
   这正是 10.2 里七条单杆路径有六条无效的根本原因。

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
| 2026-10-25 | — | **重抓生效**：16:55 手动触发 `Repository syncs`，`observedAt` / `scoredAt` 推进，TDQS 由 **4.1 → 4.6**；四工具 4.7 / 4.8 / 4.8 / 4.7，24 个维度中 16 个 5 分、8 个 4 分，Coherence 四维 5 / 4 / 4 / 4。同步更新 1.x 摘要、2.1 表、3.7 影响段与 README 徽标 |
| 2026-10-25 | — | **第四、十章按新基线全量重写**：确立 `C` 离散只取 4.3 / 4.5 / 4.8 / 5.0（4.6 / 4.7 不可达）、`D` 或 `E` 单杆即可 4.6 → 4.7、四工具 param 均为 4 故统一顶 **4.9**（绝对上限 4.93）、5.0 需 schema 变更故不可达；10.4 权重和修正为 param=3 → 470/100、param=4 → 485/100 |
