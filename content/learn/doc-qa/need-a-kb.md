---
title: 你是不是真的需要一个知识库
slug: need-a-kb
kind: unit
level: L0
domain: dev-agent
track: doc-qa
unit_index: 1
summary: 先判断要不要做内部文档问答：做最小检索、买现成产品，还是先不做。
access: free
node_ids: [doc-qa/00-need-a-kb]
prereqs: []
next: [how-it-works]
tags: [doc-qa, 知识库]
ai:
  generated: true
  model: grok-4.6
  assist_ratio: 0.7
  reviewed_by: himma
  reviewed_at: 2026-09-15
  factcheck_status: passed
sources:
  - {title: What is RAG, url: https://aws.amazon.com/what-is/retrieval-augmented-generation/, publisher: AWS, date: 2026-09-15, tier: official}
  - {title: NIST AI RMF, url: https://www.nist.gov/artificial-intelligence, publisher: NIST, date: 2026-09-15, tier: official}
last_verified_at: 2026-09-15
review_by: 2026-12-14
status: published
---

同事丢给你一句话：「我们要搞个知识库。」这句话里至少混了三件事：把文件找得到、让模型对着文件回答、再让它自己去办事。本课只处理第一层判断——你是不是真的需要一个可检索的文档问答。

<!-- more -->

读完你能：用一张做 / 不做 / 买产品的表，对着自己手头的材料做一次选择，并写出「先不做」时的替代动作。

## 成功标准

拿出三份真实文档（规章、合同摘要或项目说明），写出两个只有这些文档才答得出的问题，和一个公开搜索就能答的问题。若后一种占多数，先不要建库。

## 什么时候值得做

值得做的信号通常一起出现：材料在变、答案必须能引用原文、问的人不是作者本人、答错有代价（对内流程、对客口径）。这时「现查再写」比「把材料塞进聊天窗口」稳。

不值得做的信号也清楚：材料只有一份且一周内不会改；问题其实是开放讨论；没有人维护更新。这时用共享文件夹加目录，或把材料贴进一次对话，成本更低。

## 决策表

| 情况 | 建议 | 下一步 |
|---|---|---|
| 文档少、问的人就是作者 | 先不做 | 把目录写清楚 |
| 文档在变、要引用原文 | 做最小 RAG | 进入本路径第 4–5 课 |
| 只要一个聊天框给全公司 | 先买产品或先不做 | 读「选产品还是自建」 |
| 还想让它改工单、发邮件 | 先不要上 Agent | 读「何时不该上 Agent」 |

类比：知识库像图书馆的索引，不是把馆藏背下来的馆员。反例：把三年聊天记录一股脑导入，却没有权限和评测，看起来「有库」，问一次就胡编。

## 练习

1. 列出你真正会被反复问到的十个问题。
2. 标出哪些必须引用某份内部材料。
3. 若内部材料题少于五道，写下一句「先不做」的理由，发给需求方。

## 来源

AWS 对检索增强生成（RAG）的说明把「先取回再生成」写成默认骨架。NIST AI RMF 把没有根据的生成当作要管理的风险。本课不引用产品评测榜。Last-verified 见页眉。

## 小结

先写决策，再写架构。下一课用直觉版讲清问句如何变成带出处的回答。
