---
title: 表格怎么喂给模型
slug: table-with-model
kind: concept
level: L2
domain: office
summary: 先变成「字段：值」的句子或小表，再问能核对的问题；不要把整张表当咒语。
access: free
node_ids: [l2/table-model]
prereqs: [task-brief]
next: [chunking]
tags: [office, 语料]
ai:
  generated: true
  model: grok-4.6
  assist_ratio: 0.65
  reviewed_by: himma
  reviewed_at: 2026-09-16
  factcheck_status: passed
sources:
  - {title: What is RAG, url: https://aws.amazon.com/what-is/retrieval-augmented-generation/, publisher: AWS, date: 2026-09-16, tier: official}
  - {title: OpenAI prompting guide, url: https://platform.openai.com/docs/guides/prompt-engineering, publisher: OpenAI, date: 2026-09-16, tier: official}
last_verified_at: 2026-09-16
review_by: 2026-12-15
status: published
---

宽表、合并单元格、截图里的数字，模型很容易读错列。先清洗，再提问。

<!-- more -->

读完你能：把一张不超过二十行的表改成可读文本，并写出两道能对回单元格的问题。

## 定义

喂表：选有用的列 → 改成文本或 Markdown 表 → 问「这一格是什么」而不是「给洞察」。

## 类比

先把账本抄清楚，再请人算，而不是把拍糊的照片扔过去。

## 反例

一张 80 列导出直接粘贴，问「有没有异常」。

## 来源

RAG 把材料变成可引用的块；同一原则适用于表。Last-verified 见页眉。
