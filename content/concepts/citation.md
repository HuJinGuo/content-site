---
title: 引用
slug: citation
kind: concept
level: L1
domain: general
summary: 回答时指出用了哪一段原文，让同事能核对，而不是只说「根据内部资料」。
access: free
node_ids: [l1/citation]
prereqs: [retrieval]
next: [citations-refusals]
tags: [引用, doc-qa]
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

引用把生成绑回块。没有引用的内部问答，出了错无法回放。

<!-- more -->

读完你能：在一次回答里要求块编号或标题，并点开核对。

## 定义

可点击或可查找的出处：文件路径、标题、块号。空泛的「据悉」不算。

## 类比

论文脚注。没有脚注的断言，审稿人会退回。

## 反例

模型说「根据员工手册第三章」，手册根本没有第三章。

## 来源

路径课「加引用、拒答、权限和日志」。Last-verified 见页眉。
