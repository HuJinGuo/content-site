---
title: 为什么它会答错，怎样评测
slug: eval
kind: unit
level: L4
domain: dev-agent
track: doc-qa
unit_index: 6
summary: 为文档问答写出金标问题，区分检索错、胡编和该拒答，而不是只看感觉。
access: free
node_ids: [doc-qa/05-eval]
prereqs: [minimal-rag]
next: [citations-refusals]
tags: [doc-qa, 评测]
ai:
  generated: true
  model: grok-4.6
  assist_ratio: 0.7
  reviewed_by: himma
  reviewed_at: 2026-09-15
  factcheck_status: passed
sources:
  - {title: NIST AI RMF, url: https://www.nist.gov/artificial-intelligence, publisher: NIST, date: 2026-09-15, tier: official}
  - {title: What is RAG, url: https://aws.amazon.com/what-is/retrieval-augmented-generation/, publisher: AWS, date: 2026-09-15, tier: official}
last_verified_at: 2026-09-15
review_by: 2026-12-14
status: published
---

答错通常不是「模型不够聪明」。更常见的是：检索拿错了段、切块切断了数字、过期文件还在索引里、或者检索为空时模型不肯认输。不写评测集，你只能靠演示的那三问过日子。

<!-- more -->

读完你能：写出不少于 20 条金标问题，并用一张表记下命中、拒答、胡编。

## 成功标准

20 条问题里至少含：10 条应命中（能指出该引用哪一块）、5 条应拒答（库里没有）、3 条易混淆（两份相似文档）、2 条过时文档题（如果有旧版）。跑一遍最小系统，填表，而不是只写「还行」。

## 评分表

| 问句 | 期望 | 实际检索块 | 回答 | 判定 |
|---|---|---|---|---|
| … | 引用块 A | | | 命中 / 检索错 / 胡编 / 误拒 |

判定要互斥：检索就错了，不要把锅记在「幻觉」上；检索对了却编造数字，才记胡编。误拒是库里有答案却说不知道，也要记账，否则以后会为了召回把拒答拆掉。

## 为什么 20 条

少于这个数，你很容易只挑会做的题。20 不是统计学魔法，是能在一小时内人工看完、又不容易自欺的下限。金标必须可观察：另一人能根据「该引用哪一段」独立打分。

类比：出厂抽检。反例：每次改提示词只拿同一句「你们年假几天」演示。

## 练习

把第 2 课手写的那张纸扩成 20 条。找一个没写过这些文档的人抽 5 条盲测。意见不一致的题目，改金标，不要改成「都算对」。

## 来源

NIST AI RMF 把测量与评价当作风险管理的一部分。AWS 的 RAG 说明没有代替你写测试集。本课的表是编辑部的工作表，不是学术基准。Last-verified 见页眉。

## 小结

先有表，再改切块或模型。下一课加上引用、拒答、权限和日志，才能交给别人用。
