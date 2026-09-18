---
title: Agent 和工作流
slug: agent-vs-workflow
kind: concept
level: L2
domain: dev-agent
summary: 工作流按固定步骤跑；Agent 临时决定下一步。语料更新几乎永远该是工作流。
access: free
node_ids: [l2/agent-vs-workflow]
prereqs: [when-to-use-ai]
next: [when-not-agent]
tags: [Agent, 工作流]
ai:
  generated: true
  model: grok-4.6
  assist_ratio: 0.65
  reviewed_by: himma
  reviewed_at: 2026-09-15
  factcheck_status: passed
sources:
  - {title: NIST AI RMF, url: https://www.nist.gov/artificial-intelligence, publisher: NIST, date: 2026-09-15, tier: official}
last_verified_at: 2026-09-15
review_by: 2026-12-14
status: published
---

两者都能「自动」。差别是谁在运行时做选择。选择越多，评测和权限越难。

<!-- more -->

读完你能：把一个自动化需求标成工作流或 Agent，并给出一条理由。

## 定义

工作流：事先写好的有向步骤。Agent：模型选择工具与次序。

## 类比

地铁线路 vs 出租车司机。

## 反例

用 Agent 每天决定要不要重建索引。

## 来源

路径课「何时不该上 Agent」。Last-verified 见页眉。
