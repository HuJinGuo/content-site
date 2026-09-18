from django.core.management.base import BaseCommand

from graph.models import GraphNode, LearningPath, PathItem

NODES = [
    ("doc-qa/00-need-a-kb", "L0", "dev-agent", "你是不是真的需要一个知识库"),
    ("doc-qa/01-how", "L1", "dev-agent", "文档问答到底怎么工作（直觉版）"),
    ("doc-qa/02-build-vs-buy", "L2", "dev-agent", "选产品还是自建，选哪家模型"),
    ("doc-qa/03-corpus", "L3", "dev-agent", "准备语料：切分、清洗、权限"),
    ("doc-qa/04-minimal-rag", "L3", "dev-agent", "最小 RAG：从文件夹到能提问"),
    ("doc-qa/05-eval", "L4", "dev-agent", "为什么它会答错，怎样评测"),
    ("doc-qa/06-citations", "L6", "dev-agent", "加引用、拒答、权限和日志"),
    ("doc-qa/07-workflow", "L4", "dev-agent", "做成工作流：定时更新语料"),
    ("doc-qa/08-when-not-agent", "L4", "dev-agent", "何时不该上 Agent"),
    ("doc-qa/09-principles", "L7", "dev-agent", "原理回看：检索、嵌入、幻觉从哪来"),
    ("l0/what-is-llm", "L0", "general", "什么是大语言模型"),
    ("l0/ai-vs-search", "L0", "general", "AI 和搜索差在哪"),
    ("l0/when-to-use-ai", "L0", "general", "什么时候该用 AI"),
    ("l0/chat-privacy", "L0", "general", "对话里的隐私"),
    ("l0/what-is-kb", "L0", "general", "什么是知识库"),
    ("l1/context-window", "L1", "general", "上下文窗口"),
    ("l1/hallucination", "L1", "general", "幻觉"),
    ("l1/token", "L1", "general", "Token"),
    ("l1/prompt", "L1", "general", "提示词基础"),
    ("l1/embedding", "L1", "general", "嵌入"),
    ("l1/temperature", "L1", "general", "温度"),
    ("l1/system-prompt", "L1", "general", "系统提示词"),
    ("l1/retrieval", "L1", "general", "检索"),
    ("l1/chunking", "L1", "general", "切块"),
    ("l1/citation", "L1", "general", "引用"),
    ("l1/refusal", "L1", "general", "拒答"),
    ("l1/eval-basics", "L1", "general", "评测入门"),
    ("l1/rag", "L1", "dev-agent", "检索增强生成"),
    ("l2/product-api-local", "L2", "general", "产品 vs API vs 本地模型"),
    ("l2/cost-estimate", "L2", "general", "账单怎么估"),
    ("l2/agent-vs-workflow", "L2", "dev-agent", "Agent 和工作流"),
    ("l2/tool-use", "L2", "dev-agent", "工具调用"),
    ("l1/few-shot", "L1", "general", "少样本"),
    ("l1/review-answer", "L1", "office", "验收一次回答"),
    ("l1/task-brief", "L1", "office", "给同事的任务说明书"),
    ("l1/meeting-notes", "L1", "office", "会议纪要怎么用模型"),
    ("l2/table-model", "L2", "office", "表格怎么喂给模型"),
    ("l1/image-gen", "L1", "aigc", "图像生成入门"),
    ("l1/gen-attr", "L1", "aigc", "生成内容怎么署名"),
    ("l2/context-rot", "L2", "general", "材料过期"),
    ("l2/stuffing-pdf", "L2", "dev-agent", "把整份 PDF 塞进去"),
    ("l2/agent-first", "L2", "dev-agent", "一上来就上 Agent"),
]


UNITS = [
    (1, "你是不是真的需要一个知识库", "用决策表决定做最小检索、买产品，还是先不做。"),
    (2, "文档问答到底怎么工作（直觉版）", "能向同事讲清「问句 → 检索 → 生成」三步，并指出每步会在哪失败。"),
    (3, "选产品还是自建，选哪家模型", "画出决策树，并估得出数量级月费，而不是精确到分。"),
    (4, "准备语料：切分、清洗、权限", "把一叠文档整理成可检索的块，并写出块大小、重叠和权限规则。"),
    (5, "最小 RAG：从文件夹到能提问", "在本机用一个文件夹搭出能提问的最小检索问答，并跑通一条成功标准。"),
    (6, "为什么它会答错，怎样评测", "写出不少于 20 条金标问题，并记录命中 / 拒答 / 胡编。"),
    (7, "加引用、拒答、权限和日志", "对照上线检查单：回答带引用、证据不足就拒答、文档按权限进检索。"),
    (8, "做成工作流：定时更新语料", "写出语料更新的触发条件、步骤和失败时怎么回滚。"),
    (9, "何时不该上 Agent", "用判断清单决定停留在检索问答，还是再加工具调用。"),
    (10, "原理回看：检索、嵌入、幻觉从哪来", "能指认 Embedding、窗口和幻觉在自己那套管线里的位置。"),
]


class Command(BaseCommand):
    help = "写入文档问答路径与大纲节点（不含正文）"

    def handle(self, *args, **opts):
        keep = {nid for nid, _level, _domain, _title in NODES}
        GraphNode.objects.exclude(node_id__in=keep).delete()
        for nid, level, domain, title in NODES:
            GraphNode.objects.update_or_create(
                node_id=nid, defaults={"title": title, "level": level, "domain": domain, "status": "planned"}
            )
        path, _ = LearningPath.objects.update_or_create(
            slug="doc-qa",
            defaults={
                "title": "从 0 做一个文档问答",
                "summary": "建议顺序，不锁。任何一课都能直接读；只想做项目时再按号走。",
                "level_from": "L0",
                "level_to": "L7",
                "domain": "dev-agent",
                "status": "published",
                "eta_hours": 8,
            },
        )
        for idx, title, goal in UNITS:
            PathItem.objects.update_or_create(
                path=path, unit_index=idx, defaults={"title": title, "goal": goal}
            )
        shorts = [
            (
                "ask-better",
                "把一次提问写清楚",
                "三张卡：任务说明书、系统规则、怎么发现胡编。不必做完文档问答。",
                "L0",
                "L1",
                "general",
                2,
                [
                    (1, "提示词基础", "能把一件工作改写成任务、约束、格式。"),
                    (2, "系统提示词", "写出不超过十行的稳定规则。"),
                    (3, "验收一次回答", "会抽查出处，而不是感觉还行。"),
                ],
            ),
            (
                "hold-agent",
                "先别上 Agent",
                "被要求「上智能体」时先读这三篇。多数需求停在检索问答或工作流。",
                "L2",
                "L4",
                "dev-agent",
                2,
                [
                    (1, "何时不该上 Agent", "用清单决定不上。"),
                    (2, "Agent 和工作流", "能标出该用哪一种。"),
                    (3, "一上来就上 Agent", "认出这种坑，并改回最小方案。"),
                ],
            ),
            (
                "office-ai",
                "办公里先会用",
                "会议、任务说明书、验收回答。不建知识库也能开始。",
                "L0",
                "L2",
                "office",
                2,
                [
                    (1, "什么时候该用 AI", "给本周三件事贴标签。"),
                    (2, "给同事的任务说明书", "写出能转交的 brief。"),
                    (3, "验收一次回答", "数字和出处有核对步骤。"),
                ],
            ),
        ]
        for slug, title, summary, lf, lt, domain, eta, items in shorts:
            p, _ = LearningPath.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "summary": summary,
                    "level_from": lf,
                    "level_to": lt,
                    "domain": domain,
                    "status": "published",
                    "eta_hours": eta,
                },
            )
            for idx, ititle, goal in items:
                PathItem.objects.update_or_create(
                    path=p, unit_index=idx, defaults={"title": ititle, "goal": goal}
                )
        self.stdout.write("seeded outline + paths")
