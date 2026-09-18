from __future__ import annotations

import re

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from access.services import can, entitlements
from accounts.models import User
from codes.models import RedeemError, redeem
from content.models import ContentNode, Feedback, GlossaryTerm, transition
from core.services import set_flag
from entities.models import Entity
from graph.models import LearningPath, PathItem
from learning.models import Progress
from news.models import Issue

DOC_QA_TITLES = [
    "你是不是真的需要一个知识库",
    "文档问答到底怎么工作（直觉版）",
    "选产品还是自建，选哪家模型",
    "准备语料：切分、清洗、权限",
    "最小 RAG：从文件夹到能提问",
    "为什么它会答错，怎样评测",
    "加引用、拒答、权限和日志",
    "做成工作流：定时更新语料",
    "何时不该上 Agent",
    "原理回看：检索、嵌入、幻觉从哪来",
]

CLOSED = [
    "/jobs",
    "/launches",
    "/events",
    "/deals",
    "/sponsored",
    "/advertise",
    "/pricing",
    "/app/ask",
    "/join",
    "/ads/",
    "/quiz",
    "/lab",
]

STUDIO_GET = [
    "/studio/",
    "/studio/posts",
    "/studio/review",
    "/studio/topics",
    "/studio/briefs",
    "/studio/generate",
    "/studio/editor",
    "/studio/issues",
    "/studio/graph",
    "/studio/sources",
    "/studio/entities",
    "/studio/refresh",
    "/studio/errata",
    "/studio/assets",
    "/studio/prompts",
    "/studio/costs",
]

ADMIN_GET = [
    "/admin/",
    "/admin/flags",
    "/admin/codes",
    "/admin/users",
    "/admin/audit",
    "/admin/paywall",
    "/admin/groups",
    "/admin/ads",
    "/admin/zones",
    "/admin/mail",
    "/admin/metrics",
    "/admin/seo",
    "/admin/system",
    "/admin/settings",
]

THIRD_PARTY_NEEDLES = (
    "cdn.jsdelivr",
    "unpkg.com",
    "googleapis.com",
    "googletagmanager",
    "google-analytics",
    "cloudflare.com/ajax",
    "cdnjs.cloudflare",
    "ajax.googleapis",
)


def _redlines() -> list[str]:
    words = []
    for line in (settings.REPO_DIR / "editorial/redlines.txt").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            words.append(line)
    return words


class SeededCatalogTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_all")

    def test_published_counts_and_unit_sequence(self):
        units = ContentNode.objects.filter(kind="unit", track="doc-qa", status="published")
        self.assertGreaterEqual(units.count(), 10)
        titles = set(units.values_list("title", flat=True))
        for title in DOC_QA_TITLES:
            self.assertIn(title, titles)
        for node in units:
            body = node.body_md
            self.assertIn("<!-- more -->", body)
            self.assertIn("成功标准", body)
            self.assertIn("读完你能", body)
            self.assertIn("来源", body)
            self.assertTrue(node.last_verified_at)
            self.assertTrue(node.sources)
            self.assertTrue((node.ai or {}).get("reviewed_by"))
        path = LearningPath.objects.get(slug="doc-qa")
        self.assertEqual(path.title, "从 0 做一个文档问答")
        items = list(PathItem.objects.filter(path=path).order_by("unit_index"))
        self.assertGreaterEqual(len(items), 10)
        linked = [i for i in items if i.node_id]
        self.assertGreaterEqual(len(linked), 10)
        self.assertGreaterEqual(ContentNode.objects.filter(kind="concept", status="published").count(), 20)
        self.assertGreaterEqual(GlossaryTerm.objects.count(), 30)
        self.assertGreaterEqual(ContentNode.objects.filter(kind="news", status="published").count(), 5)
        self.assertTrue(Issue.objects.filter(kind="daily", status="published").exists())
        self.assertTrue(Issue.objects.filter(kind="weekly", status="published").exists())
        self.assertGreaterEqual(Entity.objects.count(), 3)
        self.assertGreaterEqual(LearningPath.objects.filter(status="published").count(), 4)
        self.assertTrue(LearningPath.objects.filter(slug="ask-better").exists())
        self.assertTrue(LearningPath.objects.filter(slug="hold-agent").exists())
        self.assertTrue(LearningPath.objects.filter(slug="office-ai").exists())

    def test_copy_passes_redlines(self):
        words = _redlines()
        for node in ContentNode.objects.filter(status="published"):
            blob = f"{node.title}\n{node.summary}\n{node.body_md}"
            for w in words:
                self.assertNotIn(w, blob, f"{node.slug} contains {w}")

    def test_public_pages_show_real_titles(self):
        home = self.client.get("/")
        self.assertEqual(home.status_code, 200)
        html = home.content.decode()
        self.assertIn("ai.nornless.com", html)
        self.assertIn("2 分钟选路测评", html)
        self.assertIn("按问题进", html)
        self.assertNotIn("暂无数据", html)
        self.assertTrue(
            "你是不是真的需要一个知识库" in html
            or "上下文窗口" in html
            or "什么是大语言模型" in html
            or "检索增强生成" in html
        )
        r = self.client.post("/assess", {"goal": "ship", "time": "2"})
        self.assertEqual(r.status_code, 200)
        self.assertIn("从 0 做一个文档问答", r.content.decode())
        r2 = self.client.post("/assess", {"goal": "understand"})
        self.assertEqual(r2.status_code, 200)
        self.assertIn("什么是大语言模型", r2.content.decode())
        self.assertIn("从 0 做一个文档问答", r2.content.decode())
        learn = self.client.get("/learn")
        self.assertEqual(learn.status_code, 200)
        lhtml = learn.content.decode()
        self.assertIn("从 0 做一个文档问答", lhtml)
        self.assertIn("先别上 Agent", lhtml)
        self.assertIn("办公里先会用", lhtml)
        self.assertIn("先读这一篇", lhtml)
        self.assertIn("什么是大语言模型", lhtml)
        self.assertIn("开始读", lhtml)
        self.assertNotIn("失败案例", lhtml)
        concepts = self.client.get("/learn", {"kind": "concept"}).content.decode()
        self.assertIn("什么是大语言模型", concepts)
        units = self.client.get("/learn", {"kind": "unit"}).content.decode()
        self.assertIn("原理回看：检索、嵌入、幻觉从哪来", units)
        track = self.client.get("/learn/doc-qa")
        self.assertEqual(track.status_code, 200)
        self.assertIn("最小 RAG：从文件夹到能提问", track.content.decode())
        self.assertIn("建议顺序", track.content.decode())
        self.assertEqual(self.client.get("/learn/hold-agent").status_code, 200)
        self.assertEqual(self.client.get("/articles/task-brief").status_code, 200)
        self.assertEqual(self.client.get("/articles/agent-first").status_code, 200)
        unit = self.client.get("/learn/doc-qa/need-a-kb")
        self.assertEqual(unit.status_code, 200)
        uhtml = unit.content.decode()
        self.assertIn("你是不是真的需要一个知识库", uhtml)
        self.assertIn("Last-verified", uhtml)
        self.assertIn("AI 披露", uhtml)
        self.assertIn("来源", uhtml)
        self.assertIn("读完，下一课", uhtml)
        self.assertIn("有用", uhtml)
        self.assertIn("过时了", uhtml)
        self.assertIn("<table>", uhtml)
        self.assertIn("<th>", uhtml)
        article = self.client.get("/articles/context-window")
        self.assertEqual(article.status_code, 200)
        ahtml = article.content.decode()
        self.assertIn("上下文窗口", ahtml)
        self.assertIn("概念卡", ahtml)
        gloss = self.client.get("/glossary")
        self.assertEqual(gloss.status_code, 200)
        self.assertIn("RAG", gloss.content.decode())
        self.assertEqual(self.client.get("/glossary/RAG").status_code, 200)
        news = self.client.get("/news")
        self.assertEqual(news.status_code, 200)
        self.assertIn("检索增强生成仍把", news.content.decode())
        digest = self.client.get("/digest/")
        self.assertEqual(digest.status_code, 200)
        self.assertIn("早报", digest.content.decode())
        daily = Issue.objects.filter(kind="daily").first()
        day = daily.slug.removeprefix("daily-")
        self.assertEqual(self.client.get(f"/digest/daily/{day}").status_code, 200)
        weekly = Issue.objects.filter(kind="weekly").first()
        self.assertEqual(self.client.get(f"/digest/weekly/{weekly.slug}").status_code, 200)
        search = self.client.get("/search", {"q": "上下文窗口"})
        self.assertEqual(search.status_code, 200)
        self.assertIn("上下文窗口", search.content.decode())
        self.assertIn("/articles/context-window", search.content.decode())
        self.assertNotIn('class="lvl"', search.content.decode())
        tagged = self.client.get("/learn", {"tag": "doc-qa"})
        self.assertEqual(tagged.status_code, 200)
        self.assertIn("你是不是真的需要一个知识库", tagged.content.decode())
        for path in ("/", "/learn", "/articles/what-is-llm"):
            html = self.client.get(path).content.decode()
            self.assertNotIn("<option>L0</option>", html)
            self.assertNotIn("<option>L1</option>", html)
            self.assertNotIn('class="lvl"', html)
        topics = self.client.get("/topics")
        self.assertEqual(topics.status_code, 200)
        self.assertIn("doc-qa", topics.content.decode())
        topic = self.client.get("/topics/doc-qa")
        self.assertEqual(topic.status_code, 200)
        self.assertIn("从 0 做一个文档问答", topic.content.decode())
        authors = self.client.get("/authors")
        self.assertEqual(authors.status_code, 200)
        self.assertIn("himma", authors.content.decode())
        for path in (
            "/about",
            "/disclosure",
            "/ads-policy",
            "/license",
            "/privacy",
            "/errata",
            "/changelog",
            "/authors",
            "/subscribe",
            "/redeem",
            "/login",
            "/register",
            "/tools",
            "/compare",
            "/timeline",
            "/models",
            "/companies",
            "/papers",
            "/rss.xml",
            "/sitemap.xml",
        ):
            resp = self.client.get(path)
            self.assertEqual(resp.status_code, 200, path)
        health = self.client.get("/api/v1/health")
        self.assertEqual(health.status_code, 200)
        self.assertTrue(health.json()["ok"])

    def test_learn_map_filters_more_link_and_read_state(self):
        html = self.client.get("/learn").content.decode()
        self.assertIn("先读这一篇", html)
        self.assertIn("什么是大语言模型", html)
        self.assertIn("开始读", html)
        self.assertIn("/articles/what-is-llm", html)
        self.assertIn("先别上 Agent", html)
        self.assertIn("从 0 做一个文档问答", html)
        self.assertIn("听不懂别人在说 Token、幻觉", html)
        concepts = self.client.get("/learn", {"kind": "concept"}).content.decode()
        self.assertIn("什么是大语言模型", concepts)
        self.assertIn("少样本", concepts)
        self.assertNotIn("原理回看：检索、嵌入、幻觉从哪来", concepts)
        units = self.client.get("/learn", {"kind": "unit"}).content.decode()
        self.assertIn("原理回看：检索、嵌入、幻觉从哪来", units)
        tagged = self.client.get("/learn", {"tag": "doc-qa"})
        self.assertEqual(tagged.status_code, 200)
        self.assertIn("你是不是真的需要一个知识库", tagged.content.decode())
        track = self.client.get("/learn/doc-qa").content.decode()
        self.assertIn("建议顺序", track)
        self.assertIn("也可以从这些课进", track)
        self.assertIn("/learn/doc-qa/need-a-kb", track)
        self.assertIn("/learn/doc-qa/minimal-rag", track)
        self.client.post("/articles/what-is-llm/read")
        after = self.client.get("/learn", {"kind": "concept"}).content.decode()
        self.assertRegex(after, r'class="card click post read"[^>]*data-slug="what-is-llm"|data-slug="what-is-llm"[^>]*class="card click post read"')
        user = User.objects.create_user("map-reader@localhost", "password12")
        self.client.force_login(user)
        self.client.post("/articles/context-window/read")
        logged = self.client.get("/learn", {"kind": "concept"}).content.decode()
        self.assertRegex(logged, r'class="card click post done"[^>]*data-slug="context-window"|data-slug="context-window"[^>]*class="card click post done"')

    def test_learn_page_book_tokens(self):
        html = self.client.get("/learn").content.decode()
        self.assertIn("先读这一篇", html)
        self.assertIn('href="/articles/what-is-llm"', html)
        self.assertIn("开始读", html)
        self.assertIn("先别上 Agent", html)
        self.assertIn("从 0 做一个文档问答", html)
        self.assertIn("featured", html)
        self.assertIn("约 8 小时 · 建议顺序，不锁", html)
        self.assertNotIn("#14b8a6", html)
        self.assertNotIn("全部层", html)
        for name in ("app/static/nornless.css", "app/static/components.css"):
            css = (settings.REPO_DIR / name).read_text(encoding="utf-8")
            self.assertNotIn("#14b8a6", css, name)
        concepts = self.client.get("/learn", {"kind": "concept"}).content.decode()
        self.assertIn("什么是大语言模型", concepts)
        units = self.client.get("/learn", {"kind": "unit"}).content.decode()
        self.assertIn("原理回看：检索、嵌入、幻觉从哪来", units)

    def test_closed_zones_404_and_absent_from_nav_sitemap(self):
        home = self.client.get("/").content
        self.assertNotIn(b'href="/jobs"', home)
        self.assertNotIn(b'href="/advertise"', home)
        self.assertNotIn(b'href="/pricing"', home)
        for path in CLOSED:
            self.assertEqual(self.client.get(path).status_code, 404, path)
        sm = self.client.get("/sitemap.xml").content.decode()
        self.assertNotIn("/jobs", sm)
        self.assertNotIn("/advertise", sm)
        self.assertNotIn("/pricing", sm)
        self.assertNotIn("/launches", sm)
        self.assertIn("/articles/need-a-kb", sm)

    def test_no_third_party_scripts_on_public_pages(self):
        for path in ("/", "/articles/need-a-kb", "/learn", "/news"):
            html = self.client.get(path).content.decode()
            for needle in THIRD_PARTY_NEEDLES:
                self.assertNotIn(needle, html, f"{path} {needle}")
            for src in re.findall(r"<script[^>]+src=['\"]([^'\"]+)['\"]", html, flags=re.I):
                self.assertTrue(src.startswith("/"), f"{path} script {src}")

    def test_anonymous_and_login_read_mark(self):
        r = self.client.post("/articles/need-a-kb/read")
        self.assertEqual(r.status_code, 302)
        self.assertNotIn("/login", r["Location"])
        r2 = self.client.post("/articles/need-a-kb/read")
        self.assertEqual(r2.status_code, 302)
        user = User.objects.create_user("reader-cat@localhost", "password12")
        self.client.force_login(user)
        self.client.post("/articles/need-a-kb/read")
        prog = Progress.objects.get(user=user, node__slug="need-a-kb")
        self.assertTrue(prog.read)
        self.client.post("/articles/need-a-kb/read")
        prog.refresh_from_db()
        self.assertTrue(prog.read)
        self.client.post("/articles/need-a-kb/read", {"undo": "1"})
        prog.refresh_from_db()
        self.assertFalse(prog.read)
        self.client.post("/articles/need-a-kb/read")
        prog.refresh_from_db()
        self.assertTrue(prog.read)

    def test_feedback_outdated(self):
        r = self.client.post("/articles/need-a-kb/feedback", {"kind": "outdated"})
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Feedback.objects.filter(node__slug="need-a-kb", kind="outdated").exists())

    def test_register_bookmark_subscribe_app(self):
        r = self.client.post(
            "/register",
            {"email": "newreader@localhost", "password": "password12", "display_name": "读者甲"},
        )
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r["Location"], "/app/")
        self.assertEqual(self.client.get("/app/").status_code, 200)
        self.assertEqual(self.client.get("/app/library").status_code, 200)
        node = ContentNode.objects.get(slug="context-window")
        self.assertEqual(self.client.post(f"/articles/{node.slug}/bookmark").status_code, 302)
        sub = self.client.post("/subscribe", {"email": "newreader@localhost"})
        self.assertEqual(sub.status_code, 200)

    def test_staff_pages_codes_flags_studio(self):
        guest_studio = self.client.get("/studio/")
        self.assertNotEqual(guest_studio.status_code, 200)
        self.assertNotEqual(self.client.get("/studio/posts").status_code, 200)
        self.assertNotEqual(self.client.get("/studio/editor").status_code, 200)
        guest_admin = self.client.get("/admin/")
        self.assertNotEqual(guest_admin.status_code, 200)
        pub = User.objects.create_user(
            "publisher-cat@localhost",
            "password12",
            staff_role="publisher",
            is_staff=True,
            display_name="主编",
        )
        self.client.force_login(pub)
        studio_heads = {
            "/studio/": "工作台",
            "/studio/posts": "文章",
            "/studio/review": "审稿",
            "/studio/topics": "选题池",
            "/studio/briefs": "Brief",
            "/studio/generate": "生成台",
            "/studio/editor": "新稿",
            "/studio/issues": "期刊编排",
            "/studio/graph": "图谱",
            "/studio/sources": "情报源",
            "/studio/entities": "实体与认领",
            "/studio/refresh": "保鲜队列",
            "/studio/errata": "勘误",
            "/studio/assets": "资产",
            "/studio/prompts": "提示词版本",
            "/studio/costs": "成本",
        }
        for path in STUDIO_GET:
            resp = self.client.get(path)
            self.assertEqual(resp.status_code, 200, path)
            html = resp.content.decode()
            self.assertIn(studio_heads[path], html, path)
            self.assertNotIn("暂无数据", html)
            self.assertNotIn("#14b8a6", html)
            self.assertNotIn("<option>L0</option>", html)
            self.assertNotIn("<option>L1</option>", html)
        for path in (
            "/studio/editor/need-a-kb",
            "/studio/qa/need-a-kb",
            "/studio/facts/need-a-kb",
        ):
            self.assertEqual(self.client.get(path).status_code, 200, path)
        posts_page = self.client.get("/studio/posts")
        self.assertEqual(posts_page.status_code, 200)
        posts_html = posts_page.content.decode()
        self.assertIn("文章", posts_html)
        self.assertIn("什么是大语言模型", posts_html)
        self.assertIn("/studio/editor/what-is-llm", posts_html)
        ed = self.client.get("/studio/editor").content.decode()
        self.assertIn("标签", ed)
        r = self.client.post(
            "/studio/editor",
            {
                "title": "机审草稿标题足够长了",
                "slug": "catalog-studio-draft",
                "kind": "concept",
                "access": "free",
                "tags": "入门, RAG",
                "summary": "这是一段超过二十字的摘要，用来过机审门槛。",
                "body_md": "正文。" * 40,
            },
        )
        self.assertEqual(r.status_code, 302)
        draft = ContentNode.objects.get(slug="catalog-studio-draft")
        self.assertEqual(draft.tags, ["入门", "RAG"])
        draft = transition(draft, "machine_qa", pub, "to qa")
        draft = transition(draft, "factcheck", pub, "to fact")
        draft = transition(draft, "editing", pub, "to edit")
        r = self.client.post(
            f"/studio/editor/{draft.slug}",
            {"action": "transition", "to": "published", "reason": "ship catalog draft"},
        )
        self.assertEqual(r.status_code, 302)
        draft.refresh_from_db()
        self.assertEqual(draft.status, "published")
        admin = User.objects.create_superuser("ops-cat@localhost", "password12")
        self.client.force_login(admin)
        admin_heads = {
            "/admin/": "运营",
            "/admin/flags": "功能开关",
            "/admin/codes": "发卡",
            "/admin/users": "用户",
            "/admin/audit": "审计",
            "/admin/paywall": "付费墙内容",
            "/admin/groups": "分组",
            "/admin/ads": "广告系统",
            "/admin/zones": "专区审核",
            "/admin/mail": "邮件",
            "/admin/metrics": "达标线",
            "/admin/seo": "SEO 重定向",
            "/admin/system": "系统",
            "/admin/settings": "站点设置",
        }
        for path in ADMIN_GET:
            resp = self.client.get(path)
            self.assertEqual(resp.status_code, 200, path)
            html = resp.content.decode()
            self.assertIn(admin_heads[path], html, path)
            self.assertNotIn("暂无数据", html)
            self.assertNotIn("#14b8a6", html)
        from core.services import snapshot

        before = snapshot().get("paywall.enabled")
        r = self.client.post("/admin/flags", {"key": "paywall.enabled", "value": "on"})
        self.assertEqual(r.status_code, 200)
        self.assertIn("reason required", r.content.decode())
        self.assertEqual(snapshot().get("paywall.enabled"), before)
        r = self.client.post("/admin/flags", {"key": "ads.enabled", "value": "on", "reason": "open ads for test"})
        self.assertEqual(r.status_code, 200)
        r = self.client.post(
            "/admin/flags",
            {"key": "ads.self_serve.jobs", "value": "on", "reason": "open jobs for test"},
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.client.get("/jobs").status_code, 200)
        r = self.client.post("/admin/flags", {"key": "ads.enabled", "reason": "close ads again"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.client.get("/jobs").status_code, 404)
        r = self.client.post(
            "/admin/codes",
            {"action": "issue", "kind": "member", "count": "1", "days": "31", "reason": "catalog issue"},
        )
        self.assertEqual(r.status_code, 200)
        html = r.content.decode()
        match = re.search(r"[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}", html)
        self.assertIsNotNone(match)
        code = match.group(0)
        reader = User.objects.create_user("redeemer-cat@localhost", "password12")
        redeemed = redeem(reader, code)
        self.assertEqual(redeemed.status, "redeemed")
        self.assertTrue(entitlements(reader).has("paid_content"))
        with self.assertRaises(RedeemError):
            redeem(reader, code)
        for name in ("app/static/nornless.css", "app/static/components.css"):
            css = (settings.REPO_DIR / name).read_text(encoding="utf-8")
            self.assertNotIn("#14b8a6", css, name)

    def test_hard_rules_still_hold_on_seeded_db(self):
        node = ContentNode.objects.get(slug="need-a-kb")
        self.assertEqual(node.status, "published")
        draft = ContentNode.objects.create(
            slug="unpublished-cat",
            public_id="TESTUNPUB001",
            title="未发布稿件标题够长",
            kind="concept",
            summary="这是一段超过二十字的摘要，用来占位说明。",
            body_md="可见。\n\n<!-- more -->\n\nSECRET_TAIL",
            status="drafting",
            access="free",
            level="L1",
        )
        draft.render()
        draft.save()
        self.assertEqual(self.client.get("/articles/unpublished-cat").status_code, 404)
        paid = ContentNode.objects.create(
            slug="paid-cat",
            public_id="TESTPAID0001",
            title="收费样例标题够长",
            kind="concept",
            summary="这是一段超过二十字的摘要，用来占位说明。",
            body_md="可见导语。\n\n<!-- more -->\n\nSECRET_TAIL 不该出现。",
            status="published",
            access="supporter",
            level="L1",
        )
        paid.render()
        paid.save()
        set_flag("paywall.enabled", True, actor=None, reason="catalog paywall")
        html = self.client.get("/articles/paid-cat").content.decode()
        self.assertIn("可见导语", html)
        self.assertNotIn("SECRET_TAIL", html)
        set_flag("paywall.enabled", False, actor=None, reason="catalog paywall off")
        html = self.client.get("/articles/paid-cat").content.decode()
        self.assertIn("SECRET_TAIL", html)
        bot = User.objects.create_user("bot-cat@localhost", "password12", staff_role="author", is_staff=True)
        self.assertFalse(can(bot, "publish"))
        editing = ContentNode.objects.create(
            slug="bot-pub-cat",
            public_id="TESTBOTPUB01",
            title="机器人想发布的标题",
            kind="concept",
            summary="这是一段超过二十字的摘要，用来占位说明。",
            body_md="x",
            status="editing",
            access="free",
            level="L1",
        )
        with self.assertRaises(PermissionError):
            transition(editing, "published", bot, "no")
        with self.assertRaises(ValueError):
            transition(draft, "published", bot, "skip")
