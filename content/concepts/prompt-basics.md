---
title: 提示词基础
slug: prompt-basics
kind: concept
level: L1
domain: general
summary: 把任务、约束、格式说清楚；提示词不是咒语。
access: free
node_ids: [l1/prompt]
prereqs: [context-window]
next: [system-prompt]
tags: [prompt]
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

提示词是给模型的任务说明书：要做什么、不要做什么、输出长什么样。写清楚比堆形容词有用。

<!-- more -->

读完你能：把一件自己的工作改写成五段（立场、任务、约束、输入、格式），并指出哪一段缺了会翻车。

## 定义

最小结构：角色或立场（可选）→ 任务 → 约束 → 输入 → 输出格式。需要事实时，把材料放进窗口或走检索。

## 类比

给外包的 brief，不是咒语书。

## 反例

只写「你是专家，请详细分析」然后期待内部数字正确。

## 来源

OpenAI prompting guide。Last-verified 见页眉。
