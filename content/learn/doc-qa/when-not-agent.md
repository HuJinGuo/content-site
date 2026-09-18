---
title: 何时不该上 Agent
slug: when-not-agent
kind: unit
level: L4
domain: dev-agent
track: doc-qa
unit_index: 9
summary: 用判断清单决定停留在检索问答，还是再加工具调用和多步 Agent。
access: free
node_ids: [doc-qa/08-when-not-agent]
prereqs: [workflow]
next: [principles]
tags: [doc-qa, Agent]
ai:
  generated: true
  model: grok-4.6
  assist_ratio: 0.7
  reviewed_by: himma
  reviewed_at: 2026-09-15
  factcheck_status: passed
sources:
  - {title: NIST AI RMF, url: https://www.nist.gov/artificial-intelligence, publisher: NIST, date: 2026-09-15, tier: official}
  - {title: OpenAI prompting guide, url: https://platform.openai.com/docs/guides/prompt-engineering, publisher: OpenAI, date: 2026-09-15, tier: official}
last_verified_at: 2026-09-15
review_by: 2026-12-14
status: published
---

Agent 在本站的用法：能选工具、多步执行的程序。它比单次文档问答更能「办事」，也更贵、更难评测、更容易在权限上翻车。默认停留在「问一句、引用一段、答一句」。

<!-- more -->

读完你能：用清单对一个真实需求打分，写出「上 Agent」或「不上」的理由，而不是感觉。

## 成功标准

针对自己的需求填写清单。若「需要多步副作用」为否，结论必须是不上 Agent，除非你另写了一段可验收的例外。

## 判断清单

| 问题 | 是 → | 否 → |
|---|---|---|
| 用户只要找到原文并解释 | 文档问答 | 可能需要工具 |
| 需要改工单 / 发邮件 / 动数据库 | 才考虑 Agent | 不要上 |
| 每一步能单独评测 | 可以设计工具 | 先拆成工作流 |
| 工具有鉴权与日志 | 可试点 | 先补第 7 课 |
| 失败可以人工接管 | 可试点 | 不要无人值守 |

工作流（第 8 课）按固定步骤跑；Agent 临时决定下一步。语料更新几乎永远该是工作流。只有路径事先写不完、且每步都有工具契约时，才值得让模型选工具。

类比：自动门是工作流，前台助理是 Agent。反例：为了「显得智能」，让模型自己决定要不要删除索引。

## 成本

每多一步，就多一次模型调用、一次工具风险、一次评测维度。账单和时间都会升。若你的评测集还没有 20 条，Agent 只会让你更不知道错在哪。

## 练习

把需求方口头说的「智能助手」拆成：问答、检索、改数据、通知人。后两项若存在，单独写成工具接口草案，仍然先不要接模型。

## 来源

NIST AI RMF 把误用和越权当作要管理的风险。OpenAI 的提示词指南处理的是单次任务说明书，并不等于多步代理。Last-verified 见页眉。

## 小结

能用检索问答结束的需求，不要升级。下一课回看检索、嵌入和幻觉从哪来。
