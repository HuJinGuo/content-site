---
title: 系统提示词
slug: system-prompt
kind: concept
level: L1
domain: general
summary: 长期有效的角色与规则，适合放拒答和引用格式；不适合放会过期的制度全文。
access: free
node_ids: [l1/system-prompt]
prereqs: [prompt-basics]
next: [refusal]
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

系统提示词在多次用户消息之间保持。适合稳定约束：「只根据摘录回答」「列出块编号」。不适合把整本员工手册贴进去当记忆。

<!-- more -->

读完你能：写出不超过十行的系统提示词，覆盖引用和拒答，并且不包含会过期的数字。

## 定义

对话里优先级较高、相对稳定的说明书。具体字段名因产品而异。

## 类比

岗位手册的「必须 / 禁止」，不是本月通知。

## 反例

把今年差旅标准写进系统提示词，明年标准改了却没人改提示词。

## 来源

OpenAI prompting guide。Last-verified 见页眉。
