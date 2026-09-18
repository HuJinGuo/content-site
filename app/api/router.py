from django.http import HttpRequest
from ninja import NinjaAPI, Schema

api = NinjaAPI(title="ai.nornless.com", urls_namespace="api")


class HealthOut(Schema):
    ok: bool
    flags_version: int


def _bearer_ok(request: HttpRequest) -> bool:
    from django.conf import settings

    token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    return bool(settings.IMPORT_TOKEN) and token == settings.IMPORT_TOKEN


@api.get("/health", response=HealthOut)
def health(request: HttpRequest):
    from core.services import snapshot

    flags = snapshot()
    return {"ok": True, "flags_version": flags.version}


class ImportIn(Schema):
    sha: str
    files: list[str] = []


@api.post("/import")
def import_api(request: HttpRequest, body: ImportIn):
    if not _bearer_ok(request):
        return api.create_response(request, {"code": "unauthorized", "message": "invalid token"}, status=401)

    from django.conf import settings

    from content.models import import_markdown

    imported = []
    for rel in body.files:
        path = settings.REPO_DIR / rel
        if path.exists():
            node = import_markdown(path)
            imported.append(node.slug)
    return {"ok": True, "imported": imported}


class GenerationLogIn(Schema):
    slug: str
    log: dict


@api.post("/generation-logs")
def generation_logs(request: HttpRequest, body: GenerationLogIn):
    if not _bearer_ok(request):
        return api.create_response(request, {"code": "unauthorized", "message": "invalid token"}, status=401)
    from content.models import ContentNode

    node = ContentNode.all_objects.filter(slug=body.slug).first()
    if node is None:
        return api.create_response(request, {"code": "not_found", "message": "slug"}, status=404)
    node.generation_log = body.log
    node.save(update_fields=["generation_log", "updated_at"])
    return {"ok": True, "slug": node.slug}


class BounceIn(Schema):
    email: str = ""
    email_hash: str = ""
    event: str = "bounce"


@api.post("/webhooks/mail-bounce")
def mail_bounce(request: HttpRequest, body: BounceIn):
    import hashlib

    from django.conf import settings

    from mail.models import Subscriber, Suppression

    secret = settings.MAIL_WEBHOOK_SECRET
    got = request.headers.get("X-Webhook-Secret") or request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    if not secret or got != secret:
        return api.create_response(request, {"code": "unauthorized", "message": "invalid signature"}, status=401)
    digest = body.email_hash or (hashlib.sha256(body.email.lower().encode()).hexdigest() if body.email else "")
    if not digest:
        return api.create_response(request, {"code": "validation", "message": "email required"}, status=422)
    Suppression.objects.get_or_create(email_hash=digest, defaults={"reason": body.event or "bounce"})
    Subscriber.objects.filter(email_hash=digest).update(status="bounced")
    return {"ok": True}
