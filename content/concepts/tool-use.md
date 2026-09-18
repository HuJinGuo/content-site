---
title: 工具调用
slug: tool-use
kind: concept
level: L2
domain: dev-agent
summary: 模型请求执行外部函数：查库、算数、发请求。要鉴权、限权和日志。
access: free
node_ids: [l2/tool-use]
prereqs: [agent-vs-workflow]
next: [when-not-agent]
tags: [工具, Agent]
ai:
  generated: true
  model: grok-4.6
  assist_ratio: 0.65
  reviewed_by: himma
  reviewed_at: 2026-09-15
  factcheck_status: passed
sources:
  - {title: OpenAI prompting guide, url: https://platform.openai.com/docs/guides/prompt-engineering, publisher: OpenAI, date: 2026-09-15, tier: official}
  - {title: NIST AI RMF, url: https://www.nist.gov/artificial-intelligence, publisher: NIST, date: 2026-09-15, tier: official}
last_verified_at: 2026-09-15
review_by: 2026-12-14
status: published
---

工具调用让模型停下来，由程序执行函数，再把结果送回窗口。这是 Agent 的零件，也可以在单步问答里谨慎使用。

<!-- more -->

读完你能：给一个「查库存」工具写出参数、权限和失败返回，而不是让模型直接「保证有货」。

## 定义

模型输出结构化的调用意图；运行时执行；结果成为新的上下文。

## 类比

让助理打电话问仓库，而不是让助理假装自己去过仓库。

## 反例

给模型一个没有鉴权的删除接口。

## 来源

提示词指南里的工具 / 函数调用章节因产品而异；原则是副作用必须可审计。NIST 谈误用。Last-verified 见页眉。
