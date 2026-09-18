---
title: 检索增强生成仍把「先检索再生成」当骨架
slug: news-rag-definition
kind: news
level: L1
domain: general
summary: AWS 对 RAG 的公开说明仍把取回材料与生成分开。对文档问答选型有用。
access: free
node_ids: []
prereqs: []
next: []
tags: [RAG, milestone, doc-qa]
ai:
  generated: true
  model: grok-4.6
  assist_ratio: 0.8
  reviewed_by: himma
  reviewed_at: 2026-09-15
  factcheck_status: passed
sources:
  - {title: What is RAG, url: https://aws.amazon.com/what-is/retrieval-augmented-generation/, publisher: AWS, date: 2026-09-15, tier: official}
  - {title: NIST AI RMF, url: https://www.nist.gov/artificial-intelligence, publisher: NIST, date: 2026-09-15, tier: official}
last_verified_at: 2026-09-15
review_by: 2026-12-14
status: published
---

截至 2026-09-15，AWS 对 retrieval-augmented generation 的说明仍把流程写成：先取回，再生成。这不是某一家聊天产品的广告词，而是把「现查」和「现写」分开的工程描述。

<!-- more -->

对谁有用：正在做内部文档问答、纠结要不要上超长窗口的人。相关概念卡：检索增强生成、上下文窗口。双源：AWS 词条 + 本站路径课对同一骨架的用法。
