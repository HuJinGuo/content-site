---
title: 检索增强生成
slug: rag
kind: concept
level: L1
domain: dev-agent
summary: 先检索再生成。文档问答的最小骨架，不是把整本书塞进窗口。
access: free
node_ids: [l1/rag]
prereqs: [retrieval]
next: [minimal-rag]
tags: [RAG, doc-qa]
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

检索增强生成（RAG）：先取回相关材料，再让模型根据材料写回答。它把「现查」和「现写」分开。

<!-- more -->

读完你能：用三步（问句、检索、生成）向同事解释 RAG，并指出和长上下文的差别。

## 定义

Retrieve，然后 Augment 提示词，然后 Generate。缺检索就只是聊天。

## 类比

开卷考试。

## 反例

把 RAG 当成只要接了向量库就自动正确。

## 来源

AWS: What is RAG。Last-verified 见页眉。
