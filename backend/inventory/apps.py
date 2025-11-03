from __future__ import annotations

from django.apps import AppConfig


class InventoryConfig(AppConfig):
    """Application config for inventory domain."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "inventory"
    verbose_name = "Каталог автомобилей"
