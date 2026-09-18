# ai.nornless.com · 功能设计：对外站 + 后台管理（Python 后端）

更新：2026-09-14 16:30
路径：`/Users/himma/01/01Agent学习/aigc知识付费`
状态：**功能与约束规格，已按 04 / 05 定稿内容推导；后端语言 Python 为用户定案**
上游：`04-阶见合并规划-广告为主.md`（做什么、靠什么活）、`05-产品推导-体验优先与广告开关.md`（用户拿到什么、每页怎么工作）
本文定：**每个功能的输入、规则、状态、权限、限制、错误与验收**；对外站、读者区、广告主门户、Studio 编辑部、Admin 运营后台五个面向全部覆盖；以及 Python 后端的架构约束。不含代码。
冲突处以本文为准（本文最新）；本文没写的以 `05` → `04` 为准。`04` §9.2 的 Next.js / pg-boss / Drizzle 技术栈由本文第 8 节取代，`04` §9 其余原则不变。

---

## 0. 定案、面向与全局约束

### 0.1 后端 Python：选型定案

| 层 | 定案 | 为什么 |
|---|---|---|
| 语言 / 运行时 | Python 3.12 | 用户定案 |
| Web 框架 | **Django 5.x（LTS 优先）** | 一个人维护：ORM + 迁移、认证 / 会话 / CSRF、表单校验、`sitemaps` 与 `syndication`（RSS）自带、缓存框架、管理命令、自带 admin 做原始表兜底。本站是 SSR 内容站 + 重后台，Django 的「电池」正好是我们要花时间的地方 |
| 页面渲染 | Django 模板 **服务端渲染** + **HTMX**（局部刷新）+ **Alpine.js**（微交互） | SEO 与首屏；无 SPA、无水合；`01` 的线框 HTML 与 `nornless.css` 直接变模板 |
| 机器接口 | **Django Ninja**（Pydantic v2 校验），`/api/v1/*` | CI 导入、日志上报、健康检查；人用页面不走 JSON API |
| 数据库 | PostgreSQL 16 + `pgvector` + `zhparser`（中文全文检索；不可用时退 `pg_trgm`） | 与 04 一致；镜像预装扩展 |
| 任务队列 | **Procrastinate**（PostgreSQL 队列，Django 集成，含周期任务） | 免 Redis；生成、抓源、聚类、保鲜、邮件、报表、OG 图都走它 |
| 模型调用 | `httpx` → nornless 中转站 `/v1/responses`（OpenAI 兼容），模型名配置化：`grok-4.6`（写 / 核）、`grok-build-0.1`（沙箱验证）、embedding 可换 | 与 `04` §9.2 一致；密钥只在 `.env` |
| Markdown | `markdown-it-py` + 插件（脚注、容器 callout、标题锚点）+ Pygments；front-matter 用 `python-frontmatter`；schema 用 Pydantic 生成 `front-matter.schema.json` / `cms-schema.json` | schema 单一真源在 Python，CI 与 Studio 共用 |
| 邮件 | 事务邮件与广播分开两个发件子域；供应商可换（SMTP / API 二选一配置）；退信 webhook 是全站**唯一**接受的外部回调 | 送达与信誉隔离 |
| 对象存储 | S3 兼容（R2 或 OSS），`django-storages` | 资源包、封面、广告素材、仓库 zip |
| 静态 | WhiteNoise + Caddy 缓存；字体子集化 | 公开页零第三方请求 |
| 统计 | 自托管 Umami（独立容器，经 Caddy 挂 `/u/` 同域） | 无 cookie；媒体页数据源 |
| 图片生成 | Pillow（OG 分享卡） | 不起无头浏览器 |
| 沙箱 | Docker 一次性容器（验证员跑代码） | 见 4.4 |
| 观测 | `structlog` JSON 日志；错误追踪自托管 GlitchTip（或 Sentry SaaS）；任务失败告警邮件 | 见 7.9 |
| 质量 | `uv`、`ruff`、`mypy`（django-stubs）、`pytest` + `pytest-django` + `factory-boy`、迁移检查、模板 lint | 见 8.9 |
| 部署 | Docker Compose：`web`（gunicorn）· `worker` · `scheduler` · `postgres` · `caddy` · `umami` · `umami-db`；独立 VPS；Cloudflare 解析 `ai.nornless.com`；**不上中转站 65 / 87 的 Caddy** | 与 04 §3.8 一致 |

被替代：`04` §9.2 的 Next.js 单仓、pg-boss、Drizzle、`worker/` Node 进程、`web/lib/*.ts`；`AGENTS.md` 的栈与目录随本文改。**没变**：数据模型语义、权益唯一真源、开关服务端求值、生成与发布隔离、服务端渲染广告、无第三方脚本。

### 0.2 五个人用面向 + 机器面向

| 面向 | 路径前缀 | 谁用 | 一句话 |
|---|---|---|---|
| 对外站 | `/`、`/learn`、`/articles`、`/news`、`/digest`、`/glossary`、`/tools`、`/compare`、`/topics`、`/search`、`/subscribe`、`/pricing`、`/redeem`、专区、公共页 | 所有人，匿名为主 | 读、学、查、订 |
| 读者区 | `/app/*`、`/account/*` | 登录读者、支持者 | 进度、收藏、下载、问答、账户 |
| 广告主门户 | `/ads/*`、`/advertise` | 广告主 | 兑码开通、素材、审核、报表 |
| Studio 编辑部 | `/studio/*` | Author(bot)、FactChecker、Editor、Publisher | 选题 → 生成 → 审 → 发 → 保鲜 |
| Admin 运营 | `/admin/*`；Django 原始 admin 在 `/django-admin/`（仅 Super） | AdOps、Ops、Finance、Admin、Super | 用户、码、开关、广告系统、邮件、SEO、系统 |
| 机器 | `/api/v1/*`、`/rss*`、`/sitemap*.xml`、`/robots.txt`、`/llms.txt`、`/go/<id>`、`/og/<key>.png`、`/u/`（Umami） | CI、bot skill、爬虫、邮件客户端、发卡站（无回调，人工导出）、邮件供应商退信 webhook | 契约见 2.19、8.6 |

### 0.3 全局约束 G1–G24（所有面向共用，后文只引用编号）

| 编号 | 约束 |
|---|---|
| G1 | **权限只在一处算**：`access` 服务导出 `entitlements(user)`、`visible(user, obj)`、`can_read_full(user, node)`、`quota(user, key)`、`sees_ads(user, slot)`、`can(actor, action, obj)`；模板、视图、API、RSS、任务全部调它，不得在别处写权限判断 |
| G2 | **开关服务端求值**：`flags` 服务一份配置（DB 表 + 进程内缓存 ≤ 30s）；关闭态 = 不渲染 + 路由 404 + 无入口 + 不埋点 + 不进 sitemap；模板不得用「隐藏」代替 |
| G3 | **写操作全部 POST + CSRF**；HTMX 请求带 CSRF 头；GET 幂等无副作用（`/go` 计数与 `/redeem` 校验除外，见各节） |
| G4 | **软删除**：内容、用户、广告、专区条目、码 一律 `deleted_at`，物理删除只在保留期任务里做（7.4） |
| G5 | **审计**：所有后台写操作记 `audit_logs(actor, action, obj_type, obj_id, before, after, reason, ip_hash, at)`；开关、码、权限、发布、广告上线、删除 必填 `reason` |
| G6 | **幂等**：导入、兑码、任务执行、邮件发送都有幂等键；重复请求返回首次结果 |
| G7 | **ID 与 slug**：内部主键 `bigint`；对外 URL 用 `slug`（`^[a-z0-9]+(-[a-z0-9]+)*$`，≤ 80）或日期；slug 改名自动写 301 重定向表；公开对象另有 `public_id`（12 位 Crockford base32）供分享卡与 `/go` |
| G8 | **时间**：DB 存 UTC；展示 Asia/Shanghai；早报「日期」按上海时区；所有对外日期格式 `YYYY-MM-DD` |
| G9 | **分页**：列表页 20 / 页，游标或页码；HTMX「加载更多」；最大 100 页（超过用搜索） |
| G10 | **输入长度**：所有文本字段有上限（附录 A）；超限拒绝不截断；服务端校验是唯一真源，前端限制只是提示 |
| G11 | **上传**：只在 Studio / Admin / 广告主门户；图片 png / jpg / webp ≤ 2MB，服务端重编码、去 EXIF、限最大边 2000px；禁 SVG（广告主）；资源包 zip ≤ 50MB；文件名重写为 `public_id.ext` |
| G12 | **限流**：按 IP 哈希 + 账号双维度（附录 D）；超限返回 429 与「几分钟后再试」 |
| G13 | **无 cookie 同意横幅**：只有 HttpOnly 会话 cookie（登录后）；主题 / 字号存 localStorage；Umami 无 cookie |
| G14 | **公开页零第三方请求**：字体自托管、图片自域、统计同域；只有发卡站店铺页可作为 iframe（CSP `frame-src` 白名单）|
| G15 | **CSP 严格**：`default-src 'self'`；脚本带 nonce；`frame-src` 只有发卡站；`img-src` 自域 + 对象存储域；广告素材不允许脚本 / 像素 / iframe |
| G16 | **每篇强制模块不可关**：AI 披露、Last-verified、来源、层徽章、前置 / 下一步、反馈（`05` §1 原则）；模板层没有隐藏它们的开关 |
| G17 | **广告与推广标识固定**：「广告」「赞助」「推广」角标由服务端模板注入，素材数据里没有该字段可改 |
| G18 | **红线词表** `editorial/redlines.txt`：内容、广告素材、专区条目、用户显示名、反馈文本 都过；命中 → 内容进 `machine_qa` 失败；广告 / 条目拒审；用户输入替换为「*」并记录 |
| G19 | **中文为唯一界面语言**；数字与价格带「截至 YYYY-MM-DD」；术语首次出现中英对照 |
| G20 | **无障碍**：WCAG 2.1 AA；所有交互键盘可达；HTMX 更新区块 `aria-live`；图片 alt 必填（front-matter 校验）|
| G21 | **性能预算**（公开页移动端 p75）：LCP ≤ 2.5s、CLS ≤ 0.1、INP ≤ 200ms；HTML ≤ 60KB gz、JS ≤ 40KB gz、CSS ≤ 30KB gz；推荐位与广告位固定尺寸预留 |
| G22 | **日志脱敏**：邮箱、IP、码、令牌不进日志；IP 只存 SHA-256(ip + 日轮换盐) |
| G23 | **密钥只在 `.env`**；轮换记录在 Admin 系统页；仓库、文档、日志、模板均不得出现 |
| G24 | **错误页**：404 带站内搜索与「你可能要找」；500 无堆栈；维护模式全站 503 + Retry-After，Studio / Admin 仍可登录 |

---

## 1. 角色、权限矩阵与权益判定

### 1.1 角色

| 类别 | 角色 | 说明 |
|---|---|---|
| 前台 | Guest | 匿名。读、搜、测评、快讯、订阅 |
| 前台 | Free | 邮箱注册。进度、收藏、划线、反馈署名、问答 3 / 日、示例资源 |
| 前台 | Supporter | 有效会员码期内。去广告、问答 20 / 日、资源包全部、会员 RSS、收费内容全文 |
| 前台 | GroupMember（V2） | 分组成员。按组规则 |
| 前台 | Advertiser | 广告主账号（同一用户表，带 `advertiser` 档案）。门户权限 |
| 后台 | Author | **只有 bot**。创建草稿、提交机审；不能发布、不能改事实清单、不能看用户 |
| 后台 | FactChecker | 事实清单台、快讯签字；不能发布 |
| 后台 | Editor | 编辑稿件、图谱、源、实体、资产、勘误；不能发布、不能碰广告与用户 |
| 后台 | Publisher | Editor + 发布 / 下线 / 作废 / 排期 / 期刊发送 |
| 后台 | AdOps | 广告位、广告主、活动、排期、素材审核、house ads、专区审核、报表；不能碰内容与用户权益 |
| 后台 | Ops | 用户查询与封禁、订阅与邮件、SEO、系统任务、站点设置；不能发布内容、不能审广告、不能生成码 |
| 后台 | Finance | 码生成与作废、对账、收据、成本看板；只读用户与广告订单 |
| 后台 | Admin | 以上全部 + 功能开关 + 权限分配；不能改自己的角色 |
| 后台 | Super | Admin + Django 原始 admin + 密钥轮换记录 + 删除审计以外的一切 |
| 机器 | CI Token | `POST /api/v1/import`、`/generation-logs`；只能写草稿 / 导入已合并内容 |
| 机器 | Worker | 进程内身份；只能写草稿、日志、统计、邮件任务；发布动作对 worker 拒绝 |

规则：**财务与内容权限永不绑同一日常账号；AdOps 与 Editor 一人兼任也分开登录**（`04` §7.1）；后台账号强制二步验证（TOTP）；Author 只能是 bot 服务账号。

### 1.2 能力矩阵（√ 可 · ○ 只读 · — 不可）

| 能力 | Guest | Free | Supporter | Advertiser | Author | FactChecker | Editor | Publisher | AdOps | Ops | Finance | Admin |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 读免费内容 / 搜索 / 测评 / 快讯 | √ | √ | √ | √ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ |
| 进度 / 收藏 / 划线 / 读完标记 | 本地 | √ | √ | √ | — | — | — | — | — | — | — | — |
| 收费内容全文（paywall 开） | 预览 | 预览 / 内容码 | √ | 预览 | — | ○ | ○ | ○ | — | — | — | ○ |
| 资源包下载 | 示例 | 示例 | √ | 示例 | — | — | ○ | ○ | — | — | — | ○ |
| 站内问答（ask 开） | — | 3 / 日 | 20 / 日 | 3 / 日 | — | — | — | — | — | — | — | — |
| 兑会员码 / 内容码 | 需登录 | √ | √ | √ | — | — | — | — | — | — | — | — |
| 广告主门户 | — | 开通后 | 开通后 | √ | — | — | — | — | ○ | ○ | ○ | ○ |
| 创建草稿 / 提交机审 | — | — | — | — | √ | — | √ | √ | — | — | — | √ |
| 事实清单处理 / 快讯签字 | — | — | — | — | — | √ | √ | √ | — | — | — | √ |
| 编辑稿件 / 图谱 / 源 / 实体 / 资产 | — | — | — | — | — | ○ | √ | √ | — | — | — | √ |
| 发布 / 下线 / 作废 / 排期 / 发期刊 | — | — | — | — | — | — | — | √ | — | — | — | √ |
| 广告位 / 活动 / 排期 / 素材审核 / house | — | — | — | — | — | — | — | — | √ | ○ | ○ | √ |
| 专区条目审核 / 认领核对 | — | — | — | — | — | — | ○ | ○ | √ | — | — | √ |
| 用户查询 / 封禁 / 手动权益 | — | — | — | — | — | — | — | — | — | √ | ○ | √ |
| 码生成 / 作废 / 对账 / 收据 | — | — | — | — | — | — | — | — | ○ | ○ | √ | √ |
| 邮件模板 / 广播 / 抑制名单 | — | — | — | — | — | — | — | ○ | — | √ | — | √ |
| 功能开关 / 分级开启 | — | — | — | — | — | — | — | — | ○ | ○ | ○ | √ |
| SEO 重定向 / 站点设置 / 任务 | — | — | — | — | — | — | — | — | — | √ | — | √ |
| 审计日志 | — | — | — | — | — | — | — | — | ○ | ○ | ○ | √ |
| 提示词 / 模板 / skill 版本 | — | — | — | — | ○ | ○ | √ | √ | — | — | — | √ |
| 模型成本看板 | — | — | — | — | — | — | ○ | ○ | — | ○ | √ | √ |

### 1.3 权益判定（`access` 服务的规则，唯一真源）

```text
entitlements(user)   → 集合 {ad_free, ask_quota:N, assets_all, member_rss, paid_content, group:<id>...}
                       来源：memberships(有效期内) ∪ group_rules ∪ 手动权益(有到期)；缓存 60s，兑码 / 到期 / 封禁 时主动失效
visible(user, node)  → node.status = published 且 (node.access ≠ group 或 group ∈ entitlements)；关闭态类型（quiz / lab / 专区）随 flags
can_read_full(u, n)  → flags.paywall 关 → 是
                       n.access = free → 是
                       supporter → paid_content ∈ entitlements(u)
                       code      → content_unlocks(u, n) 存在 或 paid_content ∈ entitlements(u)
                       group     → 对应 group ∈ entitlements(u)
                       否则 → 否（返回预览：<!-- more --> 之前，缺省前 30% 字符，按段落边界截）
quota(user, 'ask')   → 访客 0 · Free 3 · Supporter 20 · 组按组；按上海时区自然日；原子扣减；扣减记 tokens 与成本
sees_ads(user, slot) → flags.ads 关 → 否
                       slot ∈ {S3..S6} 且 ad_free ∈ entitlements(user) → 否
                       否则 → 是
can(actor, action, obj) → 角色矩阵（1.2）∧ 对象状态允许（第 6 节）∧ 不是自己审自己（bot 的稿由人审；AdOps 不能审自己创建的 house 以外活动）
```

缓存与失效：权益、开关、导航、页面片段都可缓存；**收费态正文与登录态个人数据不进 CDN / 页面缓存**（`Cache-Control: private`）；缓存键含 `flags 版本号 + 登录态类别（匿名 / 登录 / 支持者）`，开关翻转即全站失效。

---

## 2. 对外站功能规格

每个功能按 **目的 · 入口 · 输入 · 规则 · 状态 · 权限 · 输出 · 错误 · 埋点 · 验收** 写；交互与版式细节在 `05` §5 对应小节，不重复。

### 2.1 全局框架

- 顶栏 ≤ 7 项：学习 · 情报 · 工具 · 百科 · 招聘（`ads.self_serve.jobs` 开时）· 搜索 · 登录 / 头像；关闭态项不渲染（G2）。
- 页脚：关于、披露、广告政策、许可、隐私、勘误、更新日志、作者、RSS、支持者、媒体页（`ads.enabled` 关时媒体页不出现）。
- 全站通知条（Admin 配置，≤ 1 条，≤ 80 字，可关闭记 localStorage，7 天后再出现）。
- 主题深 / 浅随系统 + 手动切换；字号三档；均存 localStorage。
- 搜索框：回车进 `/search?q=`；输入 ≥ 2 字才提交；不做联想（第一版）。
- 维护模式：Ops 开启 → 公开站 503 + 说明 + Retry-After；`/studio` `/admin` 正常。
- 验收：无 JS 时全部公开页可读可导航（HTMX 增强不阻塞）；Lighthouse 无障碍 ≥ 95。

### 2.2 首页 `/`

- 目的：三步之内让新读者进测评或进一篇文章；老读者一键继续。
- 内容块与数据源：主 CTA（测评）· 今日简报 5 条（当日早报 items，无则最近一期）· 路径缩略（published paths）· 最新概念卡 6（kind=concept，published_at 倒序）· 工具周榜（`tool_listings` 7 日点击 + 实测徽章，专区关闭态也显示但只作导流）· 招聘精选 3（`ads.self_serve.jobs` 开时）· R1 推荐位（关闭态编辑填充）· 登录态「从这里继续」（progress 最近一条）。
- 规则：没有聊天框；每块都有空态文案由编辑配置（不出现「暂无数据」）；块顺序 Admin 可排（≤ 8 块）。
- 缓存：匿名 5 分钟；登录态个人块局部 HTMX 加载，不缓存。
- 埋点：`home_cta_assess`、`home_brief_click`、`home_continue`、`r1_click(kind)`。
- 验收：`05` §5.1；移动端首屏无广告位（`05` 原则）。

### 2.3 选路测评 `/assess`

- 输入：目标（单选 6 项）、当前工具（多选）、每周时间（3 档）、岗位（单选 8 项）；4 题，可跳过任一题。
- 规则：映射表在 Studio 可改（`assess_rules`，带版本）；结果 = 起点层 + 路径 + 单元 + 「先不要学什么」3 条；只有 doc-qa 时其他目标给「覆盖你目标的 N 个单元 + 先读概念卡」，不假装有别的路径；匿名结果存 localStorage，登录后合并写 `assessments`。
- 限制：同一 IP 哈希 60 次 / 小时（防刷）；结果页可分享（OG 图带层徽章，不带个人信息）。
- 状态：无账号 / 有账号 / 重测（覆盖，保留历史 5 次）。
- 埋点：`assess_start`、`assess_step(n)`、`assess_done(level, track)`、`assess_share`。
- 验收：完成率 ≥ 60%（达标线）；2 分钟内可完成。

### 2.4 学习地图 `/learn`、路径 `/learn/[track]`、单元 `/learn/[track]/[unit]`、读完标记

- 地图：8 层 × 领域 DAG；节点状态 = 已发布 / 计划中（灰，不可点，显示预计月份）/ 已读 / 已读完；筛选：层、岗位；**不做硬锁**，只标「建议先读」（prereqs 未读完时显示）。
- 路径页：大纲 + 每单元学习目标（可观察动词）+ 预计时长 + 前置；进度条（登录）。
- 单元页：正文（unit 类型的 content_node）+ 动手步骤在正文内 + 「读完，下一课」+ 上一课 / 下一课 + R2。
- 读完标记规则：POST；登录写 `progress(status=done, done_at)`；匿名存本地并在登录时合并（本地 → 服务端，服务端已有以服务端为准）；可撤销；一天内重复点幂等；不自动按滚动判定。
- DAG 约束（Studio 保存时校验）：无环；每节点 ≤ 6 前置；每路径 5–15 单元；单元 `unit_index` 连续；发布的路径其单元至少 3 篇已发布，否则路径页显示「建设中」而非空。
- 埋点：`map_view`、`map_filter`、`node_click`、`unit_open`、`unit_read_90`、`unit_done`、`unit_next`。
- 验收：路径第 3 单元到达率 ≥ 20%；「读完」标记率 ≥ 40%（到达者）。

### 2.5 阅读器 `/articles/[slug]`（概念卡 / 单元 / 深度 / 案例 / 对照 / 常见坑 / 项目 共用）

- 模块顺序与状态见 `05` §5.5、`04` §6.2。这里定规则：
- 渲染：Markdown → HTML 在**导入时**渲染并缓存到 `content_nodes.html`（含目录树、术语链接、callout、代码块实测标记）；请求时只拼装个性化块（进度、收藏、推荐位、广告位、收费态）。
- 术语链接：正文内术语首次出现自动链 `/glossary/[term]`（导入时按术语表匹配，最多 30 个 / 篇，人可在 front-matter 排除）。
- 代码块：必须带语言标记；实测徽章来自 `verified` 字段 + 验证记录；无记录显示「未运行」，不能显示为通过。
- 来源卡：`sources[]` ≥ 1（概念 / 单元）、≥ 2 且含官方（快讯 / 实体 / 深度）；每条带 tier；链接 rel="nofollow noopener" 除官方 tier。
- 状态：正常 / 可能过时（now > review_by）/ 已作废（archived + 替代链接）/ 有勘误 / 自上次阅读后有更新 / **收费态**（1.3 `can_read_full` 为否）。
- 收费态：服务端截断；预览之后的 HTML 不进响应；目录后半灰显；解锁卡（会员 / 内容码 → `/redeem?next=` / 发卡站链接）；`Cache-Control: private`；JSON-LD `isAccessibleForFree:false` + `hasPart{cssSelector:".paywalled"}`；列表卡角标「会员」。
- 分享：OG 图 `/og/<public_id>.png`（Pillow 生成，缓存对象存储，内容更新时失效）。
- 埋点：`05` §5.5 + `unlock_card_click(kind)`。
- 验收：`05` §5.5；收费态用抓包确认截断后的正文不在 HTML / JSON；所有强制模块存在（模板单测）。

### 2.6 反馈 · 报错 · 划线 · 收藏 · 复制引用 · 赞赏

| 功能 | 输入 | 规则与限制 | 权限 | 数据 |
|---|---|---|---|---|
| 三键反馈 | kind ∈ {helpful, confusing, outdated} + 可选锚点（段落 id） | 匿名可点（IP 哈希 + 篇 去重 24h）；登录去重按用户；每人每日 ≤ 30；`outdated` 达 3 人 / 7 日 → 自动进保鲜队列 | 所有人 | `feedback` |
| 报告错误 | 锚点 + 文本 ≤ 500 字 + 可选邮箱 | 过红线；每人每日 ≤ 10；进勘误处理队列（4.14）；提交者选择是否署名 | 所有人 | `error_reports` |
| 划线 | 选区（段落 id + 偏移）+ 可选笔记 ≤ 200 字 | 登录；每篇 ≤ 100 条；导出 Markdown | Free+ | `highlights` |
| 收藏 | 篇 / 快讯 / 实体 | 登录；≤ 2000 条；收藏对象更新或过时 → 学习台提示 | Free+ | `bookmarks` |
| 复制引用 | — | 客户端拼「标题 · ai.nornless.com · URL · Last-verified」 | 所有人 | 埋点 |
| 赞赏 | — | `tipping.enabled` 开时文末显示赞赏码图片；不记账 | 所有人 | — |

### 2.7 百科：概念卡 / 术语 `/glossary` / 实体 `/models /companies /papers` / 对照 `/compare` / 项目课 `/projects`

- 术语：每条 = 术语（中 / 英）+ 一句定义（≤ 60 字）+ 展开（≤ 300 字）+ 相关概念卡 + 首次出现的快讯；按拼音首字母索引；悬停卡数据接口 `/glossary/[term]?partial=1`（HTMX）。
- 实体页：字段 = 名称、类型、官方链接（必填）、一句话、关键事实表（价格 / 上下文 / 许可 / 国内可用性，带「截至」）、时间线（关联快讯自动）、相关对照、工具目录条目（若有）；**快讯发布时自动创建或更新实体页草稿**，人审后发布。
- 对照页：两实体 / 两方案；固定表结构（维度 ≤ 12 行）+ 结论段（人写）+ 「什么时候选 A / B」；数据 CSV 可下载（`asset.access` 配置）。
- 项目课：`project` 类型；含仓库链接（对象存储 zip 或 Git）、成功标准、验收清单；仓库下载走资源包权限。
- 验收：术语悬停不遮正文；实体页官方链接 100% 有；对照页结论段非 AI 生成（front-matter `ai.assist_ratio` 对结论段标注人写）。

### 2.8 工具目录 `/tools`（黄页读者侧 + 认领核对）

- 列表：分类、标签、国内可直连、价格档、更新日志、实测徽章（编辑给）；排序默认「实测徽章 → 更新时间」；**认证 / 置顶只在 `ads.self_serve.tools` 开时影响排序，且带角标**。
- 认领核对（关闭态也保留）：厂商填官方邮箱（域名须与官方链接同域）+ 联系人 + 要修正的字段 → 发验证邮件 → 点击后进 AdOps 队列 → 通过则条目标「官方核对 · 日期」，不改实测徽章。
- 限制：每条目 30 天内只能有一个待处理认领；认领邮箱域名与官网不同 → 拒。
- 埋点：`tools_filter`、`tool_click`、`claim_start`、`claim_verified`。

### 2.9 情报：快讯 `/news`、早报 `/digest/daily/[date]`、周报 `/digest/weekly/[slug]`、深度 `/digest/deep/[slug]`、过时清单 `/digest/outdated/[month]`、专题 `/topics/[cluster]`、时间线 `/timeline`

- 快讯条目：标题 ≤ 40 字、正文 200–400 字、3 点结论、来源 ≥ 2（含官方）、挂接节点 ≥ 1（层 / 概念 / 实体）、发布时间、可能影响的知识文列表（自动）。
- 快讯流：按时间；筛选层 / 领域 / 实体；每 10 条一处 R4（关闭态编辑卡）。
- 早报：工作日 08:00 发布；今日一句话 + 8–12 条 + 行动项（登录可勾，`digest_actions`）+ 明天看什么 + 订阅入口；S1 段关闭态省略；**发布后 24 小时内可勘误（追加「更正」段，不改原文）**。
- 周报：三栏（发生了什么 / 意味着什么 / 你该做什么）+ 本周岗位 3 条（`ads.self_serve.jobs` 开时）+ S2 位（`ads.email_sponsor`）。
- 过时清单：每月 1 日生成候选（4.13），编辑确认后发布；每条 = 什么过时了、为什么、替代、涉及文章；登录读者若收藏了涉及文章 → 学习台提醒。
- 专题页：支柱页，编辑维护的卫星列表（概念卡 / 对照 / 实体 / 快讯）；S11 位。
- 时间线：实体大事按月；数据来自快讯 `is_milestone` 标记。
- 验收：早报连续 30 个工作日；快讯双源率 100%（发布门禁）；`05` §5.7。

### 2.10 搜索 `/search`

- 输入：q（2–100 字）、分栏（概念 / 单元 / 快讯 / 工具 / 实体 / 资产 / 全部）、层筛选。
- 规则：全文检索 `zhparser`（退化 `pg_trgm`）；排序 = 相关度 × 未过时加权 × 类型权重（概念卡 > 单元 > 快讯 > 实体 > 工具）；专区条目与赞助内容**不进**搜索；收费内容进搜索但显示「会员」角标；`search.semantic` 开后混排向量结果（只索引已发布已审语料）。
- 无结果：显示「本站还没写过」+ 相近术语 + 记 `search_logs(q, zero=true)` 进选题缺口。
- 限制：60 次 / 分钟 / IP 哈希；q 过红线（不返回但记录）。
- 埋点：`search`、`search_zero`、`search_click(rank, type)`。
- 验收：无结果率 ≤ 15%（达标线）；p75 响应 ≤ 300ms。

### 2.11 订阅中心 `/subscribe`

- 邮箱订阅：邮箱 → 双重确认（确认链接 24h 有效，单次）→ 偏好（早报 默认不勾 / 周报 默认勾 / 过时清单 / 收藏更新 / 路径催学）→ 管理链接（签名 token，不需登录）。
- RSS：全站 / 快讯 / 早报 / 周报 / 某一层 / 会员 RSS（带用户 token，`member_rss` 权益，泄露可在账户重置）。
- 退订：邮件内一键（`List-Unsubscribe` + POST）；退订即时；`subscribers.status=unsubscribed`，30 天后匿名化邮箱哈希保留防重复发送。
- 限制：同一邮箱 24h 内 ≤ 3 次确认邮件；一次性域名邮箱拒；退信 2 次进抑制名单。
- 验收：确认率 ≥ 50%；退订一键成功率 100%。

### 2.12 账户：注册 / 登录 / 魔法链接 / 密码 / 会话 / 设置 / 导出 / 删除

| 功能 | 规则 |
|---|---|
| 注册 | 邮箱（小写归一，RFC 5322，一次性域名拒）+ 密码（≥ 10 位，zxcvbn ≥ 3，不在泄露库）或**魔法链接**（15 分钟、单次、绑定发起时的 UA 哈希）；注册即登录；显示名 ≤ 20 字过红线，默认「读者 + 4 位」 |
| 登录 | 邮箱 + 密码 或 魔法链接；失败 5 次 / 15 分钟 锁 15 分钟（按账号 + IP 哈希）；成功后重置 |
| 会话 | HttpOnly Secure SameSite=Lax；30 天滑动；最多 5 个活动会话，超出踢最早；「登出全部」 |
| 微信登录 | `wechat_login` 开关，默认关；开时只做绑定不做注册 |
| 后台账号 | 强制 TOTP；密码 ≥ 14 位；会话 12 小时；IP 变化重新验证 |
| 账户设置 | 显示名、邮箱换绑（新旧双确认）、密码、订阅偏好、会话列表、会员 RSS token 重置、数据导出、删除账户 |
| 数据导出 | 一键生成 zip（进度、收藏、划线、反馈、问答记录、测评）；任务异步 ≤ 10 分钟；链接 24h |
| 删除账户 | 二次确认 + 7 天冷静期（期间可撤销）→ 匿名化（邮箱哈希、显示名清空、划线 / 收藏删除、反馈保留但去关联、会员码兑换记录保留 target 为「已删除用户」）；不可恢复 |

### 2.13 读者区 `/app`

- `/app` 学习台：从这里继续（最近 progress）· 今日 3 任务（下一课 / 一张前置概念卡 / 一条关联快讯；规则：未读优先、不重复、不多于 3、可换一批 ≤ 3 次 / 日）· 我的路径（进度 = done / 总数）· 收藏更新与过时提醒（≤ 5 条）· 问答余额（`ask` 开）· 简报存档入口。
- `/app/library`：收藏 + 划线，按篇聚合，导出 Markdown（≤ 1 次 / 分钟）。
- `/app/downloads`：资源包（按权益）；下载链接签名 10 分钟；每人每日 ≤ 50 次。
- `/app/briefing`：早报 / 周报存档（订阅者）；行动项完成率。
- `/app/ask`：见 2.15。
- `/app/account`：见 2.12。
- 规则：不做掌握度、雷达图、排名、连续打卡奖励；所有个人数据 `private` 不缓存。

### 2.14 支持者 `/pricing` 与兑码 `/redeem`

- `/pricing`：`supporter.enabled` 关 → 404；开 → 权益列表（随 `ads` / `paywall` 开关自动增减条目）· 价格（读取站点设置里的展示价，与发卡站商品一致由人保证）· 「去发卡站买」（新窗口或内嵌 iframe，店址在站点设置）· 「我有码」→ `/redeem`。
- `/redeem`：登录后输入码 → 服务端校验：格式（`NRL-XXXX-XXXX-XXXX`，Crockford base32，无 0/O/1/I）→ 存在 → 状态 issued → 未过兑换期 → 类型允许（会员码 / 内容码；广告码提示去 `/ads`）→ 事务内：标记 redeemed(user, at)、写 membership 或 content_unlock、失效权益缓存、写 audit → 成功页显示到期日 / 已解锁内容并跳回 `next`。
- 限制：每用户 10 次 / 小时；连续失败 5 次锁 1 小时；同一码并发兑换靠行锁只成功一次；已兑不退（`/pricing` 写明）。
- 错误文案区分：码不存在 / 已被兑 / 已过兑换期 / 类型不对 / 请先登录。
- 埋点：`pricing_view`、`pricing_shop_click`、`redeem_submit(result)`。
- 验收：兑码到权益生效 ≤ 1s；错误文案与状态一一对应（单测）。

### 2.15 站内问答 `/app/ask`（V1，`ask.enabled`）

- 输入：问题 ≤ 500 字；可选「只问这篇」。
- 规则：只检索已发布已审语料（向量 + 全文）；答案必须带 ≥ 1 段落级引用，无引用则答「本站还没写过，已记入选题缺口」并写 `topic_gaps`；额度按 1.3 原子扣减；每问 tokens 上限（配置，默认 4k 上下文 + 1k 输出）；单用户并发 1；流式输出可选。
- 拒答：红线命中、与 AI 学习无关（分类器置信 ≥ 0.8）、要求生成整篇文章。
- 数据：`ask_threads(user, question, answer, citations[], tokens, cost, model, prompt_version)`；用户可删自己的记录。
- 验收：引用点击可跳到段落；无引用答案率 = 0；成本 / 问 有数。

### 2.16 广告专区读者侧（全部建设；开关分别控制可见）

| 专区 | 开关 | 读者可做 | 条目字段（读者可见） | 规则 |
|---|---|---|---|---|
| 招聘板 `/jobs` | `ads.self_serve.jobs` | 浏览、筛选（远程 / 城市 / 方向）、订阅岗位邮件 | 岗位、公司、薪资范围、远程、城市、方向、链接、发布日、置顶角标 | 上线 30 天自动过期；置顶 ≤ 5 条同屏；外链 `/go` 计数；过期条目 410 |
| 发布墙 `/launches` | `ads.launches` | 浏览、按周看榜 | 产品、一句话、链接、发布日、featured 角标、编辑评分 | 周榜 = 编辑评分 + 7 日点击；featured 只标注不改排序 |
| 活动 `/events` | `ads.events` | 浏览、按时间筛选、加日历（ics） | 名称、主办、形式、时间、价格、报名链接、置顶角标 | 过期自动归档；置顶 ≤ 2 |
| 优惠 `/deals` | `ads.deals` | 浏览、复制优惠码、跳转 | 实体、优惠、码、有效期、披露文案 | 全部免费展示；联盟链接文末披露；过期下线 |
| 赞助内容 `/sponsored/[slug]` | `ads.sponsored_content` | 阅读 | 正文 + 固定「推广」角标 + 广告主 + 发布日 | 不进阶梯 / 搜索 / 日报正文 / 主 RSS；独立 RSS；默认 index（Admin 可 noindex） |
| 媒体页 `/advertise` | `ads.enabled` | 看受众数据、产品价目、规则、询盘、自助入口 | `04` 附录 F | 数据每月 1 日自动更新（Umami 聚合 + 订阅数）；询盘表单过红线、每 IP 3 次 / 日 |
| 黄页付费层（认证 / 置顶 / 详情增强） | `ads.self_serve.tools` | 见 2.8 | 认证角标、置顶角标、增强详情 | 关时目录只显示实体信息与实测徽章 |
| 早报 / 周报赞助段 S1 / S2 | `ads.email_sponsor` | 阅读 | 一段赞助文案 + 「赞助」标识 | 关时站内与邮件模板都省略该块 |

### 2.17 推荐位与广告位（读者视角的渲染约束）

- 位置表 `ad_slots`：S1–S12 / R1–R5 与页面类型绑定；每页 ≤ 2 个广告位；正文中间没有位。
- 关闭态：R1–R5 渲染编辑推荐（相关文 / 概念卡 / 工具实测 / 订阅 / 过时清单），由 `recommendations` 服务算，固定尺寸预留（CLS）。
- 开启态：`ads_for(page, user)`（`04` §9.5）；会话级去重与频次（同一会话同位置不连续 3 次同一广告主）；无有效排期 → house ads；素材服务端渲染为原生卡；角标由模板注入（G17）。
- 计数：曝光在渲染时记（去爬虫 UA、去后台账号）；点击走 `/go/<public_id>`（302，带 UTM，记录 referer 页面与会话哈希；每会话同素材 1 次 / 分钟计一次）。
- 支持者：S3–S6 不渲染（不是隐藏）。
- 验收：拦截器开启时页面无空洞；无第三方请求；角标 100% 存在（模板单测）。

### 2.18 公共页

`/about`（编辑方针、团队、联系）· `/disclosure`（AI 使用披露全文、模型、人审流程）· `/ads-policy`（广告规则 + 变更记录）· `/license`（内容许可与抓取政策，`04` §11）· `/privacy`（数据清单与保留期，见 7.4）· `/errata`（勘误列表，按日期）· `/changelog`（站点与内容更新日志，自动 + 手写）· `/authors/[id]`（人与 bot 角色页：bot 页写清模型与审核人）。全部由 Studio 内「静态页」类型维护，带版本与生效日期。

### 2.19 机器接口

| 接口 | 规则 |
|---|---|
| `/rss.xml`、`/rss/[section].xml` | 最近 50 条；全文输出免费内容、摘要输出收费内容；专区与赞助不进主源；会员 RSS `/rss/member/<token>.xml` 含资源更新，token 可重置 |
| `/sitemap.xml` + 分节 sitemap | 只含已发布、可见、`index` 的 URL；关闭态与收费预览不排除但标 `lastmod`；每文件 ≤ 50k 条 |
| `/robots.txt` | 由许可策略配置生成（允许搜索 / 问答引擎、拒训练爬虫名单，季度复核）；`/studio` `/admin` `/app` `/ads` `/api` `/redeem` `/go` Disallow |
| `/llms.txt` | 与 robots 同源配置生成：站点说明、允许用途、署名要求、重点页面清单 |
| `/og/<public_id>.png` | Pillow 渲染，1200×630，缓存对象存储；对象更新时失效；不含个人信息 |
| JSON-LD | `Article` / `NewsArticle` / `TechArticle` / `BreadcrumbList` / `FAQPage` / `Organization`；收费预览 `isAccessibleForFree:false` |
| `/go/<public_id>` | 302；记录；对未知 id 404；对已结束活动跳广告主官网仍计「过期点击」 |
| `/api/v1/*` | Django Ninja；Bearer token（CI / Ops）；见 8.6 |
| `/u/` | Umami 反代；脚本同域；后台账号不计 |
| 退信 webhook | 供应商签名校验；只改 `subscribers.status` 与抑制名单；限流 100 / 分钟 |

---

## 3. 广告主门户 `/ads`

- 前提：`ads.enabled` 总开关开，且 `ads.direct` / `ads.self_serve.*` / `ads.launches` / `ads.events` / `ads.sponsored_content` 任一开时门户可见；否则 404（`ads.preview_roles` 内的角色始终可进，供验收）。
- 3.1 开通：登录读者账号 → 「成为广告主」→ 填主体信息（名称 ≤ 60、类型 公司 / 个人、官网 https、联系人、联系邮箱、结算方式 码 / 对公 / Stripe）→ 邮箱域名与官网同域则自动通过，否则 AdOps 审 ≤ 24h。
- 3.2 兑广告码：输入码 → 校验同 2.14（类型 = ad_product）→ 生成对应产品的**待填活动**（认证 30 天 / 置顶 7 天 / 招聘 30 天 / featured / 活动置顶 / 赞助文 1 篇 / 日报赞助 N 期 / 原生卡 N 天…，SKU 表在 Admin）。
- 3.3 活动与素材：固定字段表单——标题 ≤ 24 字、文案 ≤ 60 字、按钮 ≤ 6 字、一张图（16:9 ≤ 200KB）或 logo（1:1）、落地 https 链接（域名须与主体官网同域或在白名单）、投放上下文（层 / 领域 / 标签，可选）、期望起始日；**不能填**角标文字、不能传脚本 / iframe / 追踪像素；素材过红线与绝对化用语拦截（即时提示）。
- 3.4 审核：提交 → `pending_review` → AdOps 按合规清单逐项勾 → 通过 / 需修改（写原因，广告主可改 3 次）/ 拒绝（码退回 issued 状态可再用，或按政策作废）；SLA ≤ 24h 工作日；审核意见对广告主可见。
- 3.5 排期：通过后按 SKU 时长自动排期到可用位；位满则排下一可用日并告知；直销活动由 AdOps 手排。
- 3.6 报表：曝光、点击、CTR 按天；只出聚合数；不出读者任何信息；周报表邮件（可关）。
- 3.7 收据与账单：`/ads/billing` 列兑码记录、直销订单、收据 PDF（自动，写「暂不开发票」）；直销付款状态 AdOps / Finance 手改。
- 3.8 续费与到期：到期前 7 天邮件 + 门户提示；续 = 再兑一张同 SKU 码，天数累加；到期后素材下线、条目角标消失。
- 3.9 通知：审核结果、上线、到期、周报表 → 邮件 + 门户消息中心；每天 ≤ 3 封。
- 3.10 约束：一个广告主同时 ≤ 10 个活跃活动；单一广告主占总曝光 ≤ 30%（排期时预警，超出拒排）；评测涉及厂商在该评测页不投 S4 / S5（排期引擎按实体排除）。

---

## 4. Studio 编辑部 `/studio`

后台账号 TOTP 必开；所有写操作审计（G5）。

### 4.1 工作台 `/studio`
今日待办（按 SLA 倒计时排序：快讯 2h、早报 08:00、概念卡 48h、单元 1 周）· 待我处理（按角色）· 保鲜队列摘要 · 缺口 Top 10 · 昨日成本 · 失败任务 · 最近发布。

### 4.2 选题池与缺口 `/studio/topics`
- 五信号（`04` §4.5）：搜索无结果、快讯挂接不到节点、问答无引用、读者反馈「没看懂」聚集、图谱空节点；每条候选 = 信号来源 + 建议层 / 领域 + 建议类型 + 分数。
- 操作：采纳 → 生成 brief（4.3）；合并；忽略（写原因，30 天内不再出现）。
- 配额（`04` §4.6）在采纳时校验：超配额提示并需 Publisher 确认。

### 4.3 Brief `/studio/briefs`
- 必填：读者画像、层与领域、前置节点、完成后解锁节点、学习目标 1–3 条（可观察动词词表校验）、必引源 ≥ 1、禁止源、必须零件、横切模块、广告上下文标签、输出 schema 版本。
- 单元类 brief **人必须先写学习目标与练习**，否则不能进生成。
- 状态：draft → ready → generating → done；ready 才能被生成台选中。

### 4.4 生成台 `/studio/generate`
- 选 brief + 角色链（选题员 / 研究员 / 撰稿员 / 核查员 / 验证员 / 排版员 / 保鲜员 / 简报员）+ 提示词版本（默认当前）+ 模型（按角色默认）→ 提交为 Procrastinate 任务。
- 约束：**每日成本上限**（站点设置，默认 ¥100 / 日，达 80% 预警，100% 停止非快讯类生成）；单任务 tokens 上限；并发 ≤ 3；研究员不带写 / 执行工具；撰稿员只读研究员事实清单；核查员新会话不共享上下文；输出必须是 CMS JSON（Pydantic 校验），不合法 → 修复提示重试 ≤ 2 次 → 仍失败标 failed。
- 验证员沙箱：一次性容器，CPU 1、内存 1GB、10 分钟、网络仅包镜像白名单、无挂载；跑通回填 `verified: sandbox` + 环境 + 日期；跑不通标「未运行」并附日志摘要。
- 每次调用写 `generation_jobs(prompt_hash, model, tokens_in/out, cost, latency, retrieved_doc_ids, status)`；任务只写草稿，永不发布。
- 快讯类走独立通道：不受成本停机影响（有独立上限 ¥30 / 日）。

### 4.5 稿件与编辑器 `/studio/editor/[id]`
- 左 Markdown（受控编辑器）右预览（与线上同模板渲染）；front-matter 表单化编辑并实时校验（附录 A）；术语链接 / 内链建议（排版员产出，人勾选）；callout 插入；代码块语言必填。
- 版本：每次保存一版（≤ 200 版 / 篇，超出合并旧版）；diff 视图；回滚需 Editor+。
- 状态机按 `04` §8.2；转移按钮只在允许的状态与角色出现（第 6 节）；回退必填原因。
- 锁：同一稿件同时只一人编辑（软锁 10 分钟，心跳续）。

### 4.6 机审十门报告 `/studio/qa/[id]`
- 门：结构、事实、代码、术语、重复、红线、可读、标识、版权、内链（`04` §8.6）。每门 = 通过 / 失败 + 证据行；任一失败不能进 `factcheck`；人可对「可读」「内链」两门标「人工放行」（写原因），其余不可放行。
- 重复门：与已发布语料向量相似度 ≥ 0.92 视为重复；提示候选合并。
- 版权门：来源片段引用 ≤ 60 字 / 处且带链接；图片有来源或自绘标记。

### 4.7 事实清单台 `/studio/facts/[id]`
- 每条 claim：原文句、来源、状态 open / passed / doubtful / removed、处理人、时间；**100% 处理**才能进 `editing`；doubtful 必须改稿或删句；新闻类须 FactChecker 签字（字段 `signed_by`）。
- 批量操作：同源多条一起通过；导出清单随 PR。

### 4.8 审稿列表 `/studio/review`（快讯 / 早报优先）
- 列表视图：每条 = 标题、200–400 字、3 点、来源（点开原文）、候选节点、机审结果、SLA 倒计时；操作：通过 / 改（行内）/ 退回 / 合并到另一条 / 拒；键盘 J/K/Enter。
- 批量通过 ≤ 20 条 / 次；通过即进 `scheduled`（快讯立即发布，早报进当日期刊）。
- 手机可用：单列、按钮 ≥ 44px。
- 规则：双源不满足的条目不显示「通过」按钮，只显示「补源」。

### 4.9 期刊编排 `/studio/issues`
- 早报：自动汇编当日已发布快讯 → 排序拖拽 → 今日一句话（≤ 60 字）→ 行动项 ≤ 3 → 明天看什么 → S1 段（`ads.direct` 开且有排期时自动填）→ 预览（站 / 邮件）→ 发布（Publisher）；08:00 定时，未审则 08:00 发「延迟通知」不发空刊。
- 周报：三栏草稿（简报员）→ 主编改判断段（必改，字段 `judgement_edited_by`）→ 本周岗位 3 条 → S2 → 发。
- 深度：人选题 → 材料包 → 起草 → 对抗式核验 → 判断段人重写（校验：判断段 `ai.assist_ratio` ≤ 0.3）。
- 过时清单：见 4.13。
- 发送：邮件版走广播任务（7.2 限速）；站内版立即；RSS 更新；分享卡生成。
- 更正：发布后 24h 内可追加「更正」段（不改原文、不重发邮件）；站内页与 RSS 更新，下一期开头提及。

### 4.10 图谱维护 `/studio/graph`
- 八层节点表（`editorial/outline.yml` 同步；Studio 为真源，导出回 yml）：节点 = id、层、领域、标题、状态（空 / 计划 / 草稿 / 已发布）、前置、后继、覆盖内容。
- 校验：无环；每节点 ≤ 6 前置；层不倒挂（前置层 ≤ 本层）；路径单元连续；删除有内容的节点须先迁移。
- 视图：DAG 图（只读渲染）+ 表格编辑；空节点直接生成 brief。

### 4.11 情报源 `/studio/sources`
- 源 = 名称、URL / RSS / API、tier（官方 / 一手 / 二手 / 社媒）、抓取频率（≥ 15 分钟）、语言、启用、连续失败次数、最近抓取。
- 白名单：只有 tier 官方 / 一手可作为「双源」之一；社媒源只作线索不作来源。
- 聚类：embedding 相似度 ≥ 0.85 归簇；簇内评分（源 tier、数量、时效）；评分 ≥ 阈值进简报员。
- 约束：连续失败 5 次自动停用并通知；robots 禁抓的源不抓；只存摘要与链接不存全文（版权）。

### 4.12 实体与工具目录 `/studio/entities`
- 实体 CRUD（官方链接必填、类型、别名、关联）；快讯自动创建的草稿在此审；工具目录条目（实测徽章只能在此授予，记录测试环境与日期；认证 / 置顶字段只读，来自广告系统）。
- 认领核对处理：验证通过的认领请求 → 逐字段对比 → 接受 / 拒绝 → 条目标「官方核对」。

### 4.13 保鲜队列 `/studio/refresh`
- 来源：`review_by` 到期、`expires_at` 到期、快讯触发（实体变更 / 价格 / 改版 / 政策）、反馈「过时了」聚集、依赖实体作废。
- 保鲜员产出 diff 建议 → 人决定：回写（进 editing）/ 降级（加「可能过时」条）/ 作废（archived + 替代节点必填）/ 延期（新 review_by 必填原因）。
- 过时清单候选自动汇总（每月 1 日），编辑确认发布。
- 约束：`published` 且 now > expires_at 的文自动显示「可能过时」条（不需人）；作废后 URL 保留可读 + 替代链接，不 404。

### 4.14 勘误与反馈处理 `/studio/errata`
- 报错队列：new → triaged（是 / 不是错误）→ confirmed → 修文（进 editing）→ 发布修复 → 写 `/errata` 条目（文首红条 + 变更记录）；SLA：事实错误 4 小时内文首挂勘误条（可先挂条后修文）。
- 反馈聚合：每篇三键统计、「没看懂」锚点热力（段落级）→ 作为选题信号。
- 赠月：判断层错误导致读者按错行动 → Finance 发 1 个月会员码给报告者（可选）。

### 4.15 资产 `/studio/assets`
- 资源包 = 名称、版本、文件（zip ≤ 50MB）、`access`（free / supporter / code）、关联内容、变更说明；发布后旧版保留可下载 90 天。
- 对照表 CSV、提示词包、模板、仓库 zip 都是资产。

### 4.16 提示词 / 模板 / skill 版本 `/studio/prompts`
- 每个提示词与模板有语义版本与 `prompt_hash`；改动需 Editor+，生效需 Publisher 指定「当前版本」；旧版本不可删；生成日志引用版本。
- skill 文件（`editorial/skills/<role>.md`）与提示词同步导出，供本机 Grok Build skill 使用；导出带版本号。

### 4.17 Git 编辑部对接与 CI 校验
- PR 约束：改动只在 `content/**`、`assets/**`；每个新增 / 修改的 `.md` 旁必须有 `<slug>.log.json`（generation_log）与 `<slug>.qa.json`（机审报告）；front-matter 通过 schema；红线扫描通过；链接可达（外链 HEAD 200 / 301，官方源除外允许 403）；图片 ≤ 2MB 且有 alt；slug 全站唯一；`ai.reviewed_by` 非空才能合并。
- 合并后 CI 调 `POST /api/v1/import`（携带 commit sha、变更文件列表）→ 幂等导入（`content_hash` 不变跳过）→ 渲染缓存 → 进 `scheduled`（若 front-matter 有 `published_at` ≤ now 则直接 published，**但仅当稿件在 Studio 已过 factcheck**；否则进 `factcheck` 等人）。
- 导入失败 → PR 评论 + Studio 通知；不部分导入。

### 4.18 成本与配额 `/studio/costs`
- 按日 / 按篇 / 按角色 / 按模型的 tokens 与成本；预算条；配额执行情况（`04` §4.6）；导出 CSV。

---

## 5. Admin 运营后台 `/admin`

### 5.1 用户与权益
- 查（邮箱哈希 / 显示名 / public_id）、看权益与来源、会话、订阅、兑码记录、封禁（写原因，登录即失效，公开内容仍可读）、手动权益（类型 + 到期 + 原因，≤ 12 个月）、删除请求处理（冷静期状态）、导出（脱敏 CSV，Finance / Admin）。
- 不显示密码哈希、不显示明文 IP。

### 5.2 码 `/admin/codes`
- 生成批次：类型（会员 / 内容 / 资产 / 广告 SKU）、面值（天数 / 目标对象 / SKU）、数量（≤ 1000 / 批）、兑换有效期（默认 12 个月）、备注、渠道（发卡站 / 手发 / 赠送）→ 生成（CSPRNG，≥ 60 bit 熵）→ 导出 CSV（仅一次可下载明文，之后只显示后 4 位）。
- 作废：单码或整批，写原因；已兑不可作废（只能收回权益，见 5.1）。
- 对账：导入发卡站销售导出（订单号、商品、码后 4 位、时间）→ 匹配批次 → 差异列表（卖出未兑 / 兑了无售出记录 / 重复）。
- 兑换记录：谁、何时、生效了什么；可按批次统计兑换率。
- 权限：Finance / Admin 生成与作废；AdOps 可看广告码批次；Ops 只读。

### 5.3 付费墙与收费内容
- `paywall.enabled` 开关（在 5.8 开关页统一操作）；收费内容清单（所有 `access ≠ free` 的节点、当前是否生效、预览比例、解锁次数）；一键把某类型 / 某路径设为 supporter（写原因，批量 ≤ 200）；预览比例全站默认 30%，单篇可改 10–50%。

### 5.4 分组（V2）
- 组、成员（邮箱批量导入 ≤ 500）、规则（去广告 / 资源 / 进度共享 / 专属路径）、批量会员码绑定组、组管理员。

### 5.5 广告系统
- 广告位：S1–S12 / R1–R5 规格、页面类型、每页上限、支持者隐藏标记；改规格需 Admin。
- 广告主：档案、审核、结算方式、活跃活动、占比预警。
- 活动 / 排期：日历视图；冲突检测（同位同日 > 容量）；直销手排；house ads 池（≥ 5 套素材，轮播）。
- 素材审核：合规清单（标识、绝对化用语、禁投类目、链接同域、图片规格、无脚本）逐项勾；意见模板；通过 / 需修改 / 拒绝。
- 报表：位 / 活动 / 广告主 / 日；拦截率估算（渲染计数 vs Umami 页面数）；导出。
- 对账：直销订单状态；广告码兑换与活动对应；收据补发。
- 政策变更记录：`ads-policy` 每次修改自动生成变更条目公开。

### 5.6 专区条目审核
- 招聘 / 发布墙 / 活动 / 优惠 / 黄页认领 统一队列；字段校验结果、红线、外链检查、重复检测（同链接 30 天内）；通过 / 需修改 / 拒绝；SLA 24h；到期条目自动处理不进队列。

### 5.7 邮件
- 模板（事务：确认 / 魔法链接 / 收据 / 到期 / 审核结果；广播：早报 / 周报 / 过时清单 / 收藏更新 / 路径催学）版本化、测试发送到指定邮箱。
- 广播任务：受众（订阅偏好 + 权益）、预览、定时、限速（供应商额度）、进度、失败重试；发送前红线与链接检查。
- 送达统计：送达 / 打开（若供应商提供）/ 点击（`/go`）/ 退信 / 退订；抑制名单管理（硬退信、投诉自动加入；手动移除需原因）。
- 发件域健康：SPF / DKIM / DMARC 检查结果展示（每日任务）。

### 5.8 功能开关页 `/admin/flags`
- 每个开关：当前值、默认值、说明、**前置条件自动判定**（体验达标线 `05` §11.1 各指标当前值 vs 阈值；合规前置人工勾选项）、最近变更、变更人与原因。
- 操作：翻转需填原因；前置未满足可「强制」但需 Admin 二次确认并记录；翻转后 30s 内全站缓存失效；影响范围提示（哪些路由从 404 变可见）。
- 分级开启向导（`05` §11.3）：当前级、下一级内容、观察期倒计时（14 天）、体验指标对比（前 14 天 vs 后 14 天）；任一指标相对下降 > 10% → **系统自动回退一级**并邮件 Admin，可手动复原需原因。
- 开关键名以 `05` §2.2 为唯一真源：`ads.enabled` `ads.preview_roles` `ads.house` `ads.direct` `ads.self_serve.tools` `ads.self_serve.jobs` `ads.launches` `ads.events` `ads.deals` `ads.sponsored_content` `ads.email_sponsor` `ads.programmatic` `ads.slots.R1..R5` `ads.max_per_page` `supporter.enabled` `ask.enabled` `quiz.enabled` `paywall.enabled` `labs.enabled` `tipping.enabled` `groups.enabled` `wechat_login.enabled` `search.semantic` `email.digest` `outdated.banner`。本文不新增键名。

### 5.9 达标线与运营看板 `/admin/metrics`
- 体验达标线（`05` §11.1）每日计算并存 `metrics_daily`；受众、库存、内容健康、学习健康、商业、系统六层指标（`04` §14.1）；北星卡片；导出。
- 数据源：Umami API（服务端拉取）、DB 聚合；无个人数据。

### 5.10 SEO `/admin/seo`
- 重定向表（slug 改名自动 + 手动；301 / 410；环检测）；死链报告（每周任务）；canonical 冲突；sitemap 状态；robots / llms 策略配置（爬虫名单编辑，生效即重生成）；结构化数据校验结果。

### 5.11 系统与任务 `/admin/system`
- 任务队列：按队列的等待 / 运行 / 失败数；失败任务详情与重试；周期任务表与下次运行；暂停某队列。
- 抓取任务：源状态、失败源。
- 模型成本：日预算条、按模型统计（与 4.18 同源）。
- 备份：最近一次 DB 与对象存储备份时间与校验结果；一键触发。
- 密钥轮换记录（只记时间与名称，不记值）；证书到期。
- 维护模式开关（Ops）。

### 5.12 审计日志 `/admin/audit`
- 按人 / 对象 / 动作 / 时间筛选；before / after diff；导出；只读；保留 36 个月。

### 5.13 站点设置 `/admin/settings`
- 站名、slogan、社媒账号、页脚链接、通知条、发卡站店址与 CSP 白名单、支持者展示价、每日模型预算、快讯预算、默认预览比例、邮件发件域、Umami 站点 id、许可与抓取策略文本、禁投类目词表入口、红线词表入口。
- 每项改动审计；部分项（CSP、店址）改后需 Ops 确认才生效。

### 5.14 Django 原始 admin `/django-admin/`
- 仅 Super；只作数据兜底与紧急修复；所有模型只读为默认，写需显式开启；操作同样进审计。

---

## 6. 状态机总表

| 对象 | 状态 | 允许的转移（谁） | 副作用 |
|---|---|---|---|
| 内容 `content_nodes` | idea → assigned → researching → drafting → machine_qa → factcheck → editing → legal(按需) → scheduled → published → needs_update → archived | 前 4 步 Author(bot) / Editor；machine_qa 系统；factcheck FactChecker+；editing Editor+；scheduled / published / archived Publisher+；needs_update 系统或 Editor+；任何回退 Editor+ 写原因 | published：渲染缓存、sitemap、RSS、分享卡、实体页触发、订阅者「收藏更新」；archived：替代链接必填、保留 URL |
| 快讯 `news` | captured → clustered → drafted → machine_qa → review → published / rejected / merged | 系统到 review；review 由 Editor+（新闻类须 FactChecker 签字字段）；merged 指向主条 | published：挂接节点、实体页草稿、早报候选 |
| 期刊 `issues` | draft → assembled → review → scheduled → published → corrected | Publisher 发布；corrected 追加更正段 | published：邮件广播任务、RSS、站内页 |
| 事实声明 `fact_claims` | open → passed / doubtful / removed | FactChecker+ | 全部非 open 才能进 editing |
| 保鲜 | fresh → due(review_by) → stale(expires_at) → archived | 系统标 due / stale；人决定回写 / 降级 / 作废 / 延期 | stale 自动挂「可能过时」条 |
| 勘误 `error_reports` | new → triaged → confirmed → fixed / dismissed | Editor+ | confirmed：文首红条（≤ 4h）；fixed：`/errata` 条目 + changelog |
| 广告主 `advertisers` | pending → active → suspended | AdOps | suspended：全部活动暂停 |
| 广告活动 `ad_campaigns` | draft → pending_review → approved → scheduled → live → paused → ended / rejected | 广告主到 pending_review；AdOps 审；系统 scheduled / live / ended；paused AdOps 或广告主 | live：投放；ended：到期提醒已发过 |
| 素材 `ad_creatives` | pending → approved / needs_changes / rejected | AdOps | needs_changes ≤ 3 次 |
| 专区条目 `job_posts` 等 | submitted → in_review → published → expired / rejected / withdrawn | 广告主提交；AdOps 审；系统 expired；广告主 withdrawn | published：`/go` 计数开启 |
| 认领 `claims` | requested → email_verified → accepted / rejected | 系统验证邮箱；AdOps 决定 | accepted：条目标官方核对 |
| 码 `codes` | issued → redeemed / voided / expired | 系统兑换；Finance 作废；系统过期 | redeemed：写 membership / unlock / 活动 |
| 会员 `memberships` | active → expiring(7d) → expired | 系统 | expiring：邮件；expired：权益失效 |
| 订阅 `subscribers` | pending → active → unsubscribed / bounced | 用户确认；一键退订；webhook 退信 | bounced ×2 → 抑制名单 |
| 反馈 `feedback` | new → seen → actioned / ignored | Editor+ | outdated ×3 → 保鲜队列 |
| 生成任务 `generation_jobs` | queued → running → succeeded / failed / aborted | 系统；Editor+ 可 abort | failed ×3 → 通知 |
| 开关 `feature_flags` | off ↔ on（含 level 0–7） | Admin；系统自动回退 | 审计；缓存失效 |
| 用户 | active → banned / deletion_pending → deleted(anonymized) | Ops 封禁；用户删除；系统 7 天后匿名化 | 会话失效 |

通用规则：状态字段只能经 `transition(obj, to, actor, reason)` 服务改，直接改字段视为 bug；每次转移写 `state_transitions(obj, from, to, actor, reason, at)`。

---

## 7. 横切约束

### 7.1 输入与字段校验（细表见附录 A）
- 服务端 Pydantic / Django Form 是唯一真源；同一 schema 供 Studio 表单、CI、API。
- 文本一律 NFC 归一、去首尾空白、拒绝控制字符；URL 只允许 https（RSS 源允许 http）；邮箱小写。
- 富文本只有 Markdown，白名单渲染（无原生 HTML；链接 rel 处理；图片只允许自域 / 对象存储域）。

### 7.2 限流与配额（细表见附录 D）
- 维度：IP 哈希、账号、对象（码 / 稿件）；实现：DB 计数表或进程内令牌桶 + Postgres 兜底；超限 429。
- 广播邮件按供应商额度限速；早报必须在 08:00–08:30 内发完，超出容量优先站内发布并顺延邮件。
- 模型成本：日预算硬上限（快讯独立预算）；单任务 tokens 上限；预算耗尽只影响生成，不影响阅读。

### 7.3 安全
- 认证：见 2.12；后台 TOTP；密码 Argon2id；魔法链接与确认链接签名 + 单次 + 过期。
- 会话与 CSRF：Django 默认 + `SameSite=Lax`；HTMX 带头。
- 授权：G1；对象级权限在服务层；API 用 Bearer token（按用途分 token，可撤销，记最后使用）。
- 输入：G10 / G11 / G18；文件重编码；zip 解压检查（路径穿越、总大小、条目数）。
- 输出：模板自动转义；Markdown 白名单；CSP nonce；`X-Content-Type-Options`、`Referrer-Policy: strict-origin-when-cross-origin`、`Permissions-Policy` 收紧。
- 依赖：`uv lock` 锁定；每周依赖漏洞扫描任务；镜像基于 slim，非 root 运行。
- 密钥：G23；Bearer / TOTP 种子 / 会员 RSS token 只存哈希。
- 对外回调：只有邮件退信 webhook，签名校验 + 时间窗 5 分钟 + 幂等。
- 防爬：公开内容允许抓取（许可政策）；`/api` `/redeem` `/go` 有限流；后台路径不在 sitemap 且 robots Disallow；后台可按需加 IP 白名单（Caddy）。

### 7.4 隐私与数据生命周期
| 数据 | 保留 | 处理 |
|---|---|---|
| 会话 | 30 天滑动 | 过期删除 |
| 魔法链接 / 确认 token | 15 分钟 / 24 小时 | 用后即删 |
| IP | 不存明文；哈希日轮换盐 | 30 天后删除哈希 |
| 反馈 / 报错 | 永久（去关联后） | 删除账户时去关联 |
| 划线 / 收藏 / 进度 | 账户存续期 | 删除账户时删除 |
| 问答记录 | 12 个月 | 用户可随时删；到期匿名化 |
| 生成日志 | 24 个月 | 之后只留聚合成本 |
| 广告点击明细 | 13 个月 | 之后只留日聚合 |
| Umami 原始 | 13 个月 | Umami 自身设置 |
| 审计日志 | 36 个月 | 只读 |
| 码（未兑） | 兑换期 + 12 个月 | 之后标 expired 保留后 4 位 |
| 邮件退订 / 抑制 | 24 个月哈希 | 防重复发送 |
| 备份 | 每日全量 30 天 + 每月 12 个月 | 加密，异地 |
`/privacy` 页由此表生成文字；删除账户流程见 2.12；用户数据不进训练语料（`04` §11）。

### 7.5 开关约束
- 开关只影响渲染 / 路由 / 任务是否执行，不删数据；迁移随发版一起上。
- 依赖：所有 `ads.*` 子开关依赖 `ads.enabled`；`ads.self_serve.*` / `ads.launches` / `ads.events` 依赖广告审核清单已落地（人工勾选项）；`ads.programmatic` 依赖联盟账号（人工勾选项）；`paywall.enabled` 依赖 `supporter.enabled`（否则解锁卡无处可去）；`ask.enabled` 与 `search.semantic` 依赖向量索引已建（自动判定）；依赖不满足不能开。
- 每个开关有「关闭态行为」与「开启前置」两段说明，缺一不能上线。

### 7.6 缓存与一致性
- 页面级缓存：匿名公开页 5 分钟（快讯流 1 分钟）；键含 flags 版本 + 登录态类别；`Vary: Cookie` 只对个人块。
- 片段缓存：导航、页脚、推荐位（10 分钟）、术语悬停卡（1 小时）。
- 渲染缓存：`content_nodes.html` 在导入 / 编辑保存时重算。
- 失效：发布、作废、勘误、开关翻转、站点设置改动 → 按标签失效；CDN 只缓存静态与 OG 图，不缓存 HTML（起步态简单可靠）。
- 一致性：兑码、扣额度、计曝光 用 DB 事务与行锁；统计允许最终一致（≤ 1 分钟）。

### 7.7 SEO 约束
- URL 小写、无尾斜杠、日期 `YYYY-MM-DD`；改 slug 自动 301；删除用 410。
- canonical 每页一个；分页 `rel=prev/next` 不用，改用自引用 canonical + 「加载更多」。
- 收费预览可索引（结构化数据声明）；赞助内容默认索引可关；关闭态 404 不在 sitemap；`/app` `/studio` `/admin` `/ads` noindex + Disallow。
- 结构化数据每类型有单测；OG 图必有；标题 ≤ 60 字、描述 50–160 字（front-matter 校验）。

### 7.8 无障碍与性能预算
- G20 / G21；字体：正文系统字体栈，标题字体子集化 ≤ 300KB 总量；图片 `loading=lazy` + 尺寸属性；HTMX 请求带进度指示；`prefers-reduced-motion` 时无动画。
- 每次发版跑 Lighthouse（移动）对 首页 / 文章页 / 快讯流 / 早报，低于预算阻断发布。

### 7.9 可观测性与告警
- SLO：可用性 99.5% / 月；公开页 TTFB p75 ≤ 400ms（缓存）/ ≤ 800ms（未缓存）；5xx ≤ 0.5%；早报 08:00 ± 10 分钟；快讯 SLA 2 小时达成率 ≥ 90%。
- 日志：结构化 JSON，含 request_id、用户类别（不含 id）、路由、耗时；脱敏 G22。
- 告警（邮件 + Studio 通知）：任务连续失败 ≥ 3、抓源停用、成本 ≥ 80% / 100%、早报 07:45 仍无待发刊、5xx 突增、磁盘 ≥ 80%、备份失败、证书 ≤ 14 天、退信率 ≥ 2%。

### 7.10 错误与文案
- 用户可见错误只说「发生了什么 + 怎么办」，不含技术细节；错误码见附录 B；表单错误就近显示；HTMX 失败回退整页提交。

---

## 8. Python 后端架构（不含代码）

### 8.1 选型理由（补 0.1）
Django 而非 FastAPI：本站 90% 请求是服务端渲染页面与后台表单，10% 是机器接口；需要的是认证、会话、CSRF、表单、迁移、admin、RSS、sitemap 这些「电池」，而不是极致异步。异步需求（模型调用、抓源）全部在 worker 里用 `httpx` 完成，不在 web 进程。若日后问答需要流式，Django ASGI 视图可单独承担。

### 8.2 应用划分（Django apps，按领域）

| app | 职责 | 依赖 |
|---|---|---|
| `core` | 站点设置、开关（flags）、审计、状态转移服务、限流、公共模板标签 | — |
| `accounts` | 用户、会话、魔法链接、TOTP、广告主档案、删除流程 | core |
| `access` | 权益引擎（1.3）、手动权益、分组（V2） | accounts, codes |
| `codes` | 码批次、生成、兑换、作废、对账 | accounts |
| `content` | content_nodes、版本、渲染、术语链接、来源、资产、静态页、勘误、changelog | core, graph |
| `graph` | 层、领域、节点、边、路径、单元、DAG 校验、推荐 | core |
| `learning` | 测评规则与结果、progress、bookmarks、highlights、学习台 | content, graph, accounts |
| `news` | 源、抓取、聚类、快讯、实体触发、时间线 | content, generation |
| `issues` | 早报 / 周报 / 深度 / 过时清单编排与发送 | news, content, mail, ads |
| `entities` | 实体、工具目录、认领 | content |
| `search` | 全文与向量索引、搜索日志、缺口信号 | content |
| `ask` | 问答、额度、引用 | search, access |
| `generation` | brief、任务、xAI 调用、沙箱、机审十门、事实清单、提示词版本、成本 | content, core |
| `ads` | 位、广告主活动、排期、素材、审核、投放、统计、`/go`、house、报表、收据 | accounts, access, core |
| `zones` | 招聘 / 发布墙 / 活动 / 优惠 / 赞助内容 条目与审核 | ads, entities |
| `mail` | 模板、事务与广播、订阅者、抑制名单、退信 webhook | accounts |
| `seo` | 重定向、sitemap、robots / llms 生成、结构化数据、OG 图 | content |
| `telemetry` | 服务端事件、metrics_daily、达标线、Umami 拉取 | core |
| `studio` | Studio 页面（编排以上服务） | 多 |
| `ops` | Admin 页面（编排以上服务） | 多 |
| `api` | Django Ninja 路由（导入、日志、健康） | content, generation |

规则：视图薄、服务厚；跨 app 只调服务函数不直接查对方模型；权限与开关只从 `access` / `core.flags` 取（G1 / G2）。

### 8.3 请求路径与渲染
- 公开页：URL → 视图 → 服务取数据（带缓存）→ 模板（`nornless.css` 令牌）→ HTML；个人化块用 HTMX 二次请求（`private`）。
- HTMX：局部片段模板与整页模板共用组件；无 JS 时表单整页提交仍可用。
- 机器：Ninja 路由 → Pydantic 校验 → 服务 → JSON；错误统一结构 `{code, message, detail}`。
- 中间件顺序：安全头 → 会话 → CSRF → 限流 → 开关快照（一次请求内一致）→ 审计上下文。

### 8.4 数据模型总表（承 `04` §9.4，补约束）
- 身份与权益：`users`（email 唯一、小写）、`sessions`、`totp_devices`、`advertisers`、`memberships`（user, start, end；同一时间一条有效）、`entitlements`（user, key, expire_at, source；唯一 (user,key,source)）、`groups` / `group_members` / `group_rules`、`codes`（code_hash 唯一；明文只在生成瞬间返回）、`content_unlocks`（唯一 (user,node)）、`feature_flags`（key 唯一）、`audit_logs`、`state_transitions`。
- 内容图谱：`levels`、`domains`、`topics`、`content_nodes`（slug 唯一；kind 枚举；status 枚举；access 枚举；`html` 渲染缓存；`content_hash`；`review_by ≥ published_at`；`expires_at ≥ review_by`）、`content_versions`、`node_edges`（(from,to,kind) 唯一；无环由服务保证）、`entities`（official_url 必填）、`paths` / `path_items`（(path, unit_index) 唯一）、`glossary_terms`（term 唯一）、`assets` / `asset_versions`、`static_pages`、`errata`、`changelog`。
- 生产：`sources`、`source_items`（url 唯一）、`clusters`、`news`、`briefs`、`generation_jobs`、`fact_claims`、`qa_reports`、`prompts`（(name, version) 唯一）、`assess_rules`。
- 读者：`assessments`、`progress`（(user,node) 唯一）、`bookmarks`、`highlights`、`feedback`、`error_reports`、`ask_threads`、`subscribers`（email_hash 唯一）、`digest_actions`、`search_logs`、`topic_gaps`。
- 广告与专区：`ad_slots`、`ad_campaigns`、`ad_creatives`、`ad_bookings`（同位同日容量约束由服务检查 + 唯一 (slot, date, position)）、`ad_impressions_daily`、`ad_clicks`、`ad_orders`、`receipts`、`tool_listings`、`job_posts`、`launches`、`events`、`deals`、`sponsored_posts`、`claims`、`house_ads`。
- 运营：`mail_templates`、`mail_jobs`、`suppressions`、`redirects`（from 唯一；环检测）、`metrics_daily`、`site_settings`（单行）、`rate_limits`。
- 约束通用：`created_at / updated_at / deleted_at`；外键 `ON DELETE RESTRICT`（软删优先）；枚举用 DB check；金额 `integer` 分；时间 `timestamptz`。

### 8.5 任务与调度（Procrastinate）
| 队列 | 任务 | 周期 / 触发 | 重试 | 幂等键 | 超时 |
|---|---|---|---|---|---|
| `ingest` | 抓源、聚类、评分 | 每源按频率（≥ 15 分钟） | 3 次指数退避 | source_id + 窗口 | 5 分钟 |
| `generate` | 角色链调用、机审、沙箱验证 | 生成台 / 快讯通道 | 2 次（修复提示） | brief_id + role + prompt_hash | 15 分钟（沙箱 10） |
| `freshness` | review_by / expires_at 扫描、过时候选、快讯触发保鲜 | 每日 02:00；快讯发布触发 | 3 次 | node_id + 日期 | 10 分钟 |
| `issues` | 早报汇编 07:00、发布 08:00、周报窗口 | cron | 0（人工介入） | issue_id | 5 分钟 |
| `mail` | 事务即时、广播分批（每批 ≤ 500） | 事件 / 定时 | 5 次 | message_key | 2 分钟 / 批 |
| `render` | Markdown 渲染、术语链接、OG 图、sitemap、RSS | 导入 / 发布触发；sitemap 每小时 | 3 次 | node_id + content_hash | 2 分钟 |
| `stats` | 曝光 / 点击日聚合、metrics_daily、达标线、Umami 拉取、媒体页数据 | 每日 01:00 | 3 次 | 日期 | 10 分钟 |
| `housekeeping` | 会话清理、token 清理、保留期删除、匿名化、备份校验、依赖扫描、发件域检查、死链 | 每日 / 每周 | 3 次 | 任务名 + 日期 | 30 分钟 |
规则：任务只写草稿与统计，发布动作拒绝；失败 ≥ 3 告警；worker 与 scheduler 分容器；任务参数不含密钥与明文个人数据。

### 8.6 外部集成契约
| 对象 | 方向 | 契约与约束 |
|---|---|---|
| nornless 中转站 | 出 | `/v1/responses` OpenAI 兼容；模型名配置；超时 120s；重试 2；成本按当日公开价表（Admin 维护）记账；密钥 `.env` |
| 发卡站（catfk） | 无接口 | 我们生成码 → CSV 导出 → 人工上传为卡密商品；销售导出 → Admin 导入对账；店址 / CSP 在站点设置；无回调、无 API 依赖 |
| 邮件供应商 | 出 + 入（退信 webhook） | SMTP 或 HTTP API 可切；两个发件子域；webhook 签名校验；限速按额度 |
| 对象存储 | 出 | 私有桶 + 签名 URL（10 分钟）；公开桶只放 OG 图与封面；文件名 `public_id.ext` |
| Umami | 出（拉数） | 服务端 API 拉聚合；不拉个人级 |
| Git 平台 / CI | 入 | CI 调 `POST /api/v1/import`（Bearer；body：sha、files[]）；`POST /api/v1/generation-logs`；`GET /api/v1/health`；限流 60 / 分钟 / token |
| 本机 Grok Build skill | 无接口 | 产出文件进 PR；skill 文件由 Studio 导出（4.16） |
| 沙箱 | 内 | Docker socket 只对 worker；镜像白名单；资源限制见 4.4 |
| 爬虫 / 搜索引擎 | 入 | robots / llms / sitemap / JSON-LD（2.19） |

### 8.7 部署拓扑与环境
- Compose 服务：`caddy`（TLS、缓存静态、反代 `/u/` 到 umami、后台路径可加 IP 白名单）· `web`（gunicorn，2–4 worker）· `worker`（procrastinate，并发 3）· `scheduler`（周期任务，单实例）· `postgres`（pgvector + zhparser 镜像，持久卷）· `umami` + `umami-db`。
- 环境：`dev`（本机 compose，假邮件、假模型可开）· `staging`（可选，同 VPS 不同域）· `prod`；`.env` 分环境；密钥不进镜像。
- 备份：每日 `pg_dump` 加密上传对象存储；对象存储版本化；每月恢复演练记录在 Admin 系统页。
- 域名：`ai.nornless.com`（Cloudflare 解析到 VPS；起步只做 DNS 不做代理，避免与 Caddy TLS 冲突；日后可切橙云）。

### 8.8 迁移与发布流程
- 迁移向前兼容：先加列后用、先停用后删列；每次发版 `migrate` 前自动备份；禁止在迁移里写业务数据变更（用管理命令）。
- 发布：CI 绿（8.9）→ 构建镜像 → 拉取 → `migrate` → 滚动重启 `web` → 健康检查 `/api/v1/health` → 重启 `worker` / `scheduler`；失败回滚镜像 + 迁移回退脚本（仅向前兼容迁移可回滚）。
- 内容发布与代码发布分离：内容走 4.17，不重启服务。

### 8.9 质量门与测试策略
- 静态：`ruff`（lint + format）、`mypy --strict`（业务层）、模板 lint（djlint）、迁移检查（`makemigrations --check`）。
- 测试：单元（服务层，权限矩阵全组合、状态机全转移、校验规则）；模板测试（强制模块存在、角标存在、关闭态无入口）；集成（导入契约、兑码并发、限流、收费态截断抓包）；端到端冒烟（首页 / 文章 / 快讯 / 早报 / 兑码 / 审稿列表）；覆盖率 ≥ 80%（服务层 ≥ 90%）。
- 性能：Lighthouse 预算（7.8）；关键查询 EXPLAIN 基线。
- 安全：依赖扫描、`bandit`、CSP 报告端点抽样查看。
- 每次交付：`uv run lint && uv run test && uv run build` 绿 + URL 清单 + 「怎么验证的」+ 关闭态截图（`AGENTS.md`）。

### 8.10 仓库结构

```text
aigc知识付费/（content-site 仓）
  00–06 规划文档
  editorial/                      风格、红线、outline.yml、模板、skills、prompts、ads-policy、ad-review-checklist、schema 导出
  content/                        Markdown 源（front-matter v3）+ <slug>.log.json + <slug>.qa.json
  assets/                         资源包源文件
  wireframes/                     01 的线框 + 新页线框
  app/                            Django 项目
    config/                       settings（base / dev / prod）、urls、asgi / wsgi
    core/ accounts/ access/ codes/ content/ graph/ learning/ news/ issues/ entities/ search/ ask/ generation/ ads/ zones/ mail/ seo/ telemetry/ studio/ ops/ api/
    templates/                    base、components、site、app、ads、studio、admin（用 nornless.css 令牌）
    static/                       nornless.css、htmx、alpine、自有 ≤ 10KB js
    tests/
  deploy/                         compose、caddy、备份脚本、pg 镜像 Dockerfile
  pyproject.toml  uv.lock  ruff.toml  mypy.ini
```

### 8.11 与 `04` §9 / `AGENTS.md` 的差异
- 替换：Next.js → Django + HTMX；pg-boss → Procrastinate；Drizzle → Django ORM + 迁移；`web/lib/access.ts` → `app/access/`；`web/lib/flags.ts` → `app/core/flags`；`worker/` Node → `worker` / `scheduler` 容器跑同一 Django 代码；`pnpm` → `uv`。
- 不变：数据模型语义、权益唯一真源、开关语义、生成与发布隔离、服务端渲染广告、无第三方脚本、`nornless.css` 令牌真源、Umami、对象存储、Docker Compose + Caddy。
- `AGENTS.md` 已同步（栈、目录、验收命令）。

---

## 9. 验收总表（按面向）

| 面向 | 必过 |
|---|---|
| 对外站 | 无 JS 可读可导航；强制模块 100%；关闭态路由 404 且无入口、不进 sitemap；收费态截断抓包验证；零第三方请求；Lighthouse 移动 LCP ≤ 2.5s、无障碍 ≥ 95；RSS / sitemap / robots / llms / OG / JSON-LD 校验通过；限流 429 生效 |
| 读者区 | 匿名进度登录合并正确；读完标记幂等可撤销；导出 zip 完整；删除账户 7 天后匿名化验证；会员 RSS token 重置即失效 |
| 支持者与码 | 兑码并发只成功一次；五种错误文案一一对应；权益 ≤ 1s 生效；到期权益即时收回；对账差异列表正确 |
| 广告主门户 | 素材字段限制服务端生效；脚本 / iframe / 像素被拒；审核三态与 ≤ 3 次修改；占比 30% 拒排；报表只出聚合 |
| Studio | 状态机非法转移被拒（全组合测试）；十门任一失败不能进 factcheck；事实清单 100% 才能进 editing；bot 与 worker 不能发布；成本上限停机；沙箱资源限制生效；审稿列表 3 分钟 / 条可达成；早报 08:00 ± 10 分钟 |
| Admin | 开关翻转需原因且 30s 内全站生效；前置未满足需强制确认；自动回退触发并通知；码明文只可下载一次；审计 before / after 完整；维护模式后台可用 |
| 机器接口 | 导入幂等（同 sha 重放无变化）；PR 校验规则全部阻断样例；退信 webhook 伪造签名被拒；`/go` 未知 id 404 |
| 运维 | 每日备份存在且可恢复演练；迁移前备份；健康检查；告警到达邮件 |

---

## 附录 A · 字段校验细表

| 对象 | 字段 | 规则 |
|---|---|---|
| 内容 | title | 4–60 字；不含红线；全站近似重复（相似度 ≥ 0.9）警告 |
| 内容 | slug | `^[a-z0-9]+(-[a-z0-9]+)*$`，≤ 80，唯一；改名自动 301 |
| 内容 | summary | 50–160 字 |
| 内容 | kind / level / domain | 枚举；level 与 track 层级一致 |
| 内容 | prereqs / next | 存在的 node_id；无环；≤ 6 |
| 内容 | sources[] | 概念 / 单元 ≥ 1；快讯 / 实体 / 深度 ≥ 2 且 ≥ 1 官方；每条 title、url(https)、publisher、date、tier |
| 内容 | ai.* | generated、model、assist_ratio(0–1)、prompt_version、reviewed_by（发布前非空）、factcheck_status=passed（发布前） |
| 内容 | verified | sandbox / manual / none；sandbox 需 verified_env |
| 内容 | last_verified_at / review_by / expires_at | last ≤ now；review_by ≥ published_at；expires_at ≥ review_by |
| 内容 | access | free / supporter / code / group；默认 free |
| 内容 | 正文 | 概念卡 800–2000 字；单元 2000–6000；深度 3000–8000；快讯 200–400；代码块必带语言；图片必带 alt；外链 ≤ 30 |
| 快讯 | 3 点结论 | 每点 ≤ 40 字；不得含未在正文出现的事实 |
| 快讯 | 挂接节点 | ≥ 1 |
| 术语 | term / en / definition | 唯一；定义 ≤ 60 字；展开 ≤ 300 字 |
| 实体 | official_url | https，必填，HEAD 可达（403 允许） |
| 广告素材 | title / body / button | ≤ 24 / ≤ 60 / ≤ 6 字；无绝对化用语；过红线 |
| 广告素材 | image | png / jpg / webp；16:9 ≤ 200KB 或 1:1 logo；重编码 |
| 广告素材 | url | https；域名 = 主体官网域或白名单 |
| 招聘 | title / company / salary / url | ≤ 40 / ≤ 30 / 格式 `min–max k/月` 或「面议」/ https；30 天 |
| 发布墙 | title / tagline / url | ≤ 40 / ≤ 140 / https；同链接 30 天内唯一 |
| 活动 | name / host / time / price / url | ≤ 40 / ≤ 30 / 未来时间 / ≥ 0 / https |
| 优惠 | entity / code / url / disclosure / valid_to | 存在实体 / ≤ 32 / https / 必填 / 未来 |
| 码 | code | `NRL-XXXX-XXXX-XXXX` Crockford base32 无 0O1I；存哈希 |
| 用户 | email / password / display_name | RFC 5322 小写、一次性域名拒 / ≥ 10 位 zxcvbn ≥ 3 / ≤ 20 字过红线 |
| 订阅 | email / prefs | 同上 / 枚举集合 |
| 反馈 | kind / anchor / text | 枚举 / 存在的段落 id / ≤ 500 字 |
| 问答 | question | 2–500 字 |
| 认领 | email / fields | 域名 = 官网域 / 只允许白名单字段 |
| 询盘 | company / email / budget / message | ≤ 60 / RFC / 枚举 / ≤ 1000 字 |

## 附录 B · 错误码

`E_AUTH_REQUIRED`（需登录）· `E_FORBIDDEN`（无权限）· `E_NOT_FOUND`（不存在或关闭态）· `E_RATE_LIMITED`（429）· `E_VALIDATION`（字段错误，附字段表）· `E_STATE`（状态不允许该操作）· `E_CODE_INVALID` / `E_CODE_REDEEMED` / `E_CODE_EXPIRED` / `E_CODE_TYPE`（兑码四态）· `E_QUOTA`（额度用尽）· `E_BUDGET`（模型预算耗尽）· `E_LOCKED`（稿件被他人编辑）· `E_DEPENDENCY`（开关依赖未满足）· `E_UPSTREAM`（模型 / 邮件 / 存储上游失败）· `E_MAINTENANCE`（503）。用户文案与错误码一一映射，文案在站点设置可改。

## 附录 C · 埋点

沿 `05` §12 全表；本文新增：`unit_done`、`unlock_card_click(kind)`、`redeem_submit(result)`、`pricing_shop_click`、`claim_verified`、`assess_share`、`digest_action_check`、`library_export`、`ads_portal_*`（门户内，仅广告主）。服务端事件：曝光 / 点击 / 开关变更 / 状态转移 / 兑码 / 成本；均不含个人标识。

## 附录 D · 限流

| 动作 | 维度 | 限制 |
|---|---|---|
| 登录失败 | 账号 + IP | 5 / 15 分钟，锁 15 分钟 |
| 魔法链接 / 确认邮件 | 邮箱 | 3 / 小时；24h 内 ≤ 3 封确认 |
| 注册 | IP | 10 / 小时 |
| 兑码 | 用户 | 10 / 小时；失败 5 次锁 1 小时 |
| 反馈 / 报错 | 用户或 IP | 30 / 日；10 / 日 |
| 搜索 | IP | 60 / 分钟 |
| 测评 | IP | 60 / 小时 |
| 问答 | 用户 | 按权益日额；并发 1 |
| 下载 | 用户 | 50 / 日 |
| 导出 | 用户 | 1 / 分钟；zip 1 / 小时 |
| 询盘 / 认领 | IP | 3 / 日 |
| `/go` | 会话 + 素材 | 计数 1 / 分钟 |
| API 导入 | token | 60 / 分钟 |
| 退信 webhook | 供应商 | 100 / 分钟 |
| 后台写操作 | 账号 | 600 / 小时（防脚本误操作） |

## 附录 E · 开关表
以 `05` §2.2 为准，新增 `paywall.enabled`（关 / 关 / 择开；依赖 `supporter.enabled`）与 `quiz.enabled`（关 / 关 / 择开）已并入；本文 5.8 列出全部键名。
