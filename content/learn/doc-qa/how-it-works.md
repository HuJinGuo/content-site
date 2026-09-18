---
title: 文档问答到底怎么工作（直觉版）
slug: how-it-works
kind: unit
level: L1
domain: dev-agent
track: doc-qa
unit_index: 2
summary: 用三步讲清文档问答：问句、检索、生成；并指出每一步会在哪失败。
access: free
node_ids: [doc-qa/01-how]
prereqs: [need-a-kb]
next: [build-vs-buy]
tags: [doc-qa, RAG]
ai:
  generated: true
  model: grok-4.6
  assist_ratio: 0.7
  reviewed_by: himma
  reviewed_at: 2026-09-15
  factcheck_status: passed
sources:
  - {title: What is RAG, url: https://aws.amazon.com/what-is/retrieval-augmented-generation/, publisher: AWS, date: 2026-09-15, tier: official}
  - {title: OpenAI prompting guide, url: https://platform.openai.com/docs/guides/prompt-engineering, publisher: OpenAI, date: 2026-09-15, tier: official}
last_verified_at: 2026-09-15
review_by: 2026-12-14
status: published
---

把文档问答想成开卷考试。学生（模型）可以看书，但书要先被拆成条目、编好目录。提问的人写下问句，系统去目录里找条目，再让学生根据找到的条目写答案。找不到书就应该说「卷子上没有」，而不是编一页看起来像书的文字。

<!-- more -->

读完你能：向没有技术背景的同事画出「问句 → 检索 → 生成」三步，并各举一个失败例子。

## 成功标准

用自己的话讲完三步，听众能复述「检索错了，生成再流畅也是错的」。

## 三步

1. **问句**。用户的问题往往短、含糊、带内部黑话。系统有时会改写问句（加上部门名、时间），这叫查询扩展。改写错了，后面全错。
2. **检索**。把问句变成可比较的形式（常见是嵌入向量），在切好的块里找相近的几段。块切错、权限没过滤、索引过期，都会让「书」变成错的章节。
3. **生成**。模型看到问句和这几段文字，写出回答。它不会自动核对数字；你要在提示词里要求引用，并在证据不足时拒答。

对照：只把 PDF 塞进超长窗口，相当于把整本书摊在桌上，没有目录。材料短、已经圈定范围时可以；材料在变、要计费可控时，目录（检索）更合适。

## 失败长什么样

- 问「报销额度」，检索到了去年作废的通知 → 答案过时。
- 问「合同里违约金」，检索到了另一家客户的合同 → 权限或切块失败。
- 检索空，模型仍写得斩钉截铁 → 缺少拒答。

## 练习

拿一份自己的规章，手写：问句、你认为该命中的段落标题、如果命中失败模型不该说什么。这张纸就是第 6 课评测集的种子。

## 来源

AWS 的 RAG 词条把检索与生成分开写。OpenAI 的提示词指南强调把材料放进上下文，而不是假设模型「记得」你的文档。Last-verified 见页眉。

## 小结

三步里，检索是骨架，生成是文笔。下一课决定买产品还是自建。
