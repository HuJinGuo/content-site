---
title: 材料过期
slug: context-rot
kind: concept
level: L2
domain: general
summary: 索引里还躺着作废通知，回答就会一本正经地错。过期是产品问题，不是文笔问题。
access: free
node_ids: [l2/context-rot]
prereqs: [hallucination]
next: [workflow]
tags: [过时, RAG]
ai:
  generated: true
  model: grok-4.6
  assist_ratio: 0.65
  reviewed_by: himma
  reviewed_at: 2026-09-16
  factcheck_status: passed
sources:
  - {title: NIST AI RMF, url: https://www.nist.gov/artificial-intelligence, publisher: NIST, date: 2026-09-16, tier: official}
  - {title: What is RAG, url: https://aws.amazon.com/what-is/retrieval-augmented-generation/, publisher: AWS, date: 2026-09-16, tier: official}
last_verified_at: 2026-09-16
review_by: 2026-12-15
status: published
---

文档问答最常见的「幻觉」，其实是检索到了去年的红头。Last-verified 和过时清单就是为这件事准备的。

<!-- more -->

读完你能：给自己的一份制度标上生效日，并写出过期后索引里该怎么处理。

## 定义

材料过期：源已失效，块还在被取回。处理：退出索引、挂过时条、或指向替代节点。

## 类比

药盒过期还放在柜台上。

## 反例

只改提示词「请使用最新规定」，却不更新文件夹。

## 来源

NIST 的生命周期与监控。AWS RAG 默认你有可维护的材料源。Last-verified 见页眉。
