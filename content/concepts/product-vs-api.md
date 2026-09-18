---
title: 产品 vs API vs 本地模型
slug: product-vs-api
kind: concept
level: L2
domain: general
summary: 聊天产品、调用接口、自己托管推理，三种交付差在数据出域、维护和账单形态。
access: free
node_ids: [l2/product-api-local]
prereqs: [when-to-use-ai]
next: [build-vs-buy]
tags: [选型]
ai:
  generated: true
  model: grok-4.6
  assist_ratio: 0.65
  reviewed_by: himma
  reviewed_at: 2026-09-15
  factcheck_status: passed
sources:
  - {title: What is RAG, url: https://aws.amazon.com/what-is/retrieval-augmented-generation/, publisher: AWS, date: 2026-09-15, tier: official}
last_verified_at: 2026-09-15
review_by: 2026-12-14
status: published
---

产品给你界面和同步；API 让你把检索留在自己这边；本地模型把推理放在自己的机器。没有普遍更优，只有约束不同。

<!-- more -->

读完你能：按「能否出域 / 谁维护评测 / 调用量级」三问给自己的场景选一类。

## 定义

产品 = 别人的应用。API = 别人的模型，你的编排。本地 = 你的模型进程。

## 类比

食堂、买半成品回家炒、自己种菜。都能吃饭，卫生责任不同。

## 反例

文档不能出域却用个人账号把原文贴进消费级聊天产品。

## 来源

路径课「选产品还是自建」。Last-verified 见页眉。
