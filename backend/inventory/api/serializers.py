"""Serializers for inventory API endpoints."""
from __future__ import annotations

from rest_framework import serializers

from .. import models


class FeatureCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FeatureCategory
        fields = ["id", "title", "slug"]


class FeatureSerializer(serializers.ModelSerializer):
    category = FeatureCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=models.FeatureCategory.objects.all(),
        source="category",
        write_only=True,
    )

    class Meta:
        model = models.Feature
        fields = ["id", "title", "slug", "category", "category_id"]


class CarImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CarImage
        fields = [
            "id",
            "image",
            "caption",
            "is_primary",
            "ordering",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class CarSerializer(serializers.ModelSerializer):
    images = CarImageSerializer(many=True, required=False)
    features = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=models.Feature.objects.all(),
        required=False,
    )

    class Meta:
        model = models.Car
        fields = [
            "id",
            "title",
            "slug",
            "vin",
            "brand",
            "model_name",
            "generation",
            "manufacture_year",
            "price",
            "currency",
            "mileage_km",
            "body_type",
            "color",
            "transmission",
            "drive_type",
            "fuel_type",
            "engine_capacity_l",
            "engine_power_hp",
            "owners_count",
            "customs_cleared",
            "description",
            "contact_name",
            "contact_phone",
            "contact_email",
            "status",
            "status_changed_at",
            "published_at",
            "features",
            "images",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status_changed_at", "published_at", "created_at", "updated_at"]

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        features = validated_data.pop("features", [])
        car = super().create(validated_data)
        if features:
            car.features.set(features)
        self._sync_images(car, images_data)
        return car

    def update(self, instance, validated_data):
        images_data = validated_data.pop("images", None)
        features = validated_data.pop("features", None)
        car = super().update(instance, validated_data)
        if features is not None:
            car.features.set(features)
        if images_data is not None:
            self._sync_images(car, images_data)
        return car

    def _sync_images(self, car: models.Car, images_data: list[dict]) -> None:
        existing = {img.id: img for img in car.images.all()}
        keep_ids = []
        for image in images_data:
            image_id = image.get("id")
            if image_id and image_id in existing:
                for attr, value in image.items():
                    if attr != "id":
                        setattr(existing[image_id], attr, value)
                existing[image_id].save()
                keep_ids.append(image_id)
            else:
                models.CarImage.objects.create(car=car, **image)
        to_delete = [img_id for img_id in existing if img_id not in keep_ids]
        if to_delete:
            models.CarImage.objects.filter(id__in=to_delete).delete()


class PublicationChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PublicationChannel
        fields = ["id", "slug", "title", "description", "active", "integration_notes"]


class PublicationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PublicationLog
        fields = [
            "id",
            "car",
            "channel",
            "external_id",
            "status",
            "error_message",
            "published_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
