---
title: 选产品还是自建，选哪家模型
slug: build-vs-buy
kind: unit
level: L2
domain: dev-agent
track: doc-qa
unit_index: 3
summary: 用决策树在产品、自建 API、本地模型之间选择，并估得出数量级月费。
access: free
node_ids: [doc-qa/02-build-vs-buy]
prereqs: [how-it-works]
next: [corpus]
tags: [doc-qa, 选型]
ai:
  generated: true
  model: grok-4.6
  assist_ratio: 0.7
  reviewed_by: himma
  reviewed_at: 2026-09-15
  factcheck_status: passed
sources:
  - {title: OpenAI tokenizer, url: https://platform.openai.com/tokenizer, publisher: OpenAI, date: 2026-09-15, tier: official}
  - {title: pgvector, url: https://github.com/pgvector/pgvector, publisher: GitHub, date: 2026-09-15, tier: official}
  - {title: What is RAG, url: https://aws.amazon.com/what-is/retrieval-augmented-generation/, publisher: AWS, date: 2026-09-15, tier: official}
last_verified_at: 2026-09-15
review_by: 2026-12-14
status: published
---

选型不是选「听起来更聪明的名字」，是选谁来维护切块、权限、评测和账单。产品替你包了界面和同步；自建 API 让你把检索留在自己的库；本地模型把推理放在自己的机器上。三者都能做文档问答，失败模式不同。

<!-- more -->

读完你能：画出一棵不超过两层的决策树，并给自己的场景填一笔数量级月费（不必精确到分）。

## 成功标准

书面回答三个问题：数据能否出域、谁来写评测集、月调用大概是百次还是万次。每个问题都有对应选项。

## 决策树

1. 文档不能出你的机器 → 倾向本地或专有云，而不是把原文贴到消费级聊天产品。
2. 没有人能写 20 道金标问题 → 先不要自建，产品也未必救得了你；回去补第 1 课的决策表。
3. 问的人少于十个、文档少于一百份 → 现成产品或最小自建都够；不要先上多 Agent。
4. 已有 PostgreSQL，愿意维护一行扩展 → 自建最小 RAG 合理，pgvector 是常见选项之一。

模型怎么选：先定「要不要出域」和「要不要引用」，再比单价。单价看输入 / 输出是否分开、有没有缓存折扣。窗口更大不自动等于检索更好，见概念卡「上下文窗口」。

## 月费怎么估

粗算：每月问题数 ×（问句 token + 检索块 token + 回答 token）× 单价。中文可按 1–2 字约 1–2 个 token 估数量级，用公开分词器抽查一篇，不要发明精确换算。存储和人工评测往往比推理费更先见顶。

反例：只比较「哪家模型更强」的演示视频，却没有把权限和评测写进合同或自己的检查单。

## 练习

用自己团队上月「被反复问到的内部问题」次数，估一笔月费区间（低 / 中 / 高三档即可）。把假设写在旁边，方便以后改。

## 来源

OpenAI tokenizer 用来感受数量级。pgvector 文档说明可以在现有 Postgres 上存向量。AWS 的 RAG 说明适合作为「产品也在做同一件事」的对照。Last-verified 见页眉。

## 小结

先约束，再模型。下一课准备语料：切分、清洗、权限。
