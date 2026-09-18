---
title: 一上来就上 Agent
slug: agent-first
kind: pitfall
level: L2
domain: dev-agent
summary: 现象：还没有评测集，就已经让模型改工单。为什么贵、怎么退回。
access: free
node_ids: [l2/agent-first]
prereqs: [when-not-agent]
next: [agent-vs-workflow]
tags: [pitfall, Agent]
ai:
  generated: true
  model: grok-4.6
  assist_ratio: 0.65
  reviewed_by: himma
  reviewed_at: 2026-09-16
  factcheck_status: passed
sources:
  - {title: NIST AI RMF, url: https://www.nist.gov/artificial-intelligence, publisher: NIST, date: 2026-09-16, tier: official}
last_verified_at: 2026-09-16
review_by: 2026-12-15
status: published
---

现象：需求是「内部问答」，方案直接上多步工具调用，还没有 20 道金标问题。

<!-- more -->

读完你能：把这类方案改回「检索问答或固定工作流」，并写出少了哪一张检查单。

## 原因

Agent 听起来像能办事。评测、权限、账单会一起变难。失败时你分不清是检索错还是工具选错。

## 改法

先跑通最小 RAG 和拒答。副作用（改数据、发信）单独做成有鉴权的工作流。

## 何时会再犯

演示日将近，有人说「让它自己想办法」。把演示改成一次带引用的问答。

## 来源

路径课「何时不该上 Agent」。NIST 谈误用与越权。Last-verified 见页眉。
