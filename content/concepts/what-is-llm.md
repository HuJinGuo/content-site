---
title: 什么是大语言模型
slug: what-is-llm
kind: concept
level: L0
domain: general
summary: 它是预测下文的模型，不是装了全世界的数据库，也不是会负责的同事。
access: free
node_ids: [l0/what-is-llm]
prereqs: []
next: [ai-vs-search]
tags: [LLM]
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

大语言模型（LLM）在一次对话里看起来像会聊天的人。机制上，它根据已经出现的 token 预测后面可能出现的 token。流畅不等于知情，更不等于已核对。

<!-- more -->

读完你能：用「预测下文」解释为什么它能写邮件，也能编一个不存在的条款。

## 定义

输入一段文本（提示词、对话、检索到的块），输出继续写下去的文本。训练数据里见过很多人类写作，所以格式像人。

## 类比

很会接话的同事，但没有你们公司的网盘权限，除非你把文件贴给他或先检索。

## 反例

把它当成「已经读过我昨天上传的合同」。没有检索或粘贴，它没有读过。

## 来源

公开的提示词指南把模型当完成任务的系统，要求你把材料和约束写清楚。Last-verified 见页眉。
