from __future__ import annotations

import pytest
from django.conf import settings

from access.services import can, can_read_full, grant_membership, visible
from accounts.models import User
from codes.models import RedeemError, issue_codes, redeem
from content.models import ContentNode, import_markdown, new_public_id, transition
from core.services import set_flag
from graph.models import LearningPath

pytestmark = pytest.mark.django_db


def _publisher() -> User:
    return User.objects.create_user(
        "publisher@localhost",
        "password12",
        staff_role="publisher",
        is_staff=True,
        display_name="主编",
    )


def _node(**kwargs) -> ContentNode:
    defaults = {
        "slug": "demo",
        "public_id": new_public_id(),
        "title": "样例文章标题",
        "kind": "concept",
        "summary": "这是一段超过五十字用来充当摘要的说明文字，避免校验空着。",
        "body_md": "可见导语。\n\n<!-- more -->\n\nSECRET_TAIL 不该出现。",
        "status": "published",
        "access": "free",
        "level": "L1",
        "domain": "general",
    }
    defaults.update(kwargs)
    node = ContentNode(**defaults)
    node.render()
    node.save()
    return node


def test_health(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert "flags_version" in body


def test_home_learn_news_redeem(client):
    LearningPath.objects.create(
        slug="doc-qa",
        title="从 0 做一个文档问答",
        summary="最小路径",
        status="published",
    )
    r = client.get("/")
    assert r.status_code == 200
    assert b"ai.nornless.com" in r.content
    assert client.get("/learn").status_code == 200
    assert client.get("/news").status_code == 200
    assert client.get("/glossary").status_code == 200
    assert client.get("/search").status_code == 200
    assert client.get("/redeem").status_code == 200
    assert client.get("/login").status_code == 200
    assert client.get("/about").status_code == 200


def test_closed_zones_404(client):
    assert client.get("/jobs").status_code == 404
    assert client.get("/advertise").status_code == 404
    assert client.get("/pricing").status_code == 404
    assert client.get("/launches").status_code == 404
    assert client.get("/app/ask").status_code == 404
    assert b'href="/jobs"' not in client.get("/").content


def test_open_jobs_and_advertise(client):
    set_flag("ads.enabled", True, actor=None, reason="test open ads")
    set_flag("ads.self_serve.jobs", True, actor=None, reason="test open jobs")
    assert client.get("/jobs").status_code == 200
    assert client.get("/advertise").status_code == 200


def test_sample_article_import(client):
    path = settings.REPO_DIR / "content/concepts/context-window.md"
    node = import_markdown(path)
    assert node.status == "published"
    r = client.get("/articles/context-window")
    assert r.status_code == 200
    html = r.content.decode()
    assert "上下文窗口" in html
    assert "Last-verified" in html
    assert "AI 披露" in html
    assert "来源" in html


def test_paywall_cuts_html(client):
    node = _node(access="supporter", slug="paid-demo")
    set_flag("paywall.enabled", True, actor=None, reason="test paywall")
    r = client.get("/articles/paid-demo")
    assert r.status_code == 200
    html = r.content.decode()
    assert "可见导语" in html
    assert "SECRET_TAIL" not in html
    assert "后半段需要权益" in html
    assert can_read_full(None, node) is False


def test_paywall_off_shows_full(client):
    _node(access="supporter", slug="paid-open")
    r = client.get("/articles/paid-open")
    assert r.status_code == 200
    assert b"SECRET_TAIL" in r.content


def test_unpublished_is_404(client):
    _node(slug="draft-only", status="drafting")
    assert client.get("/articles/draft-only").status_code == 404


def test_redeem_once():
    user = User.objects.create_user("reader@localhost", "password12")
    _batch, plains = issue_codes(kind="member", count=1, days=31, actor=None, reason="test issue")
    code = plains[0]
    redeemed = redeem(user, code)
    assert redeemed.status == "redeemed"
    user.refresh_from_db()
    from access.services import entitlements

    assert entitlements(user).has("paid_content")
    with pytest.raises(RedeemError) as exc:
        redeem(user, code)
    assert exc.value.code == "used"


def test_illegal_transition():
    node = _node(status="drafting", slug="trans-demo")
    pub = _publisher()
    with pytest.raises(ValueError):
        transition(node, "published", pub, "skip")
    node = transition(node, "machine_qa", pub, "to qa")
    node = transition(node, "factcheck", pub, "to fact")
    node = transition(node, "editing", pub, "to edit")
    node = transition(node, "published", pub, "ship")
    assert node.status == "published"


def test_bot_cannot_publish():
    node = _node(status="editing", slug="bot-demo")
    bot = User.objects.create_user("bot@localhost", "password12", staff_role="author", is_staff=True)
    with pytest.raises(PermissionError):
        transition(node, "published", bot, "no")
    assert can(bot, "publish") is False


def test_access_matrix():
    free = _node(slug="free-n", access="free")
    paid = _node(slug="sup-n", access="supporter")
    assert visible(None, free) is True
    assert visible(None, paid) is True
    set_flag("paywall.enabled", True, actor=None, reason="matrix")
    assert can_read_full(None, free) is True
    assert can_read_full(None, paid) is False
    user = User.objects.create_user("m@localhost", "password12")
    grant_membership(user, days=31, source="test")
    assert can_read_full(user, paid) is True


def test_studio_requires_login(client):
    r = client.get("/studio/")
    assert r.status_code == 302
    assert "/login" in r["Location"]
    user = User.objects.create_user("ed@localhost", "password12", staff_role="editor", is_staff=True)
    client.force_login(user)
    assert client.get("/studio/").status_code == 200
    assert client.get("/admin/flags").status_code == 403
    admin = User.objects.create_superuser("admin@localhost", "password12")
    client.force_login(admin)
    assert client.get("/admin/flags").status_code == 200
    r = client.get("/ops/flags")
    assert r.status_code == 302
    assert r["Location"] == "/admin/flags"


def test_reader_cannot_silently_enter_admin(client):
    reader = User.objects.create_user("reader@localhost", "password12")
    client.force_login(reader)
    r = client.get("/admin/")
    assert r.status_code == 403
    assert "员工" in r.content.decode()


def test_staff_login_totp_two_step(client):
    import pyotp

    from accounts.models import TotpDevice

    admin = User.objects.create_superuser("boss@localhost", "password12")
    secret = pyotp.random_base32()
    TotpDevice.objects.create(user=admin, secret=secret, confirmed=True)
    r = client.post("/login", {"email": "boss@localhost", "password": "password12", "next": "/admin/"})
    assert r.status_code == 200
    assert "验证码" in r.content.decode()
    assert client.session.get("pending_totp_uid") == admin.id
    r = client.post("/login", {"totp": pyotp.TOTP(secret).now(), "next": "/admin/"})
    assert r.status_code == 302
    assert r["Location"] == "/admin/"
    assert client.get("/admin/").status_code == 200


def test_public_extras(client):
    from content.models import GlossaryTerm
    from news.models import Issue

    GlossaryTerm.objects.create(term="Token", definition="计费单位。", body="中文大约一两字一个。")
    Issue.objects.create(
        slug="daily-2026-09-15",
        kind="daily",
        title="早报 2026-09-15",
        status="published",
        body_md="x",
        html="<p>x</p>",
        items=[{"title": "一条", "url": "/news"}],
    )
    LearningPath.objects.create(slug="doc-qa", title="文档问答", summary="路径", status="published")
    unit = _node(slug="minimal-rag", kind="unit", track="doc-qa")
    from graph.models import PathItem

    path = LearningPath.objects.get(slug="doc-qa")
    PathItem.objects.create(path=path, unit_index=1, title=unit.title, goal="能跑通", node=unit)
    assert client.get("/glossary/Token").status_code == 200
    assert client.get("/digest/daily/2026-09-15").status_code == 200
    assert client.get("/learn/doc-qa/minimal-rag").status_code == 200
    assert client.get("/authors").status_code == 200
    assert client.get("/topics").status_code == 200
    assert client.get("/compare").status_code == 200
    assert client.get("/timeline").status_code == 200
    assert client.get("/rss.xml").status_code == 200
    assert client.get("/rss/news.xml").status_code == 200
    r = client.get(f"/og/{unit.public_id}.png")
    assert r.status_code == 200
    assert r["Content-Type"] == "image/png"


def test_ads_portal_404_when_off(client):
    assert client.get("/ads/").status_code == 404
    assert client.get("/go/not-a-real-id").status_code == 404


def test_generation_logs_and_bounce_unauthorized(client):
    r = client.post("/api/v1/generation-logs", data={"slug": "x", "log": {}}, content_type="application/json")
    assert r.status_code == 401
    r = client.post("/api/v1/webhooks/mail-bounce", data={"email": "a@b.c"}, content_type="application/json")
    assert r.status_code == 401


def test_studio_editor_and_admin_pages(client):
    pub = _publisher()
    client.force_login(pub)
    r = client.post(
        "/studio/editor",
        {
            "title": "机审草稿标题足够长了",
            "slug": "studio-draft",
            "kind": "concept",
            "level": "L1",
            "access": "free",
            "domain": "general",
            "summary": "这是一段超过二十字的摘要，用来过机审门槛。",
            "body_md": "正文。" * 40,
        },
    )
    assert r.status_code == 302
    assert client.get("/studio/editor/studio-draft").status_code == 200
    client.force_login(User.objects.create_superuser("opsadmin@localhost", "password12"))
    assert client.get("/admin/metrics").status_code == 200
    assert client.get("/admin/settings").status_code == 200
    assert client.get("/admin/seo").status_code == 200
    assert client.get("/studio/topics").status_code == 200


def test_bookmark_and_subscribe(client):
    node = _node(slug="book-me")
    user = User.objects.create_user("saver@localhost", "password12")
    client.force_login(user)
    r = client.post(f"/articles/{node.slug}/bookmark")
    assert r.status_code == 302
    from learning.models import Bookmark

    assert Bookmark.objects.filter(user=user, node=node).exists()
    r = client.post("/subscribe", {"email": "saver@localhost"})
    assert r.status_code == 200
    from mail.models import Subscriber

    assert Subscriber.objects.filter(email="saver@localhost").exists()


def test_archived_article_stays(client):
    node = _node(slug="old-piece", status="archived")
    r = client.get(f"/articles/{node.slug}")
    assert r.status_code == 200
    assert "作废" in r.content.decode()
