---
title: AI 和搜索差在哪
slug: ai-vs-search
kind: concept
level: L0
domain: general
summary: 搜索返回链接和摘录；对话模型返回一段连续的话。要出处时，两者得一起用。
access: free
node_ids: [l0/ai-vs-search]
prereqs: [what-is-llm]
next: [when-to-use-ai]
tags: [搜索]
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

搜索把查询对到网页或文档列表。对话模型把查询对到一段生成的句子。前者难在排序，后者难在是否有根据。

<!-- more -->

读完你能：说明什么时候该点开链接核对，什么时候生成文本只是草稿。

## 定义

搜索：检索。生成：补全。文档问答把两者串起来，所以叫检索增强生成。

## 类比

图书馆目录卡 vs 让人根据目录卡写摘要。摘要写得再顺，也要能指回那张卡。

## 反例

只用聊天框问「我们公司差旅标准」，既没有搜索内部站，也没有把制度贴进去。

## 来源

AWS 对 RAG 的说明。Last-verified 见页眉。
