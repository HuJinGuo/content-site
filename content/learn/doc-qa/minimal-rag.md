---
title: 最小 RAG：从文件夹到能提问
slug: minimal-rag
kind: unit
level: L3
domain: dev-agent
track: doc-qa
unit_index: 5
summary: 用一个本地文件夹搭最小可用的检索问答，理解每一步在做什么。
access: free
node_ids: [doc-qa/04-minimal-rag]
prereqs: [corpus, context-window]
next: [eval]
tags: [doc-qa, RAG]
ai:
  generated: true
  model: grok-4.6
  assist_ratio: 0.7
  reviewed_by: himma
  reviewed_at: 2026-09-15
  factcheck_status: passed
sources:
  - {title: What is RAG, url: https://aws.amazon.com/what-is/retrieval-augmented-generation/, publisher: AWS, date: 2026-09-15, tier: official}
  - {title: pgvector, url: https://github.com/pgvector/pgvector, publisher: GitHub, date: 2026-09-15, tier: official}
  - {title: OpenAI tokenizer, url: https://platform.openai.com/tokenizer, publisher: OpenAI, date: 2026-09-15, tier: official}
last_verified_at: 2026-09-15
review_by: 2026-12-14
status: published
---

RAG 把「现查」和「现写」分开。本课只要求：一个文件夹、一种切块、一种检索、一次能回答的提问。不引入 Agent、不引入多路工具、不引入微调。

<!-- more -->

读完你能：在本机用三份文档提出一个只有这些文档才答得出的问题，并看到系统引用了正确的块。

## 成功标准

用自己的三份文档，提出一个只有这些文档才答得出的问题，系统引用了正确的块。再提一个文档里没有的问题，系统拒绝编造或明确说找不到。

## 步骤（每步可验证）

1. **文件夹**。只放清洗过的文本或 Markdown。成功：`ls` 能列出三份，且每份能被 UTF-8 读出。
2. **切块**。按标题切，记录 `source` 与序号。成功：打印前五个块，人工能读懂，没有把表格切成乱码。
3. **嵌入与索引**。用你选的模型把块变成向量；本地可用 Postgres + pgvector，或任何你能导出距离的库。成功：用一句几乎等于某块原文的话查询，最近邻就是那一块。
4. **提问**。把问句嵌入，取回 k 块（先从 k=4 试），拼进提示词：「只根据下列摘录回答；摘录不够就说不知道；回答末尾列出用到的块编号。」成功：命中题能引用，缺文档题不胡编。

常见失败：PDF 没抽干净导致块是空的；k 太大把无关章节灌进窗口；提示词没要求引用，你以为它「懂了」。

## 不要在这一课做的事

不要接工单系统、不要让模型自己决定再搜一次、不要为了演示换更大窗口。那些会让你分不清是检索赢了还是碰巧蒙对。

## 练习

把成功标准的那次提问截图或日志留下来（问句、取回的块编号、回答）。这是第 6 课评测的第一条。

## 来源

AWS 对 RAG 的定义。pgvector 作为在 Postgres 上存向量的一种实现。OpenAI tokenizer 用来估窗口有没有被块撑满。Last-verified 见页眉。

## 小结

最小项目跑通之后，立刻进入评测，而不是加功能。
