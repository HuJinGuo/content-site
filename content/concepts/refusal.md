---
title: 拒答
slug: refusal
kind: concept
level: L1
domain: general
summary: 证据不足时明确说不知道；在内部问答里，拒答往往比流畅的错答更值钱。
access: free
node_ids: [l1/refusal]
prereqs: [hallucination]
next: [citations-refusals]
tags: [拒答]
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

拒答是产品规则。模型默认会补全；你要在检索空、分数低或权限不足时换成固定句子。

<!-- more -->

读完你能：写出一句拒答模板，并把它算进评测表，而不是当失败隐瞒。

## 定义

系统选择不提供实质性答案，并说明原因类型：找不到、无权、材料过时。

## 类比

柜员说「系统里没有这笔」，而不是随口编一个余额。

## 反例

为了演示「什么都能答」，关掉拒答。

## 来源

NIST 将不可靠输出视为要管理的风险。Last-verified 见页眉。
