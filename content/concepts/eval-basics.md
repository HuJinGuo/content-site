---
title: 评测入门
slug: eval-basics
kind: concept
level: L1
domain: general
summary: 用事先写好的问句和可观察的期望，代替「感觉还行」。
access: free
node_ids: [l1/eval-basics]
prereqs: [retrieval]
next: [eval]
tags: [评测]
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

评测集是文档问答的出厂抽检。没有它，每次改切块都是盲飞。

<!-- more -->

读完你能：写出五条带期望的问题（命中或拒答），并说明谁来打分。

## 定义

金标 = 问句 + 可观察期望（该引用哪块，或该拒答）。另一人能独立判定。

## 类比

听力考试有标准答案。老师不能当场改题来迁就设备。

## 反例

只保留会做的三问当「回归」。

## 来源

路径课「为什么它会答错」。NIST 谈测量与评价。Last-verified 见页眉。
