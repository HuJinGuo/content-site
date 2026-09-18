---
title: 验收一次回答
slug: review-an-answer
kind: concept
level: L1
domain: office
summary: 生成只是草稿。核对出处、数字和能不能执行，才算读完。
access: free
node_ids: [l1/review-answer]
prereqs: [prompt-basics]
next: [hallucination]
tags: [验收, office]
ai:
  generated: true
  model: grok-4.6
  assist_ratio: 0.65
  reviewed_by: himma
  reviewed_at: 2026-09-16
  factcheck_status: passed
sources:
  - {title: NIST AI RMF, url: https://www.nist.gov/artificial-intelligence, publisher: NIST, date: 2026-09-16, tier: official}
  - {title: OpenAI prompting guide, url: https://platform.openai.com/docs/guides/prompt-engineering, publisher: OpenAI, date: 2026-09-16, tier: official}
last_verified_at: 2026-09-16
review_by: 2026-12-15
status: published
---

模型会写得很顺。顺不等于对。验收是给「这一次回答」设三个检查点，而不是上一个评分系统。

<!-- more -->

读完你能：对同事贴来的一段生成文字，标出要核对的句子，并决定采用、改写还是扔掉。

## 定义

验收 = 出处（这句话从哪来）+ 数字（能否对上原文或计算器）+ 可执行（下一步谁来做）。缺一项就当草稿。

## 类比

编辑看初稿，不是老师打分。没有排名，只有能不能发出去。

## 反例

把聊天记录转发到群里当制度解释，没有人点开原文。

## 来源

NIST 把不可靠输出放进风险管理。提示词指南要求把材料放进上下文。Last-verified 见页眉。
