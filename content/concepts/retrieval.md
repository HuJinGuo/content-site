---
title: 检索
slug: retrieval
kind: concept
level: L1
domain: general
summary: 按问题找出可能相关的块；这一步错了，后面生成再流畅也是错的。
access: free
node_ids: [l1/retrieval]
prereqs: [embedding]
next: [chunking]
tags: [RAG, 检索]
ai:
  generated: true
  model: grok-4.6
  assist_ratio: 0.65
  reviewed_by: himma
  reviewed_at: 2026-09-15
  factcheck_status: passed
sources:
  - {title: What is RAG, url: https://aws.amazon.com/what-is/retrieval-augmented-generation/, publisher: AWS, date: 2026-09-15, tier: official}
last_verified_at: 2026-09-15
review_by: 2026-12-14
status: published
---

检索是文档问答的骨架。用关键词、向量近邻，或两者混合。目标是把「可能有用的几段」送到窗口里。

<!-- more -->

读完你能：区分检索错和幻觉，并说出一条只改检索就能修好的失败。

## 定义

给定问句，返回 k 个块。k 太小易漏，太大易灌噪声。

## 类比

先抽书再写读后感。抽错书，读后感写得再好也没用。

## 反例

只改提示词「请认真阅读」，却不看取回的块编号。

## 来源

AWS RAG。Last-verified 见页眉。
