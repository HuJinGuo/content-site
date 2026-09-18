---
title: 嵌入
slug: embedding
kind: concept
level: L1
domain: general
summary: 把文本变成可比较的向量；相近意思通常更近，但它不知道对错和权限。
access: free
node_ids: [l1/embedding]
prereqs: [token]
next: [retrieval]
tags: [embedding, RAG]
ai:
  generated: true
  model: grok-4.6
  assist_ratio: 0.65
  reviewed_by: himma
  reviewed_at: 2026-09-15
  factcheck_status: passed
sources:
  - {title: Attention Is All You Need, url: https://arxiv.org/abs/1706.03762, publisher: arXiv, date: 2026-09-15, tier: official}
  - {title: pgvector, url: https://github.com/pgvector/pgvector, publisher: GitHub, date: 2026-09-15, tier: official}
last_verified_at: 2026-09-15
review_by: 2026-12-14
status: published
---

嵌入（embedding）是检索的尺子。问句和文档块都变成向量，再用距离找近邻。

<!-- more -->

读完你能：说明为什么「意思近」不等于「允许你看」，也不等于「这段就是答案」。

## 定义

一个把文本映射到固定长度数字列表的模型。训练目标通常是让相关文本更近。

## 类比

把每本书放到地图上，近的主题聚在一起。地图不会检查借书证。

## 反例

认为向量距离低就可以跳过权限过滤。

## 来源

Transformer 论文给出注意力与表示学习的背景；工程上的嵌入是后续工具。pgvector 用来存这些向量。Last-verified 见页眉。
