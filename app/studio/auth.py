from urllib.parse import quote

from django.shortcuts import redirect, render


def staff_required(role_action: str):
    def wrap(view):
        def inner(request, *args, **kwargs):
            nxt = quote(request.path)
            if not request.user.is_authenticated:
                return redirect(f"/login?staff=1&next={nxt}")
            from access.services import can

            if not can(request.user, role_action):
                return render(request, "accounts/staff_denied.html", {"next": request.path}, status=403)
            return view(request, *args, **kwargs)

        return inner

    return wrap
