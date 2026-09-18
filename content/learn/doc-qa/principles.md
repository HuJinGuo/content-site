---
title: 原理回看：检索、嵌入、幻觉从哪来
slug: principles
kind: unit
level: L7
domain: dev-agent
track: doc-qa
unit_index: 10
summary: 把路径里用到的检索、嵌入、窗口和幻觉对回公开文献里的基本机制。
access: free
node_ids: [doc-qa/09-principles]
prereqs: [when-not-agent, hallucination, embedding]
next: []
tags: [doc-qa, 原理]
ai:
  generated: true
  model: grok-4.6
  assist_ratio: 0.7
  reviewed_by: himma
  reviewed_at: 2026-09-15
  factcheck_status: passed
sources:
  - {title: Attention Is All You Need, url: https://arxiv.org/abs/1706.03762, publisher: arXiv, date: 2026-09-15, tier: official}
  - {title: What is RAG, url: https://aws.amazon.com/what-is/retrieval-augmented-generation/, publisher: AWS, date: 2026-09-15, tier: official}
  - {title: NIST AI RMF, url: https://www.nist.gov/artificial-intelligence, publisher: NIST, date: 2026-09-15, tier: official}
  - {title: OpenAI tokenizer, url: https://platform.openai.com/tokenizer, publisher: OpenAI, date: 2026-09-15, tier: official}
last_verified_at: 2026-09-15
review_by: 2026-12-14
status: published
---

前面九课都在做事。这一课把词对回机制：嵌入为什么能「靠近」、检索为什么会拿错、窗口为什么不是无限记忆、幻觉为什么在没有检索时特别顺。读懂摘要即可，不要求推导公式。

<!-- more -->

读完你能：指认 Embedding、上下文窗口和幻觉在自己那套管线里的位置，并能读懂一篇 RAG 或注意力机制论文摘要在说什么。

## 成功标准

画一张自己的管线，标注四处：文档→块、块→向量、问句→近邻、近邻+问句→回答。在「回答」处写上：没有近邻时为什么仍可能有字。

## 嵌入

嵌入把一段话映射到向量，使「意思相近」在几何上更近。它不保存对错，也不知道文档过期。相似不等于相关，更不等于允许你看。Attention Is All You Need 讲的是用注意力机制做序列映射；后来的嵌入模型是同一大家族里的工具，不是那篇论文的原实验设置。

## 检索

近邻搜索是在近似「哪些块的向量靠近问句」。切块切错，近邻就近在错误的地方。权限必须在这个阶段做，因为生成阶段看到的文本已经出了库。

## 窗口与幻觉

上下文窗口是一次能放进模型的 token 上限，见概念卡。超出的部分模型根本没看见。幻觉是补全看起来合理的文本：训练目标是预测下一个 token，不是「只说有出处的话」。所以拒答和引用是产品规则，不是模型本能。NIST 把这类风险放进管理框架，而不是假设某一版参数能根除。

## 练习

找一篇 RAG 综述或 AWS 词条、再打开 Transformer 原论文摘要。用三句话写下：哪一句对应你的切块，哪一句对应你的生成，哪一句你的系统还没做。

## 来源

Vaswani 等，Attention Is All You Need（arXiv:1706.03762）。AWS RAG 词条。NIST AI。OpenAI tokenizer。Last-verified 见页眉。

## 小结

机制不会替你做权限和评测。路径到这里可以停：你已经能交付一个带引用的文档问答，并知道何时不要升级成 Agent。
