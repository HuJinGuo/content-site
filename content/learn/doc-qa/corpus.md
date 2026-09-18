---
title: 准备语料：切分、清洗、权限
slug: corpus
kind: unit
level: L3
domain: dev-agent
track: doc-qa
unit_index: 4
summary: 把文档变成可检索的块：切多大、怎么重叠、谁能看见、哪些段落必须扔掉。
access: free
node_ids: [doc-qa/03-corpus]
prereqs: [build-vs-buy]
next: [minimal-rag]
tags: [doc-qa, 语料]
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

语料不是「把网盘挂上」。扫描件里的页眉页脚、已作废的红头、别人不该看见的薪资表，都会变成检索噪声或事故。这一课把文件夹变成一块块能被引用的文字，并写清权限。

<!-- more -->

读完你能：为一叠真实文档写出切块大小、重叠、清洗规则和「不能进索引」的名单。

## 成功标准

拿出不少于二十个块的样例表：每个块有来源路径、标题、权限标签、字符数。其中至少三块被标为「不进索引」，并写了原因。

## 切分

按标题和段落切，比按固定字数硬切更不容易把「不得低于」和后面的数字切开。固定长度仍然有用，尤其是没有标题的纯文本。常见起点：大约 500–1000 字一块，相邻块重叠一两句。这是起点，不是标准；要用第 6 课的问句来回看。

块太大：检索到了，但模型要在噪声里找一句。块太小：问「这一章的例外」时，例外写在下一块。重叠就是为这种情况准备的。

## 清洗

去掉重复页眉、目录页、扫描噪点。把表格变成「字段：值」的句子，模型更吃得下。版本号和生效日期写进块的元数据，不要只写在文件名里。

## 权限

检索阶段就要过滤。提示词里写「不要泄露」挡不住相近向量把薪资表召回来。最小做法：每块带 `group` 或 `owner`，查询时只在调用者可见的集合里搜。做不到这一点，就不要把那份文档放进库。

类比：图书馆不是把所有书堆在大厅；有些在闭架，借书证不同。反例：用全员可读的聊天机器人接人事文件夹。

## 练习

选三份敏感程度不同的文档，写出「进索引 / 进摘要 / 不进库」三种处置。把规则贴到仓库 README，而不是只放在某个人的脑子里。

## 来源

NIST AI RMF 把权限、数据治理和风险放在同一套管理语言里。AWS 的 RAG 说明默认你已经有可检索的材料来源。Last-verified 见页眉。

## 小结

语料规范先于模型。下一课用一个本地文件夹把最小 RAG 跑通。
