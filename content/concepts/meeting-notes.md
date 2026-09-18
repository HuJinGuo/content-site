---
title: 会议纪要怎么用模型
slug: meeting-notes
kind: concept
level: L1
domain: office
summary: 纪要适合归纳待办和分歧；不适合当未出席者的唯一事实来源。
access: free
node_ids: [l1/meeting-notes]
prereqs: [task-brief]
next: [review-an-answer]
tags: [office]
ai:
  generated: true
  model: grok-4.6
  assist_ratio: 0.65
  reviewed_by: himma
  reviewed_at: 2026-09-16
  factcheck_status: passed
sources:
  - {title: OpenAI prompting guide, url: https://platform.openai.com/docs/guides/prompt-engineering, publisher: OpenAI, date: 2026-09-16, tier: official}
  - {title: NIST AI RMF, url: https://www.nist.gov/artificial-intelligence, publisher: NIST, date: 2026-09-16, tier: official}
last_verified_at: 2026-09-16
review_by: 2026-12-15
status: published
---

录音转写再让模型出纪要，能省时间。风险是：它会补全没说出口的结论，听起来像会上拍板了。

<!-- more -->

读完你能：给纪要模板加上「待确认」栏，并规定数字必须能对上转写。

## 定义

纪要任务：待办（谁、何时）、未决分歧、引用原话。不要让模型写「会议认为」。

## 类比

速记员可以整理句子，不能代替主席宣布决议。

## 反例

把生成的「全员同意下周上线」发到全公司，而转写里根本没有这句话。

## 来源

提示词写清格式；NIST 提醒误用。Last-verified 见页眉。
