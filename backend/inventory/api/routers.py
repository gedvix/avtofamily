"""Router registration helpers for inventory endpoints."""
from __future__ import annotations

from rest_framework.routers import DefaultRouter

from . import viewsets


def register_routes(router: DefaultRouter) -> None:
    """Attach inventory endpoints to the shared router."""

    router.register(r"makes", viewsets.MakeViewSet, basename="make")
    router.register(r"models", viewsets.CarModelViewSet, basename="model")
    router.register(r"cars", viewsets.CarViewSet, basename="car")
    router.register(r"features", viewsets.FeatureViewSet, basename="feature")
    router.register(
        r"publication-channels",
        viewsets.PublicationChannelViewSet,
        basename="publication-channel",
    )
    router.register(
        r"publication-logs",
        viewsets.PublicationLogViewSet,
        basename="publication-log",
    )
