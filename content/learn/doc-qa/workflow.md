---
title: 做成工作流：定时更新语料
slug: workflow
kind: unit
level: L4
domain: dev-agent
track: doc-qa
unit_index: 8
summary: 给文档问答加上语料更新节奏：什么时候切块、如何回滚、失败了谁会收到通知。
access: free
node_ids: [doc-qa/07-workflow]
prereqs: [citations-refusals]
next: [when-not-agent]
tags: [doc-qa, 工作流]
ai:
  generated: true
  model: grok-4.6
  assist_ratio: 0.7
  reviewed_by: himma
  reviewed_at: 2026-09-15
  factcheck_status: passed
sources:
  - {title: NIST AI RMF, url: https://www.nist.gov/artificial-intelligence, publisher: NIST, date: 2026-09-15, tier: official}
  - {title: pgvector, url: https://github.com/pgvector/pgvector, publisher: GitHub, date: 2026-09-15, tier: official}
last_verified_at: 2026-09-15
review_by: 2026-12-14
status: published
---

索引不会自己跟上文件夹。有人覆盖了 PDF、有人生效了新通知、有人把草稿丢进了「已发布」目录——这些都该触发更新。工作流是「按时间或事件自动跑的步骤」，不是再雇一个 Agent 去想要不要更新。

<!-- more -->

读完你能：写出语料更新的触发条件、步骤、失败回滚和通知人。

## 成功标准

一份不超过一页的流程：触发 → 同步 → 切块 → 建索引 → 冒烟 5 问 → 发布或回滚。其中「发布」和「回滚」都有可执行命令或按钮名。

## 建议骨架

1. **触发**。每天一次加「源目录变更」。不要只靠有人想起。
2. **同步**。只拉已审核目录。草稿区和回收站排除。
3. **切块与索引**。写入新索引别名，先不要删旧索引。
4. **冒烟**。跑评测表里固定的 5 条（3 命中 2 拒答）。失败则不切换别名。
5. **切换与回滚**。别名切换是发布；保留上一版索引至少一次工作日。

可以用定时脚本、n8n、或你们已有的 CI。工具不重要，别名和冒烟重要。

反例：每次有人喊「搜不到」就手动把整库删了重建，而且没有评测，重建后更糟也没人知道。

## 过时

源文档过复核日，块应带过时标记或退出索引。本站的过时清单是同一思路：过了 Last-verified 的承诺日，就挂条，而不是假装永远正确。

## 练习

把你第 5 课的文件夹接到一条「变更则重建索引」的脚本。故意放进一份空文件，确认冒烟会失败、别名不切。

## 来源

NIST AI RMF 把生命周期和监控写进风险过程。pgvector 索引可重建；发布应用别名或双写是工程习惯，不是该扩展独有的功能。Last-verified 见页眉。

## 小结

更新是产品的一部分。下一课判断要不要在这套管线上再叠 Agent。
