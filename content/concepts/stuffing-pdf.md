---
title: 把整份 PDF 塞进去
slug: stuffing-pdf
kind: pitfall
level: L2
domain: dev-agent
summary: 现象：窗口很大，答案却引用了目录页。原因和改法。
access: free
node_ids: [l2/stuffing-pdf]
prereqs: [context-window]
next: [chunking]
tags: [pitfall, RAG]
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

现象：把 120 页 PDF 一次性贴进对话，问一个数字，得到一个自信的错误答案。

<!-- more -->

读完你能：说出何时该检索切块、何时可以把已经圈定的十页塞进窗口。

## 原因

窗口里噪声太多，模型仍会补全。目录、页眉、另一章的表，都会变成「看起来相关」。

## 改法

先切块再问；或先人工圈定章节再贴。问句里写「只根据第 4 节」。

## 何时会再犯

新窗口数字又涨一档，就会有人说「那就整本塞进去」。更长不等于目录更好。

## 来源

AWS RAG；上下文窗口概念卡。Last-verified 见页眉。
