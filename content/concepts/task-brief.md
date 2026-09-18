---
title: 给同事的任务说明书
slug: task-brief
kind: concept
level: L1
domain: office
summary: 给模型的 brief 和给同事的 brief 是同一件事：任务、约束、输入、格式。
access: free
node_ids: [l1/task-brief]
prereqs: [prompt-basics]
next: [review-an-answer]
tags: [office, 提示词]
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

办公里最常见的失败不是「模型不够聪明」，是任务没写清。把同一张说明书给人看和给模型看，都能少返工。

<!-- more -->

读完你能：把本周一件事写成四段：要做什么、不要做什么、输入在哪、输出长什么样。

## 定义

任务说明书（brief）：任务 → 约束 → 输入 → 格式。角色可选。数字和制度放进输入，不要写进「你是专家」。

## 类比

外包需求单。没有验收标准就不要开工。

## 反例

只发「帮我优化一下」配一个 40 页 PDF。

## 来源

OpenAI prompting guide 的任务结构。Last-verified 见页眉。
