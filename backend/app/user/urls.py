from __future__ import annotations

from app.user.views import router

urlpatterns = [
    *router.urls,
]