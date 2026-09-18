---
title: 上下文窗口
slug: context-window
kind: concept
level: L1
domain: general
summary: 模型一次能「看见」多少字；更长不一定更好，账单和注意力都会变。
access: free
node_ids: [l1/context-window]
prereqs: [token]
next: [hallucination]
tags: [context, token]
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

模型并不是把整本书「记住」，而是每次生成时把一段有上限的文本放进窗口。超过上限的部分要么截断，要么被检索系统另外处理。

<!-- more -->

读完你能：指出自己常用产品的窗口数量级，并说出一个「更长反而更差」的例子。

## 定义

窗口以 token 计。问句、系统提示词、检索块、对话历史，都占同一笔预算。

## 类比

书桌大小。桌子更大，可以摊更多纸；并不保证你能找到正确那一页。

## 反例

把整个网盘塞进 1M 窗口，又没有目录，还为噪声里的一句错误数字签字。

## 来源

OpenAI tokenizer 用来感受 token 数量级。各家窗口数字以官方文档为准，本页不抄会过期的营销表。Last-verified 见页眉。
