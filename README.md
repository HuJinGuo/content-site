# ai.nornless.com（文档代号「阶见」）

Grok 写、人审、保鲜的 AI 知识阶梯 + 科技情报站。内容默认免费，广告预留、总开关默认关。

编码代理先读根目录 `AGENTS.md`。规划冲突：`docs/06` > `05` > `04`。

| 文件 | 角色 |
|------|------|
| `docs/06-功能设计-对外与后台-Python后端.md` | 功能与约束规格，冲突时最优先 |
| `docs/05-产品推导-体验优先与广告开关.md` | 体验、开关、推荐位关闭态 |
| `docs/04-阶见合并规划-广告为主.md` | 主规划：定位、内容、商业、路线图 |
| `docs/01-页面设计.md` | 视觉令牌与版式 |
| `docs/00` / `02` / `03` | 参考或部份沿用，文首有状态 |
| `wireframes/index.html` | 全站 61 页线框；旧六页在 `_legacy/` |
| `editorial/` | 红线、模板、skill、outline |
| `content/` | Markdown 源 |
| `app/` | Django 5 站点 |
| `grok-export/` | Grok 原稿，只读 |

## 本机跑起来

需要 Python 3.12（不要用系统自带的 3.9）和 [uv](https://docs.astral.sh/uv/)。

```bash
cp .env.example .env
uv sync --extra dev
uv run python manage.py migrate
uv run python manage.py seed_all
uv run python manage.py bootstrap   # 打印一次 TOTP，写入认证器
uv run python manage.py runserver
uv run pytest
```

默认 sqlite（`db.sqlite3`）。可选 Postgres：`deploy/compose.yml`，把 `.env` 的 `DATABASE_URL` 改成注释里那行。

不要部署、不要改 65/87 的 Caddy。发卡站商品与 DNS 由人做。
