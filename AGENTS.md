# AGENTS.md · ai.nornless.com（文档代号「阶见」）

给在这个目录里干活的编码代理看。人也可以看。

冲突时：`docs/06` > `docs/05` > `docs/04`。不要发明开关键名或路由。

## 先读

1. `docs/06-功能设计-对外与后台-Python后端.md` — 功能、约束 G1–G24、状态机、apps、验收。
2. `docs/05-产品推导-体验优先与广告开关.md` — 开关语义、推荐位关闭态、体验达标线。
3. `docs/04-阶见合并规划-广告为主.md` — 定位、内容、商业、路线图。
4. `docs/01-页面设计.md` — 令牌与版式；`wireframes/index.html` 是 61 页线框，不是产品代码。
5. `docs/00` / `02` / `03` — 文首有状态；`02` 的 B 路暂不采用。

## 目录

- `app/` Django 项目（`config` + 业务 apps + `templates` + `static` + `tests`）
- `editorial/` 风格、红线、outline、8 模板、8 skill、广告政策、front-matter schema
- `content/` Markdown 源（front-matter v3）+ `<slug>.log.json` + `<slug>.qa.json`，导入用
- `wireframes/` 线框；旧六页在 `_legacy/`
- `deploy/` 本机 compose / Caddy 草稿；**不要**往 65/87 或生产发
- `grok-export/` Grok 原稿，只读

## 栈

- Python 3.12 + Django 5.2 LTS + 模板 SSR + HTMX + Alpine（无 SPA）
- Django Ninja：`/api/v1/*`
- 本机可 sqlite；目标 PostgreSQL 16 + pgvector + zhparser
- 队列：Procrastinate（免 Redis）；现阶段可不上 worker
- 包管理：`uv`；检查：`ruff` / `mypy` / `pytest` / `djlint`
- 不用 FastAPI、Celery、Next.js；Redis / Meilisearch 是目标态不是起步

系统 `python3` 可能是 3.9。一律：

```bash
uv sync --extra dev
uv run python manage.py …
uv run pytest
```

## 硬规则

- 权限只在 `app/access/` 算：`entitlements` / `visible` / `can_read_full` / `sees_ads` / `can`。页面、API、导入、Studio 都调它。
- 开关只在 `app/core/flags.py` 声明键名（05 §2.2），`core.services.snapshot()` / `set_flag()` 求值。广告子开关在 `ads.enabled` 为假时视为关。
- 状态只经 `transition()`。非法转移抛错。bot（`staff_role=author`）不能发布。
- 付费正文服务端裁切：`paywall.enabled` 开时未授权部分不进 HTML / JSON。预览分割 `<!-- more -->`，否则前约 30%。
- 专属 / 未发布 / 开关关闭的专区：404，不是 403；列表与 sitemap 不出现。
- 码制：会员码 / 内容码 / 广告码。明文只在生成瞬间返回；库里只存哈希。不接支付 SDK。
- 广告位全部建好，总开关默认关；关时路由 404、推荐位渲染编辑内容。标识由模板注入。
- 公开页零第三方请求。HTMX / Alpine 必须 vendor 进 `app/static`，禁止 CDN。
- 视觉只用 `app/static/nornless.css` 令牌；青绿 `#14b8a6` 不出现；浅色正文级金字只用 `#8b6914`。
- 不做：LMS（评分 / 排名 / 作业 / 证书）、测验（`quiz.enabled` 关）、动手实验区（`labs.enabled` 关）、公众号、UGC、DRM、微信登录（开关关）。
- 密钥只在 `.env`。不改本目录之外的东西。不碰线上服务器、不改 65/87 Caddy。不 commit，除非用户明确要求。

## 开关键名（只准用这些）

`ads.enabled` 及 `ads.*` 子键、`supporter.enabled`、`ask.enabled`、`quiz.enabled`、`paywall.enabled`、`labs.enabled`、`tipping.enabled`、`groups.enabled`、`wechat_login.enabled`、`search.semantic`、`email.digest`（默认开）、`outdated.banner`（默认开）。

关时 404：`/jobs` `/launches` `/events` `/deals` `/sponsored` `/advertise` `/pricing` `/app/ask` `/join`。

## 第 0 步算完的标准

```bash
uv run python manage.py migrate
uv run python manage.py seed_all
uv run python manage.py bootstrap   # 打印一次 TOTP，写入认证器
uv run python manage.py runserver
uv run pytest
```

必须能看见：首页、学习地图、文章、概念卡、快讯；关闭开关的专区 404；`/redeem` 能兑一张手发的会员码；`GET /api/v1/health` 200；`/studio/` 与 `/ops/flags` 要登录 + 员工 TOTP。

## 提交

用户没要求就不要 commit、不要 push。若要求：小步、中文说明「做了什么 + 怎么验证」。不 force-push。范围外的脏改动不要顺手清掉。
