from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

import users.views
import www.views
from catalog.sitemap import CourseSitemap
from documents.sitemap import DocumentSitemap

sitemaps = {
    "course": CourseSitemap,
    "document": DocumentSitemap,
}

urlpatterns = [
    path("", www.views.index, name="index"),
    path(
        "finder/<slug:id>/<slug:category_slug>/<str:mobile>",
        www.views.finder_turbo,
        name="finder_turbo",
    ),
    path(
        "finder/<slug:action>/<slug:course_slug>",
        www.views.set_follow_course,
        name="set_course_follow",
    ),
    path("search/", include("search.urls")),
    path("catalog/", include("catalog.urls")),
    path("documents/", include("documents.urls")),
    path("users/", include("users.urls")),
    path("admin/", admin.site.urls),
    path("api/", include("www.rest_urls")),
    path("syslogin", LoginView.as_view(template_name="syslogin.html"), name="syslogin"),
    path("login", users.views.login_view, name="login"),
    path("auth-ulb", users.views.auth_ulb, name="auth-ulb"),
    path("logout", LogoutView.as_view(next_page="/"), name="logout"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]

handler400 = "www.error.error400"
handler403 = "www.error.error403"
handler404 = "www.error.error404"
handler500 = "www.error.error500"


if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar

    urlpatterns.extend(
        [
            path("__debug__/", include(debug_toolbar.urls)),
        ]
    )
