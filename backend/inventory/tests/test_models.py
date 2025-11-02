from __future__ import annotations

from django.utils import timezone

from inventory import models


def test_car_status_timestamp_updates(db):
    car = models.Car.objects.create(
        title="Test Car",
        brand="Audi",
        model_name="A4",
        manufacture_year=2020,
        price=25000,
        currency="USD",
        mileage_km=10000,
        contact_name="Manager",
        contact_phone="+375291112233",
    )
    original_changed = car.status_changed_at

    car.status = models.Car.Status.PUBLISHED
    car.save()

    car.refresh_from_db()
    assert car.status == models.Car.Status.PUBLISHED
    assert car.published_at is not None
    assert car.status_changed_at >= original_changed
    assert car.status_changed_at <= timezone.now()


def test_publication_log_str(db):
    car = models.Car.objects.create(
        title="Test Car",
        brand="BMW",
        model_name="X5",
        manufacture_year=2019,
        price=30000,
        currency="USD",
        mileage_km=15000,
        contact_name="Manager",
        contact_phone="+375291112233",
    )
    channel = models.PublicationChannel.objects.create(slug="av-by", title="av.by")
    log = models.PublicationLog.objects.create(car=car, channel=channel)

    assert str(log) == f"В обработке – {car} в {channel}"
