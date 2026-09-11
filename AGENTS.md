# AGENTS.md · AIGC 知识付费站

给在这个目录里干活的编码代理看（DeepSeek Harness / Claude Code / Codex / Cursor 都读这份）。人也可以看。

## 先读

1. `00-网站规划.md` — 功能、数据表、权限规则、分步与验收场景。
2. `01-页面设计.md` — 风格令牌、版式、每页线框说明。
3. `02-DeepSeek-Harness集成.md` — 走 B 路（dsh 为脚手架）时的插件清单、配置层、分步。
4. `wireframes/nornless.css` — 视觉令牌真源；`wireframes/*.html` 是版式参考，不是产品代码。

## 目录

- `content/` Markdown 源，只读，导入用。不要改里面的文件。
- `web/` A 路网站代码。第 0 步在这里初始化。
- `harness/` B 路 dsh 插件 workspace（`packages/kb-*`、`bundles/`、`presets/`）。H0 在这里初始化。`skills/` 放每篇案例 / 教程的 `SKILL.md`。
- `wireframes/` 静态线框。不要往里写业务逻辑。

## 栈（用户未另说时默认）

- A 路：Next.js（App Router, TypeScript）+ PostgreSQL + Drizzle + Tailwind；Markdown 用 remark + shiki；cookie session；上传文件存 `web/data/uploads`。
- B 路：TypeScript Cordis 插件；HTTP 用 `ctx.webServer` fallback 挂 Hono（`@hono/node-server` 的 `getRequestListener`），页面用 Hono JSX 字串 SSR；存储用 `ctx.storageDomain` + `sqlite` 后端；Markdown 同上。不碰 `@Remote` / Typert 生成链；不改 dsh 源码，一切用上层 patch 或新插件。

## 硬规则

- 权限只在一处算：A 路 `web/lib/access.ts`，B 路 `@aigc/kb-access` 服务（`ctx.kbAccess`）；都导出 `visible()` / `canReadFull()` / `priceFor()`，页面、API、工具、技能目录、助教都调它，不要各写一份。规则见 `00-网站规划.md`「权限规则」。
- 付费正文在服务端裁切：未授权的部分不进 HTML、不进 JSON。预览分割线 `<!-- more -->`，缺省前 30%。
- 专属文章对无权用户返回 404，列表不出现；不是 403 页。
- 不做：课程进度 / 作业 / 评分 / 直播；DRM / 禁复制 / 禁右键；第 1 版接支付 SDK。
- 密钥只在 `.env`，不进仓库、不进文档、不进日志。
- 视觉只用 `nornless.css` 里的令牌；青绿 `#14b8a6` 不出现；浅色正文级金字只用 `#8b6914`。
- 写操作走遮罩弹窗；列表显示中文状态和展示名称。
- 不改本目录之外的任何东西；不碰线上服务器。

## 每步算完的标准

A 路：

- 第 0 步：`pnpm dev` 起得来；`pnpm import ../content` 后首页 / 分类 / 文章能看（全免费）；后台能登录。
- 第 1 步：`00-网站规划.md`「第 2 步结束时要过的场景」第 1–3 条通过。
- 第 2 步：第 4–7 条全部通过。

B 路（`02` 的 H0–H6）：

- H0：`dsh --profile aigc-site --dump-config` 里能看到 `@aigc/site` 层；进程起得来。
- H1：导入 `content/` 后首页 / 分类 / 文章 SSR 能看，`nornless.css` 生效。
- H2 / H3：同 A 路第 1 / 2 步的验收条。
- H4：本机 `dsh web` 装上 `@aigc/studio` 填令牌后，已解锁文章出现在 `<available_skills>`，未解锁的不出现；`kb_read` 对未解锁返回拒绝。
- H5：文章页助教只引用已解锁正文，对未解锁问题答「先解锁」。

每步都要：`pnpm lint && pnpm test && pnpm build` 绿；交一份可点的 URL 清单和一段「怎么验证的」。

## 提交

- 小步提交，一件事一个 commit，消息用中文写「做了什么 + 怎么验证的」。
- 不 force-push。范围外的脏改动不要顺手清掉。
