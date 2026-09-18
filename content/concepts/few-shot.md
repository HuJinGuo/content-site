---
title: 少样本
slug: few-shot
kind: concept
level: L1
domain: general
summary: 在提示词里放两三个例子，比堆「专业、详细」更能稳住格式。
access: free
node_ids: [l1/few-shot]
prereqs: [prompt-basics]
next: [system-prompt]
tags: [prompt]
ai:
  generated: true
  model: grok-4.6
  assist_ratio: 0.65
  reviewed_by: himma
  reviewed_at: 2026-09-16
  factcheck_status: passed
sources:
  - {title: OpenAI prompting guide, url: https://platform.openai.com/docs/guides/prompt-engineering, publisher: OpenAI, date: 2026-09-16, tier: official}
last_verified_at: 2026-09-16
review_by: 2026-12-15
status: published
---

少样本（few-shot）：给你要的输入和输出各举两三个真例子。模型会跟格式走。

<!-- more -->

读完你能：为自己的一种周报格式写两个正例和一个反例。

## 定义

例子要真实、短、含你在意的约束（比如「没有出处就写未知」）。不要只写形容词。

## 类比

给新人看两份合格纪要，比讲一小时「要专业」有用。

## 反例

十个互相矛盾的例子，再抱怨模型不稳定。

## 来源

OpenAI prompting guide。Last-verified 见页眉。
