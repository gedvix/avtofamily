"""Database models describing vehicles and publication workflow."""
from __future__ import annotations

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class TimestampedModel(models.Model):
    """Abstract base with created/updated timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class FeatureCategory(models.Model):
    """Lookup table grouping car features."""

    title = models.CharField("Название", max_length=100)
    slug = models.SlugField("Слаг", max_length=100, unique=True)

    class Meta:
        verbose_name = "Категория особенностей"
        verbose_name_plural = "Категории особенностей"
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


class Feature(models.Model):
    """Describes a single feature such as heated seats."""

    title = models.CharField("Название", max_length=120)
    slug = models.SlugField("Слаг", max_length=120, unique=True)
    category = models.ForeignKey(
        FeatureCategory,
        on_delete=models.CASCADE,
        related_name="features",
        verbose_name="Категория",
    )

    class Meta:
        verbose_name = "Особенность"
        verbose_name_plural = "Особенности"
        ordering = ["category__title", "title"]

    def __str__(self) -> str:
        return self.title


class Car(TimestampedModel):
    """Represents a car that can be published to different channels."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        REVIEW = "review", "На модерации"
        READY = "ready", "Готово к публикации"
        PUBLISHED = "published", "Опубликовано"
        ARCHIVED = "archived", "Архив"

    title = models.CharField("Заголовок", max_length=255)
    slug = models.SlugField("Слаг", max_length=255, unique=True, blank=True)
    vin = models.CharField("VIN", max_length=32, blank=True)
    brand = models.CharField("Марка", max_length=80)
    model_name = models.CharField("Модель", max_length=80)
    generation = models.CharField("Поколение", max_length=80, blank=True)
    manufacture_year = models.PositiveSmallIntegerField("Год выпуска")
    price = models.DecimalField(
        "Цена",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    currency = models.CharField("Валюта", max_length=3, default="BYN")
    mileage_km = models.PositiveIntegerField("Пробег (км)", default=0)
    body_type = models.CharField("Тип кузова", max_length=80, blank=True)
    color = models.CharField("Цвет", max_length=80, blank=True)
    transmission = models.CharField("Трансмиссия", max_length=80, blank=True)
    drive_type = models.CharField("Привод", max_length=80, blank=True)
    fuel_type = models.CharField("Тип топлива", max_length=80, blank=True)
    engine_capacity_l = models.DecimalField(
        "Объем двигателя (л)",
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
    )
    engine_power_hp = models.PositiveIntegerField(
        "Мощность (л.с.)",
        null=True,
        blank=True,
    )
    owners_count = models.PositiveSmallIntegerField(
        "Количество владельцев",
        default=1,
    )
    customs_cleared = models.BooleanField("Растаможен", default=True)
    description = models.TextField("Описание", blank=True)

    contact_name = models.CharField("Контактное лицо", max_length=120)
    contact_phone = models.CharField("Телефон", max_length=30)
    contact_email = models.EmailField("Email", blank=True)

    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    status_changed_at = models.DateTimeField(
        "Изменено", default=timezone.now, editable=False
    )
    published_at = models.DateTimeField(
        "Дата публикации",
        null=True,
        blank=True,
    )

    features = models.ManyToManyField(
        Feature,
        related_name="cars",
        verbose_name="Особенности",
        blank=True,
    )

    class Meta:
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["brand", "model_name"]),
        ]

    def __str__(self) -> str:
        return f"{self.brand} {self.model_name} ({self.manufacture_year})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.brand}-{self.model_name}-{self.vin or self.pk or ''}")
        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        if "update_fields" in kwargs and kwargs["update_fields"]:
            if "status" in kwargs["update_fields"]:
                self.status_changed_at = timezone.now()
        elif self.pk is None or "status" in self.get_dirty_fields():
            self.status_changed_at = timezone.now()
        super().save(*args, **kwargs)

    def get_dirty_fields(self) -> set[str]:
        if not self.pk:
            return {"status"}
        old = Car.objects.get(pk=self.pk)
        changed = set()
        for field in ["status"]:
            if getattr(old, field) != getattr(self, field):
                changed.add(field)
        return changed


class CarImage(TimestampedModel):
    """Image belonging to a car."""

    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Автомобиль",
    )
    image = models.ImageField("Изображение", upload_to="cars/%Y/%m/%d")
    caption = models.CharField("Подпись", max_length=150, blank=True)
    is_primary = models.BooleanField("Основное фото", default=False)
    ordering = models.PositiveSmallIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Фото автомобиля"
        verbose_name_plural = "Фотографии автомобилей"
        ordering = ["ordering", "id"]

    def __str__(self) -> str:
        return f"Фото {self.car}"


class PublicationChannel(models.Model):
    """Platform where a car can be published."""

    slug = models.SlugField("Код", max_length=50, unique=True)
    title = models.CharField("Название", max_length=120)
    description = models.TextField("Описание", blank=True)
    active = models.BooleanField("Активен", default=True)
    integration_notes = models.TextField(
        "Комментарии по интеграции",
        blank=True,
        help_text="Ссылки на API, требования к данным, контакт модераторов",
    )

    class Meta:
        verbose_name = "Канал публикации"
        verbose_name_plural = "Каналы публикации"
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


class PublicationLog(TimestampedModel):
    """Stores history of publications to external channels."""

    class Result(models.TextChoices):
        SUCCESS = "success", "Успех"
        FAILED = "failed", "Ошибка"
        PENDING = "pending", "В обработке"

    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name="publication_logs",
        verbose_name="Автомобиль",
    )
    channel = models.ForeignKey(
        PublicationChannel,
        on_delete=models.PROTECT,
        related_name="publication_logs",
        verbose_name="Канал",
    )
    external_id = models.CharField(
        "Идентификатор на площадке",
        max_length=255,
        blank=True,
    )
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Result.choices,
        default=Result.PENDING,
    )
    error_message = models.TextField("Ошибка", blank=True)
    published_at = models.DateTimeField(
        "Дата публикации на площадке",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Лог публикации"
        verbose_name_plural = "Логи публикаций"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["channel", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.get_status_display()} – {self.car} в {self.channel}"
