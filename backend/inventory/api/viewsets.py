"""REST API endpoints for the inventory domain."""
from __future__ import annotations

from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .. import models
from . import serializers


class MakeViewSet(viewsets.ModelViewSet):
    queryset = models.Make.objects.all()
    serializer_class = serializers.MakeSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "slug"]
    ordering_fields = ["title"]
    ordering = ["title"]


class CarModelViewSet(viewsets.ModelViewSet):
    queryset = models.CarModel.objects.select_related("make").all()
    serializer_class = serializers.CarModelSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ["make"]
    search_fields = ["title", "slug", "make__title"]
    ordering_fields = ["title", "make__title"]
    ordering = ["make__title", "title"]


class FeatureViewSet(viewsets.ModelViewSet):
    queryset = models.Feature.objects.select_related("category").all()
    serializer_class = serializers.FeatureSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "slug"]
    ordering_fields = ["title", "category__title"]
    ordering = ["category__title", "title"]


class PublicationChannelViewSet(viewsets.ModelViewSet):
    queryset = models.PublicationChannel.objects.all()
    serializer_class = serializers.PublicationChannelSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "slug"]
    ordering_fields = ["title", "active"]
    ordering = ["title"]


class PublicationLogViewSet(viewsets.ModelViewSet):
    queryset = (
        models.PublicationLog.objects.select_related("car", "channel")
        .order_by("-created_at")
        .all()
    )
    serializer_class = serializers.PublicationLogSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["channel", "status", "car"]
    search_fields = ["external_id", "error_message", "car__title"]
    ordering_fields = ["created_at", "published_at"]


class CarViewSet(viewsets.ModelViewSet):
    queryset = (
        models.Car.objects.select_related("make", "model")
        .prefetch_related(
            "features",
            Prefetch("images", queryset=models.CarImage.objects.order_by("ordering", "id")),
        )
        .all()
    )
    serializer_class = serializers.CarSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "status",
        "make",
        "model",
        "manufacture_year",
        "fuel_type",
        "body_type",
        "drive_type",
        "customs_cleared",
    ]
    search_fields = ["title", "make__title", "model__title", "vin", "description"]
    ordering_fields = ["created_at", "manufacture_year", "price", "mileage_km"]
    ordering = ["-created_at"]

