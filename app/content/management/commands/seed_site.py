from django.core.management.base import BaseCommand
from django.utils import timezone

from content.models import GlossaryTerm, StaticPage, md
from entities.models import Entity
from news.models import Issue, Source

PAGES = {
    "about": (
        "关于",
        "ai.nornless.com 是 nornless 的 AI 知识阶梯（L0–L7）与科技情报站。"
        "Grok 起草、人审、保鲜。内容默认免费，广告与支持者是配置，总开关默认关。\n\n"
        "第一课路径是「从 0 做一个文档问答」：先判断要不要做知识库，再搭最小检索问答，"
        "然后评测、加引用和拒答，最后才讨论 Agent。",
    ),
    "disclosure": (
        "AI 使用披露",
        "每篇有 AI 披露：模型、协助比例、复核人、复核日。进站生成内容必须带 generation_log。\n\n"
        "本站公开页不加载第三方脚本。HTMX 与 Alpine 都放在本站静态目录。",
    ),
    "ads-policy": (
        "广告政策",
        "标识由模板注入：广告 / 赞助 / 推广。禁止脚本、iframe、像素、SVG。"
        "禁止红线词与绝对化用语。单一广告主展示占比不超过 30%。上下文定向，不做人群画像。暂不开发票。\n\n"
        "广告总开关默认关闭；关闭时招聘、发布墙、活动、优惠、赞助内容和投放页返回 404。",
    ),
    "license": (
        "许可",
        "正文 CC BY-NC-ND 4.0（署名、链回、保留 AI 披露与 Last-verified；禁改编与商用）。"
        "代码块 MIT。资源包仅个人与团队内部使用、禁止再分发。"
        "允许搜索与问答引擎索引摘要；拒绝纯训练爬虫。",
    ),
    "privacy": (
        "隐私",
        "邮箱登录。无 cookie 同意横幅。日志不写邮箱、IP、码、令牌。IP 只存日盐哈希。"
        "账户删除申请后 7 天匿名化。\n\n"
        "读完标记：登录后写入账户进度；未登录写在浏览器本地，不建账号。",
    ),
    "errata": ("勘误", "已发布文章的勘误会出现在这里，并在原文顶部提示。发现错误可用文末「报告错误」。"),
    "changelog": (
        "更新日志",
        "- 2026-09-16：补办公/创作概念卡与三条短路径；测评改为建议起点，地图不锁。\n"
        "- 2026-09-15：文档问答 10 单元与 L0–L2 概念卡首发。\n"
        "- 2026-09-14：站点按对外 / Studio / Admin 铺完，广告总开关默认关。",
    ),
}

TERMS = [
    ("上下文窗口", "模型一次能读入的文本上限。", "更长不等于更好，注意力会稀释，账单会上升。"),
    ("幻觉", "生成看起来合理但没有根据的内容。", "用检索、拒答和人工抽查缓解，不要指望一次提示词根除。"),
    ("RAG", "先检索再生成。", "把「现查」和「现写」分开，是文档问答的最小骨架。"),
    ("Token", "模型计费与窗口的基本单位。", "中文大约 1–2 字对应 1–2 个 token，以各家分词器为准。"),
    ("嵌入", "把文本变成可比较的向量。", "相近意思的句子，向量距离通常更近；它不理解对错。"),
    ("切块", "把长文档切成可检索的片段。", "块太大噪声高，太小会切断句子；重叠用来保上下文。"),
    ("检索", "按问题找出可能相关的块。", "检索错了，后面生成再漂亮也是错的。"),
    ("拒答", "证据不足时明确说不知道。", "拒答比胡编更值钱，尤其是对内规章和数字。"),
    ("引用", "回答时指出用了哪一段原文。", "没有引用的内部问答，同事没法核对。"),
    ("提示词", "给模型的任务说明书。", "写清任务、约束、格式，比堆形容词有用。"),
    ("系统提示词", "长期有效的角色与规则。", "适合放「不确定就说不知道」这类稳定约束。"),
    ("温度", "控制生成随机程度的参数。", "要事实时偏低；要草稿时可以略高。不是准确率旋钮。"),
    ("知识库", "供检索的文档集合。", "它不是模型记忆。更新知识库，不必重训模型。"),
    ("Agent", "能选工具、多步执行的程序。", "比单次问答贵、更难评测；默认先不要上。"),
    ("微调", "用自己的数据继续训练模型。", "适合稳定口径与格式，不适合天天变的文档。"),
    ("评测集", "事先写好的问句与可接受答案。", "没有评测集，你只是在演示，不是在交付。"),
    ("金标", "人工确认过的标准答案。", "金标要可观察：能指出该引用哪一段。"),
    ("召回", "相关块被找出来的比例。", "召回低时先改切块和检索，再改提示词。"),
    ("准确率", "答案被判为可接受的比例。", "要同时记胡编和拒答，否则数字会很好看。"),
    ("权限", "谁能看见哪份文档。", "检索阶段就要过滤，不能靠提示词保密。"),
    ("语料", "用来检索或训练的文本材料。", "扫描件、表格、权限混乱的网盘，都要先清洗。"),
    ("工作流", "按时间或事件自动跑的步骤。", "文档问答里通常是：同步语料 → 切块 → 建索引。"),
    ("长上下文", "一次塞进窗口的很长材料。", "适合已经圈定的一小份材料；知识库在变时用检索。"),
    ("工具调用", "模型请求执行外部函数。", "查库、算数、发请求都属于工具，要鉴权和日志。"),
    ("过时", "复核日已过、结论可能失效。", "本站过复核日会挂条，并进入过时清单。"),
    ("Last-verified", "上次核对事实的日期。", "引用本站文章时请带上这个日期。"),
    ("支持者", "用会员码兑换的付费读者身份。", "价格在发卡站配置；站内只兑码，不接支付。"),
    ("会员码", "发卡站发出、站内兑一次的码。", "明文只在生成瞬间可见，库里只存哈希。"),
    ("向量索引", "按相似度查找嵌入的结构。", "pgvector 是 PostgreSQL 上常用的一种实现。"),
    ("块重叠", "相邻切块共用的文字。", "用来减少「答案刚好被切断」的情况。"),
    ("幻觉率", "评测里胡编条目的比例。", "要单独记账，不要和「没找到」混在一起。"),
    ("文档问答", "针对自有文档提问并引用回答。", "本站有一条完整项目路径，也可以只读其中一课。"),
    ("少样本", "在提示词里放几个例子。", "格式和口径靠例子比靠形容词稳。"),
    ("任务说明书", "写清任务、约束、输入和格式。", "给模型的 brief，也是给同事的 brief。"),
    ("验收", "核对出处、数字和能不能执行。", "没有验收步骤的生成，只是草稿。"),
    ("材料过期", "源文档已失效还在被引用。", "过复核日要挂条或退出索引。"),
    ("署名", "标明谁写的、模型是否协助。", "本站每篇有 AI 披露和 Last-verified。"),
    ("图像生成", "用提示词出图的一类模型。", "版权与肖像要另看，不能当免费素材库。"),
    ("开卷", "回答时可以看材料。", "文档问答就是开卷考试；检索是目录。"),
]

ENTITIES = [
    ("pgvector", "pgvector", "tool", "https://github.com/pgvector/pgvector", "PostgreSQL 向量扩展，常用来存嵌入并做相似度检索。"),
    ("htmx", "HTMX", "tool", "https://htmx.org", "用 HTML 属性做局部请求，不必上 SPA。本站公开页采用它。"),
    ("grok", "Grok", "model", "https://x.ai", "xAI 的对话与编码模型。本站编辑部默认起草模型。"),
    ("xai", "xAI", "company", "https://x.ai", "Grok 的开发公司。"),
    ("attention-is-all-you-need", "Attention Is All You Need", "paper", "https://arxiv.org/abs/1706.03762", "Transformer 原论文，注意力机制的常用引用。"),
    ("nist-ai-rmf", "NIST AI RMF", "paper", "https://www.nist.gov/artificial-intelligence", "美国国家标准与技术研究院的人工智能风险管理框架。"),
]


class Command(BaseCommand):
    help = "写入静态页、术语、实体、白名单源、早报与周报"

    def handle(self, *args, **opts):
        from content.models import ContentNode

        for slug in (
            "minimal-rag-from-folder",
            "news-agent-metered",
            "news-context-1m",
            "news-vector-2",
        ):
            n = ContentNode.all_objects.filter(slug=slug).first()
            if n:
                n.delete()
                self.stdout.write(f"removed stale {slug}")
        for slug, (title, body) in PAGES.items():
            page, _ = StaticPage.objects.update_or_create(
                slug=slug,
                defaults={"title": title, "body_md": body, "html": md.render(body)},
            )
            self.stdout.write(f"page {page.slug}")
        for term, definition, body in TERMS:
            if len(definition) > 60 or len(body) > 300:
                raise ValueError(f"glossary too long: {term}")
            GlossaryTerm.objects.update_or_create(
                term=term, defaults={"definition": definition[:60], "body": body[:300]}
            )
        for slug, name, kind, url, summary in ENTITIES:
            Entity.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "kind": kind, "official_url": url, "summary": summary},
            )
        Source.objects.update_or_create(
            url="https://www.nist.gov/artificial-intelligence",
            defaults={"name": "NIST AI", "tier": "official"},
        )
        Source.objects.update_or_create(
            url="https://aws.amazon.com/what-is/retrieval-augmented-generation/",
            defaults={"name": "AWS RAG", "tier": "official"},
        )
        Source.objects.update_or_create(
            url="https://platform.openai.com/tokenizer",
            defaults={"name": "OpenAI tokenizer", "tier": "official"},
        )
        Source.objects.update_or_create(
            url="https://arxiv.org/abs/1706.03762",
            defaults={"name": "Attention Is All You Need", "tier": "official"},
        )
        Source.objects.update_or_create(
            url="https://github.com/pgvector/pgvector",
            defaults={"name": "pgvector", "tier": "official"},
        )
        today = timezone.now().date().isoformat()
        daily_md = (
            f"今日早报 {today}。先读「从 0 做一个文档问答」的第一课："
            "你是不是真的需要一个知识库。\n\n"
            "今日行动：打开学习地图，用测评选路；若已有文件夹里的规章，"
            "先写 20 条只有这些文档才答得出的问题，再谈模型。\n\n"
            "<!-- more -->\n\n"
            "相关快讯见情报流。过复核日的文章会进过时清单。"
        )
        Issue.objects.update_or_create(
            slug=f"daily-{today}",
            defaults={
                "kind": "daily",
                "title": f"早报 {today}",
                "published_at": timezone.now(),
                "status": "published",
                "body_md": daily_md,
                "html": md.render(daily_md),
                "items": [
                    {"title": "你是不是真的需要一个知识库", "url": "/articles/need-a-kb"},
                    {"title": "检索增强生成仍把「先检索再生成」当骨架", "url": "/articles/news-rag-definition"},
                    {"title": "上下文窗口", "url": "/articles/context-window"},
                ],
            },
        )
        week = timezone.now().date().strftime("%Y-W%W")
        weekly_md = (
            f"周报 {week}。判断段由人写：先把文档问答跑通，再谈 Agent。\n\n"
            "<!-- more -->\n\n"
            "## 重要\n\n"
            "最小 RAG 仍然够用：文件夹、切块、检索、带引用的回答。NIST AI RMF 把幻觉当要管理的风险，不是靠提示词保证不出现。\n\n"
            "## 不重要\n\n"
            "窗口数字又涨了一档，并不自动等于检索更好。评测集比换模型更先该做。\n\n"
            "## 被高估\n\n"
            "一上来就上 Agent。多步工具调用会同时放大权限、账单和评测成本。\n\n"
            "本周岗位观察：能写金标问题、能画权限边界的人，比会调参数的人更缺。"
        )
        Issue.objects.update_or_create(
            slug=f"weekly-{week}",
            defaults={
                "kind": "weekly",
                "title": f"周报 {week}",
                "published_at": timezone.now(),
                "status": "published",
                "body_md": weekly_md,
                "html": md.render(weekly_md),
                "items": [
                    {"title": "学习地图", "url": "/learn"},
                    {"title": "何时不该上 Agent", "url": "/articles/when-not-agent"},
                    {"title": "过时清单", "url": "/digest/outdated"},
                ],
            },
        )
        month = timezone.now().strftime("%Y-%m")
        outdated_md = (
            f"{month} 过时清单。本月暂无作废条目。过复核日的文章会自动挂条，"
            "并在这里汇总替代节点。"
        )
        Issue.objects.update_or_create(
            slug=f"outdated-{month}",
            defaults={
                "kind": "outdated",
                "title": f"{month} 过时清单",
                "published_at": timezone.now(),
                "status": "published",
                "body_md": outdated_md,
                "html": md.render(outdated_md),
                "items": [],
            },
        )
        from accounts.models import User
        from content.models import Asset, new_public_id
        from mail.models import MailTemplate

        author, created = User.objects.get_or_create(
            email="editor@localhost",
            defaults={
                "display_name": "himma",
                "staff_role": "publisher",
                "is_staff": True,
            },
        )
        if created:
            author.set_unusable_password()
            author.save()

        node, created = ContentNode.all_objects.get_or_create(
            slug="rag-vs-long-context",
            defaults={
                "public_id": new_public_id(),
                "title": "RAG 还是长上下文",
                "kind": "compare",
                "summary": "检索增强和把整份材料塞进窗口，不是同一件事，选错会同时烧掉钱和准确率。",
                "body_md": (
                    "读完你能：说出何时该检索、何时该把原文放进窗口。\n\n"
                    "<!-- more -->\n\n"
                    "成功标准：拿一份自己的材料，写出「用 RAG」和「塞进窗口」各一条理由。\n\n"
                    "长上下文适合已经圈定的一小份材料；知识库在变、要计费可控时用 RAG。\n\n"
                    "## 来源\n\n"
                    "AWS 对 RAG 的说明，以及各家公开的上下文窗口文档。核对日期见 Last-verified。\n"
                ),
                "status": "published",
                "access": "free",
                "level": "L2",
                "domain": "dev-agent",
                "tags": ["RAG", "doc-qa"],
                "ai": {
                    "generated": False,
                    "reviewed_by": "himma",
                    "reviewed_at": "2026-09-15",
                    "assist_ratio": 0,
                },
            },
        )
        if created:
            node.published_at = timezone.now()
        node.last_verified_at = timezone.now().date()
        node.render()
        node.save()
        Asset.objects.update_or_create(
            slug="doc-qa-checklist",
            defaults={"title": "文档问答检查清单", "access": "free", "note": "与上线检查单配套，支持者可下全部包。"},
        )
        MailTemplate.objects.update_or_create(
            key="confirm",
            defaults={"subject": "确认订阅", "body_md": "打开确认链接完成订阅。"},
        )
        MailTemplate.objects.update_or_create(
            key="magic",
            defaults={"subject": "登录链接", "body_md": "15 分钟内有效。"},
        )
        self.stdout.write("seed_site done")
