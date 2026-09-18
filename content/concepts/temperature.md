---
title: 温度
slug: temperature
kind: concept
level: L1
domain: general
summary: 控制生成时抽样有多随机；它不是准确率旋钮，更不能消灭幻觉。
access: free
node_ids: [l1/temperature]
prereqs: [prompt-basics]
next: [hallucination]
tags: [参数]
ai:
  generated: true
  model: grok-4.6
  assist_ratio: 0.65
  reviewed_by: himma
  reviewed_at: 2026-09-15
  factcheck_status: passed
sources:
  - {title: OpenAI prompting guide, url: https://platform.openai.com/docs/guides/prompt-engineering, publisher: OpenAI, date: 2026-09-15, tier: official}
last_verified_at: 2026-09-15
review_by: 2026-12-14
status: published
---

温度低，模型更倾向概率最高的下一个 token；温度高，更常抽出意外的词。事实问答应偏低。

<!-- more -->

读完你能：为自己的「写草稿」和「摘制度」各选一个相对高低，并解释为什么。

## 定义

抽样参数。不同产品还有 top-p 等亲戚，作用类似：管多样性，不管真实性。

## 类比

骰子的偏向。偏向最大面，并不保证那一面写着正确答案。

## 反例

把温度调到 0，以为内部数字就会对。数字对不对看材料在不在窗口里。

## 来源

各家提示与参数文档；本页只讲机制。Last-verified 见页眉。
