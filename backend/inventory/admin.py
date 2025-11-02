"""Admin registrations for inventory models."""
from __future__ import annotations

from django.contrib import admin
from django.utils.html import format_html

from . import models


class CarImageInline(admin.TabularInline):
    model = models.CarImage
    extra = 1
    fields = ("preview", "image", "caption", "is_primary", "ordering")
    readonly_fields = ("preview",)

    @admin.display(description="Превью")
    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="max-height: 120px; border-radius: 6px;" />',
                obj.image.url,
            )
        return "—"


@admin.register(models.Car)
class CarAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "brand",
        "model_name",
        "manufacture_year",
        "price",
        "status",
        "updated_at",
    )
    list_filter = (
        "status",
        "brand",
        "model_name",
        "manufacture_year",
        "fuel_type",
        "body_type",
    )
    search_fields = (
        "title",
        "brand",
        "model_name",
        "vin",
        "description",
    )
    inlines = [CarImageInline]
    prepopulated_fields = {"slug": ("brand", "model_name", "manufacture_year")}
    autocomplete_fields = ("features",)
    filter_horizontal = ("features",)
    fieldsets = (
        ("Основная информация", {
            "fields": (
                "title",
                "slug",
                "vin",
                "status",
                "brand",
                "model_name",
                "generation",
                "manufacture_year",
                "price",
                "currency",
                "mileage_km",
                "description",
            )
        }),
        ("Технические характеристики", {
            "fields": (
                "body_type",
                "color",
                "transmission",
                "drive_type",
                "fuel_type",
                "engine_capacity_l",
                "engine_power_hp",
                "owners_count",
                "customs_cleared",
                "features",
            )
        }),
        ("Контакты", {
            "fields": (
                "contact_name",
                "contact_phone",
                "contact_email",
            )
        }),
        ("Публикация", {
            "fields": (
                "published_at",
                "status_changed_at",
            )
        }),
    )
    readonly_fields = ("status_changed_at", "published_at", "created_at", "updated_at")


@admin.register(models.Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ("title", "category")
    list_filter = ("category",)
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(models.FeatureCategory)
class FeatureCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(models.PublicationChannel)
class PublicationChannelAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "active")
    list_filter = ("active",)
    search_fields = ("title", "slug")


@admin.register(models.PublicationLog)
class PublicationLogAdmin(admin.ModelAdmin):
    list_display = (
        "car",
        "channel",
        "status",
        "external_id",
        "published_at",
        "created_at",
    )
    list_filter = ("channel", "status")
    search_fields = ("car__title", "external_id", "error_message")
    autocomplete_fields = ("car", "channel")
    readonly_fields = ("created_at", "updated_at")
