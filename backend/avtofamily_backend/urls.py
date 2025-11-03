"""Main URL configuration for the Avtofamily backend."""
from __future__ import annotations

from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from inventory.api import routers as inventory_routers

router = routers.DefaultRouter()
inventory_routers.register_routes(router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]
