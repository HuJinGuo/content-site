---
title: 加引用、拒答、权限和日志
slug: citations-refusals
kind: unit
level: L6
domain: dev-agent
track: doc-qa
unit_index: 7
summary: 把最小 RAG 补成可上线：回答带出处、证据不足就拒答、检索按权限、关键操作留日志。
access: free
node_ids: [doc-qa/06-citations]
prereqs: [eval]
next: [workflow]
tags: [doc-qa, 上线]
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

能提问还不够。交给别人用之前，回答必须能被核对，找不到时必须停，不该看见的文档不能进检索，出了问题要能回放。这四件事构成上线检查单的核心。

<!-- more -->

读完你能：对照检查单决定「能否把系统交给同事用」，并指出还缺哪一条。

## 成功标准

检查单上引用、拒答、权限、日志四项都有「如何验证」的一句话。任意一项只能靠「我们相信模型」通过，则不能上线。

## 引用

提示词要求列出块编号或原文标题；界面把编号链回块。抽查：命中题的引用能点开，且人能看出依据。不要接受「根据内部资料」这种空引用。

## 拒答

检索分数低或人工规则判定「没有足够摘录」时，固定回复模板：「根据现有文档找不到。你可以补充哪份材料。」把拒答算进评测，而不是当失败隐瞒。

## 权限

在取回块之前过滤。测试账号只能命中自己组的文档。把一份不该看见的薪资表放进库，用普通账号问「平均工资」，期望是检索为空或拒答，而不是一个被打码的数字——打码也是一种泄露形态。

## 日志

至少记录：谁在何时问了什么（问句可做哈希或截断）、取回了哪些块编号、是否拒答、用的提示词版本。不要把完整文档和密钥写进日志。日志是为了回放事故，不是为了再训练。

## 上线检查单（首个资源包的文字版）

- [ ] 20 条评测表有最近一次日期
- [ ] 命中题带可点击引用
- [ ] 缺文档题走拒答模板
- [ ] 跨权限题不召回
- [ ] 能根据日志复现一次回答
- [ ] 过复核日的源文档会退出或标记

## 来源

NIST AI RMF 强调治理、可追溯与风险。AWS RAG 词条默认生成应依据取回内容。Last-verified 见页眉。

## 小结

四项里缺权限，其他三项都会变成事故报告。下一课把语料更新做成工作流。
