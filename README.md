# 内容发布站

静态 Markdown 内容站（Astro）。当前是 **T0 脚手架**：已接好 posts 内容集合和 `/posts/[slug]` 路由占位。完整文章页是 T1，S1-01 正文导入是 T2，都还不在这里。

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

## 内容约定（T0）

| 路径 | 作用 |
| --- | --- |
| `src/content.config.ts` | posts 集合与 frontmatter schema |
| `src/content/posts/*.md` | 文章 Markdown |
| `src/pages/posts/[slug].astro` | 单篇路由占位（目前只渲染标题） |

Schema 字段：`title`、`description`、`ogImage`、`series`、`episode`、`publishedAt`、`status`。

`status` 控制是否发布：只有 `published` 会出现在列表，并生成 `/posts/<slug>`；`draft` 不会。
