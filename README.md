# 内容发布站

静态 Markdown 内容站（Astro）。当前覆盖 **T0 脚手架 + T1 单篇页 + T2 S1-01 导入**。

## 本地运行

需要 Node.js 22.12 或更高版本。

```sh
npm install
npm run dev
```

`dev` 会在本机启动开发服务器（默认 http://localhost:4321 ）。改 Markdown 或页面后会热更新。

## 静态构建与预览

```sh
npm run build
```

构建产物写到 `dist/`，是纯静态 HTML / CSS / JS，没有服务端接口。

```sh
npm run preview
```

`preview` 只是在本地托管已经生成的 `dist/`，用来检查静态输出，不是 SSR。

## 可点 URL

| URL | 说明 |
| --- | --- |
| `/` | 目录 / 首页，只列出 `status: published` |
| `/posts/s1-01-open-one-ai/` | S1-01 正文（系列徽标、导读、正文、今天就做、下篇预告） |
| `/posts/hello-world/` | T0 夹具；含一张缺失图，用来看占位 |
| `/posts/not-a-real-slug/` | 404：短文案 + 回首页 |
| `/og/s1-01-open-one-ai.png` | S1-01 16:9 OG 封面 |

文章 URL 用文件名当 slug（`s1-01-open-one-ai.md` → `/posts/s1-01-open-one-ai/`）。改 `title` 不会改地址。

## 内容约定

| 路径 | 作用 |
| --- | --- |
| `src/content.config.ts` | posts 集合与 frontmatter schema |
| `src/content/posts/*.md` | 文章 Markdown |
| `src/pages/posts/[slug].astro` | 单篇页 |
| `public/og/` | OG 图 |

Schema 字段：`title`、`description`、`ogImage`、`series`、`episode`、`publishedAt`、`status`；可选 `episodeTotal`、`nextTitle`、`nextHook`、`nextHref`。

`status` 控制是否发布：只有 `published` 会出现在列表，并生成 `/posts/<slug>`；`draft` 不会。

`## 今天就做` 会从正文抽出来，单独做成行动块。下篇预告只走 frontmatter（`nextHref` 默认可写 `#`，不要链到站外未发布的相对 `.md`）。
