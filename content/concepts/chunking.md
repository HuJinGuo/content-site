---
title: 切块
slug: chunking
kind: concept
level: L1
domain: general
summary: 把长文档切成可检索的片段；大小、重叠和边界决定检索能不能命中。
access: free
node_ids: [l1/chunking]
prereqs: [retrieval]
next: [corpus]
tags: [语料, RAG]
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

切块把章节变成检索单位。按标题切通常优于纯固定字数。重叠用来避免句子在边界上断开。

<!-- more -->

读完你能：为自己的一类文档选出起点（大约 500–1000 字、重叠一两句），并写明要用问句回看。

## 定义

块是带元数据的文本片段：来源、权限、序号、日期。

## 类比

把一本书做成一张张目录卡。卡太大像整章复印，卡太小像把一句话撕成两半。

## 反例

按 200 字硬切法律条文，把「但」和例外切开。

## 来源

见路径课「准备语料」。Last-verified 见页眉。
