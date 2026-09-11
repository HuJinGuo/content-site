# AIGC 知识付费站 · 以 DeepSeek Harness 为脚手架

更新：2026-09-06
前置：`00-网站规划.md`（功能 / 数据 / 权限）、`01-页面设计.md`（视觉）
依据：dsh 官方文档 Architecture / Publish / Storage / Skills / Web Server / Slots（2026-09-06 读的 developer preview 版本，字段以本机 `dsh --profile <名> --dump-config` 输出为准）

## 一句话

**整站就是一棵 dsh 插件树。** dsh 提供进程、HTTP 载体、存储、模型路由、工具、技能、会话、审批、沙箱、客户端 UI 槽位；我们写的每个功能——内容、权限、付费墙、分组、后台、AI 助教、学员侧技能——都是一个 Cordis 插件，装进一个自定义 profile。不改 dsh 源码，只加层。

## 为什么这样成立（dsh 的四个机制）

1. **Profile = 有序的 bundle 层 + patch 层。** `dsh --profile aigc-site` 启动时按顺序叠：`@deepseek-ai/dsh-base`（模型适配 / 工具 / 持久化 / 存储 / 设置 / 凭据）→ 我们的 bundle → profile 的 `cordis.patch.yml` → 家目录 patch → `--patch` 覆盖。任何一行都能按 `id` 被上层替换。`dsh plugin --profile aigc-site add ./bundles/site` 一条命令装进去。
2. **`ctx.webServer` 是裸 `node:http` 载体**：命名路由（exact / prefix）、SSE、一个 fallback 席位。不装 `dsh-web-app` 时席位是空的，我们认领它，整站 HTML 就从 dsh 进程里出。载体**不带认证、TLS、Origin 策略**，这些由我们的路由和前面的 Caddy 负责。
3. **`ctx.storageDomain`**：zod 声明表结构，`sqlite` 后端落盘，读全在内存、写先落盘再改内存、`domain/changed` 事件。用户 / 分组 / 文章 / 订单都放这。
4. **`ctx.skills` / `ctx.tools` / `ctx.agents` / 客户端 `ctx.slots`**：内容能以「技能」进学员的代理；`kb_read` 工具让模型只读到已解锁正文；服务端能为每个访客开受限会话做助教；学员本机 dsh 的侧栏和设置能插我们的卡。

## 两个 profile，一份代码

| profile | 跑在哪 | 叠的层 | 干什么 |
|---|---|---|---|
| `aigc-site` | 一台 VPS，`127.0.0.1:3090`，Caddy 反代 | `dsh-base` + `@aigc/site` + patch | 公共站：读、付费墙、分组、后台、助教、给学员发技能目录 |
| `web`（学员 / 作者本机） | 各自电脑，`dsh web` | `dsh-base` + `dsh-web-app` + `@aigc/studio` | 学员：填站点令牌 → 已解锁教程 / 案例变成技能、`kb_read` 能读；作者：写作、导入、发布 |

公共站**永远不挂 dsh 的浏览器控制台**：那是单操作者的本地工具，它的会话认证不为多用户设计。学员在自己机器上跑 dsh。

## 插件清单

| 插件 | 提供的服务 / 面 | 用到的 dsh 接缝 |
|---|---|---|
| `@aigc/kb-store` | `ctx.kbStore`：`users` `sessions` `groups` `group_members` `group_rules` `articles_meta` `entitlements` `orders` `redeem_codes` `audit` | `ctx.storageDomain.open(defineDomain({...}))`，路由到 `sqlite` 后端；表值 zod；写后 `domain/changed` |
| `@aigc/kb-content` | `ctx.kb`：读 `content/**.md` + front-matter，渲染 HTML（remark + shiki），按 `<!-- more -->` 裁切，内存全文索引，附件清单；命令 `/kb import` | 自有服务；`ctx.commands` 注册人类命令 |
| `@aigc/kb-access` | `ctx.kbAccess`：`visible()` `canReadFull()` `priceFor()` —— **唯一真源**，规则同 `00` | 自有服务，`inject: ['kbStore']`；被 web / tools / skills / tutor 注入 |
| `@aigc/kb-web` | 公共站全部 HTTP：页面 SSR、cookie 会话、注册登录、`/join` `/me` `/buy` `/admin/*`、`/api/kb/*`、`/assets` `/uploads`、上传 | `ctx.webServer.registerFallback()` 挂一个 **Hono** 应用（路由 / 表单 / cookie / JSX SSR 全有）；SSE 用 `register({kind:'exact', path:'/api/tutor/stream'})` |
| `@aigc/kb-tools` | 模型工具 `kb_search` `kb_read`（只回已解锁正文）+ 系统提示段 | `ctx.tools.register(defineTool(...))`、`ctx.systemPrompt.section()`、`tools/pre-execute` 门按会话身份拒越权 |
| `@aigc/kb-skills` | 技能提供方：每篇案例 / 教程一个 `skills/<slug>/SKILL.md`，目录按权限过滤 | `ctx.skills.registerProvider(control => ({ name, list, get }))`；`list()` 里带令牌拉 `站点/api/kb/skills`，`get()` 拉正文 |
| `@aigc/kb-tutor` | AI 助教：文章页「问这篇」→ 服务端为访客开一个受限会话 → SSE 回流 | `ctx.agents` 建 / 续会话；`ctx.agentPresets` 的 `presets/tutor/cordis.yml`（只留 `kb_read`，去掉 fs / bash，`ctx.tools.restrict`）；`agent.inject()` 塞已解锁正文；`session/event` 渲染 |
| `@aigc/kb-client`（studio 侧） | dsh Web UI 里「知识库」设置卡（站点地址 / 令牌 / 已解锁列表）、侧栏入口 | `dsh.client` 客户端模块；`ctx.slots.inject('settings.section', …)`、`sidebar.footer.action`；令牌走 `ctx.credentials`，不进 yaml |

bundle 只是打包：`@aigc/site` = 前 7 个的 `cordis.patch.yml`；`@aigc/studio` = `kb-tools` + `kb-skills` + `kb-client`。

## 三条数据流

```text
访客读文章
  Caddy → kb-web(Hono) GET /a/<slug>
       → kbAccess.visible / canReadFull(user, article)
       → kb.render(article, { cutAt: more })      # 未授权部分不进 HTML
       → 01 的版式 + nornless.css

学员在本机 dsh 里
  kb-skills.list()  →  GET 站点/api/kb/skills  (Bearer 令牌)
                    ←  服务端 kbAccess 过滤后的目录
  模型调 skill({name}) → kb-skills.get() → GET /api/kb/skills/<name>（再查一次权限）
  模型调 kb_read      → 同一条接口；tools/pre-execute 门兜底

助教
  文章页 POST /api/tutor/ask {slug, q}
    → ctx.agents.create(sessionId, { preset: 'tutor', cwd: 空沙箱目录 })
    → agent.inject(已解锁正文)  → agent.followup(q)
    → session/event 里的 assistant/chunk → SSE → 右栏
```

## 目录

```text
aigc知识付费/
  harness/                      pnpm workspace，全部 TypeScript
    packages/
      kb-store/  kb-content/  kb-access/  kb-web/  kb-tools/  kb-skills/  kb-tutor/  kb-client/
    bundles/
      site/    package.json（dsh.bundle）+ cordis.patch.yml
      studio/  同上
    presets/
      tutor/cordis.yml          助教会话预设
    profiles/aigc-site.patch.example.yml   给 VPS 的 profile patch 样例（真文件在 $DSH_HOME）
  content/   Markdown 源（kb-content 读这里）
  skills/    每篇案例 / 教程的 SKILL.md（kb-skills 从这里发）
  wireframes/  01 的线框；nornless.css 直接被 kb-web 当 /assets 发出去
```

## 配置样例（示意，字段以 `--dump-config` 为准）

`bundles/site/cordis.patch.yml`：

```yaml
- insert:
    - id: kb-store
      name: '@aigc/kb-store'
      config: { backend: sqlite }
    - id: kb-content
      name: '@aigc/kb-content'
      config: { contentDir: /srv/aigc/content, uploadsDir: /srv/aigc/uploads }
    - id: kb-access
      name: '@aigc/kb-access'
    - id: kb-web
      name: '@aigc/kb-web'
      config: { publicUrl: https://kb.example.com, sessionTtlDays: 30 }
    - id: kb-tools
      name: '@aigc/kb-tools'
    - id: kb-tutor
      name: '@aigc/kb-tutor'
      config: { preset: tutor, model: 'nornless-grok/grok-4.6', maxTurnsPerVisitor: 20 }
```

`$DSH_HOME/profiles/aigc-site/cordis.patch.yml`（机器私有，`dsh plugin add` 后自己写）：

```yaml
# 替换 dsh-base 里的行：整份 config 要重写，patch 不做深合并
- id: webserver
  config: { host: 127.0.0.1, port: 3090, compression: gzip }
- id: llm-pi-ai
  config:
    providers:
      nornless-grok:
        api: openai-responses
        baseURL: https://api.nornless.com/v1
        models: [{ id: grok-4.6 }, { id: grok-build-0.1 }]
# 公网站进程不需要这些模型工具，关掉
- id: tool-bash
  disabled: true
- id: tool-fs
  disabled: true
```

Key 不写这里：走 Settings → Models 或 `ctx.credentials`，落 `$DSH_HOME/.credentials.yaml`。

`presets/tutor/cordis.yml`：

```yaml
- id: tutor-tools
  name: '@aigc/kb-tools/restrict'      # ctx.tools.restrict(['kb_read'])
- id: tutor-prompt
  name: '@aigc/kb-tutor/prompt'        # systemPrompt.section：只答这篇、引用段落、不编造
```

## 代码骨架（示意）

权限服务：

```ts
// packages/kb-access/src/index.ts
import type { Context } from '@deepseek-ai/cordis'
export const name = 'kb-access'
export const inject = ['kbStore']

export class KbAccess {
  constructor(private ctx: Context) {}
  visible(user, article) { /* 00 的规则 */ }
  canReadFull(user, article) { /* 文章 > 分类 > 组默认；多组取优 */ }
  priceFor(user, article) { /* 命中折扣取最低 */ }
}
export function apply(ctx: Context) {
  ctx.set('kbAccess', new KbAccess(ctx))   // 注册为服务；卸载即撤
}
```

公共站挂 Hono：

```ts
// packages/kb-web/src/index.ts
import { Hono } from 'hono'
import { getRequestListener } from '@hono/node-server'
export const name = 'kb-web'
export const inject = ['webServer', 'kb', 'kbAccess', 'kbStore']

export function apply(ctx: Context, config: Config) {
  const app = new Hono()
  app.use(sessionCookie(ctx.kbStore))                 // 自己写的认证
  app.get('/', home)  app.get('/c/:cat', category)
  app.get('/a/:slug', article)                        // 服务端裁切
  app.route('/admin', admin(requireAdmin))
  app.get('/api/kb/skills', bearer, listEntitledSkills)
  ctx.effect(() => ctx.webServer.registerFallback(getRequestListener(app.fetch)))
}
```

学员侧技能提供方：

```ts
// packages/kb-skills/src/index.ts
export const inject = ['skills', 'credentials']
export function apply(ctx: Context, config: { site: string }) {
  ctx.skills.registerProvider(control => ({
    name: 'aigc-kb',
    async list({ signal }) {
      const token = await ctx.credentials.resolve('aigc-kb-token')
      const r = await fetch(`${config.site}/api/kb/skills`, { headers: { authorization: `Bearer ${token}` }, signal })
      return (await r.json()).map(s => ({ ...s, rank: 350, provider: 'aigc-kb', locator: s.name,
        invocation: { modelInvocable: true, userInvocable: true }, source: 'custom' }))
    },
    async get(c, { signal }) { /* GET /api/kb/skills/<name> → { content, resourceBase } */ },
  }))
}
```

## 部署

- VPS：`DSH_HOME=/srv/aigc/dsh dsh --profile aigc-site`，systemd 常驻；只听 `127.0.0.1:3090`；Caddy 做 TLS 和反代（**新机器新 Caddy，不上 87 / 65 那两台**）。
- 不是 `dsh web`：那条命令拒绝非回环并带单操作者认证；我们是自定义 profile。
- 备份：`$DSH_HOME/storage/`（sqlite）+ `content/` + `uploads/` + `skills/`，每日一份。
- 钉版本：`harness/package.json` 里 `@deepseek-ai/dsh` 钉具体版本或 git commit；升级前后 `--dump-config` 对比 diff。
- 密钥：只在 `$DSH_HOME/.credentials.yaml` 和 `.env`，不进仓库。

## 分步（替代 `00` 的第 0–3 步）

| 步 | 目标 | 交付 |
|---|---|---|
| H0 | 脚手架立起来 | 本机装 dsh；`hello` 插件按官方教程跑通；`aigc-site` profile 建好，`--dump-config` 能看到我们的层 |
| H1 | 能看 | `kb-store` + `kb-content` + `kb-web` 只读版：导入 `content/`，首页 / 分类 / 文章 SSR，全免费，`nornless.css` 生效 |
| H2 | 能收 | 注册登录 + `kb-access` + 付费墙裁切 + 兑换码 + 人工确认订单 + `/me`（`00` 验收 1–3） |
| H3 | 能分组 | 分组默认策略 / 特例规则 / 邀请码 / 成员到期 + 后台（`00` 验收 4–7） |
| H4 | 内容进代理 | `kb-tools` + `kb-skills` + `@aigc/studio`：学员本机 `dsh plugin --profile web add @aigc/studio`，填令牌，已解锁内容出现在 `<available_skills>`，`kb_read` 能读 |
| H5 | 助教 | `kb-tutor` + `presets/tutor`：文章页问答 SSE，只答已解锁内容 |
| H6 | 上线 | 新 VPS + Caddy + systemd + 备份 + sitemap |

H0 半天，H1–H3 各 2–3 天，H4 2–3 天，H5 2 天。

## 诚实的账

- **H1–H3 和 Next.js 版一样多**。付费墙、分组、后台是业务逻辑，dsh 不替你写；Hono + JSX 字串 SSR 替代 Next 的页面层，轻但少了成熟表单 / 路由生态。
- **H4、H5 几乎白送**：模型路由、工具、技能目录、会话持久化、审批、沙箱、子代理、客户端槽位都是现成的。**产品里有「内容进代理 + 助教」，用 dsh 是净赚；没有，就是净亏。** 这个平台的内容本来就是 Agent 用法，所以值。
- **存储是 KV**：读全内存、单文档落盘。用户 / 订单几万条内没问题；报表在内存过滤。超了把 `kb-store` 内部换成自己开的 SQLite 表，别的插件不知情。
- **不碰 `@Remote` / Typert**：那套要 tsc + 生成器 + 客户端打包链。Host↔浏览器通信全走普通 HTTP + fetch；只有 `kb-client` 的设置卡是真客户端模块，放 H4 末尾，做不动就先用环境变量 `AIGC_KB_TOKEN` 顶着。
- **developer preview**：接口会变，钉版本，每次升级先跑一遍 `00` 验收场景。卡死的话，`kb-*` 里的业务逻辑（权限、内容、模板）都是纯函数和 Hono 路由，搬到 Next.js 只丢 dsh 那层胶水。
- **安全**：载体无认证，`kb-web` 每条路由自己查会话；CSRF token；上传限类型大小；助教按访客限次；Caddy 限速。`dsh-web-app` 绝不上公网。

## 不要

- 把公共站和 dsh 浏览器控制台跑在同一个 profile 里对外。
- 在 `dsh-base` 的行上做「只改一个键」的 patch：patch 是整份替换。
- 把令牌 / Key 写进 `cordis.patch.yml` 或仓库。
- 一开始就做客户端模块（`dsh.client` + 打包链）；先 H1–H3。
- 改 dsh 源码。要改的行为都用上层 patch 覆盖或新插件。

## 拍板

1. 架构：**B. dsh 为脚手架（本文）** 还是 **A. Next.js 纯站（`00`）**。B 的前提是产品要有 H4 / H5。
2. 其余同 `00` 待定：账号标识、收款主体、备案 / 境外、站名。
