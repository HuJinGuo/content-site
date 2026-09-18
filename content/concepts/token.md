---
title: Token
slug: token
kind: concept
level: L1
domain: general
summary: 模型计费和窗口大小的基本单位；中文大约怎么估。
access: free
node_ids: [l1/token]
prereqs: []
next: [context-window]
tags: [token, context]
ai:
  generated: true
  model: grok-4.6
  assist_ratio: 0.65
  reviewed_by: himma
  reviewed_at: 2026-09-15
  factcheck_status: passed
sources:
  - {title: OpenAI tokenizer, url: https://platform.openai.com/tokenizer, publisher: OpenAI, date: 2026-09-15, tier: official}
last_verified_at: 2026-09-15
review_by: 2026-12-14
status: published
---

Token 不是「一个汉字」也不是「一个英文单词」。它是分词器切出来的片段。窗口和账单都按它算。

<!-- more -->

读完你能：把一篇自己的文档估一个数量级，而不是报一个精确数字。

## 定义

分词器把文本切成词表里的编号。不同产品词表不同，所以不能用别家的「一字一 token」去结算另一家的账单。

## 类比

超市按重量，但各店秤的刻度略有差别。要比价，先看是按输入、输出还是缓存计价。

## 反例

用英文单词数乘 0.75 去报中文项目的预算，还不写假设。

## 来源

OpenAI tokenizer。Last-verified 见页眉。
