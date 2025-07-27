import re

from django.conf import settings
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path, re_path, reverse
from django.views.static import serve


def index(request):
    """Index page with links to the admin and API apps"""
    return JsonResponse(
        {
            "admin": request.build_absolute_uri(reverse("admin:index")),
            "api": request.build_absolute_uri(reverse("api-root")),
        }
    )


urlpatterns = [
    path("", index, name="index"),
    path("api/", include("api.urls")),
    path("admin/", admin.site.urls),
]

# Adding static files when serving in production, not ideal, but this is an exercise
# Code from `django.conf.urls.static:static`
if not settings.DEBUG:
    urlpatterns += [
        re_path(
            r"^%s(?P<path>.*)$" % re.escape(settings.STATIC_URL.lstrip("/")),
            serve,
            kwargs={"document_root": settings.STATIC_ROOT},
        ),
    ]
