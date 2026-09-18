---
title: pgvector 仍是 Postgres 上常用的向量扩展之一
slug: news-pgvector
kind: news
level: L1
domain: general
summary: 已有 PostgreSQL 时，用扩展存嵌入是最小 RAG 的常见选项，不是唯一选项。
access: free
node_ids: []
prereqs: []
next: []
tags: [pgvector, RAG, milestone]
ai:
  generated: true
  model: grok-4.6
  assist_ratio: 0.8
  reviewed_by: himma
  reviewed_at: 2026-09-15
  factcheck_status: passed
sources:
  - {title: pgvector, url: https://github.com/pgvector/pgvector, publisher: GitHub, date: 2026-09-15, tier: official}
  - {title: What is RAG, url: https://aws.amazon.com/what-is/retrieval-augmented-generation/, publisher: AWS, date: 2026-09-15, tier: official}
last_verified_at: 2026-09-15
review_by: 2026-12-14
status: published
---

pgvector 在 Postgres 里提供向量类型和相似度检索。适合已经把业务数据放在 Postgres、不想先上独立向量云的团队。索引参数变化会让旧教程里的数字失效，要以仓库说明为准。

<!-- more -->

对谁有用：走「自建最小 RAG」分支的人。相关实体页：pgvector。来源：项目仓库。
