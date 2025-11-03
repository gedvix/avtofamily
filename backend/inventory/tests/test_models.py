from __future__ import annotations

from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.utils.text import slugify
from PIL import Image
from PIL import Image
from django.utils import timezone

from inventory import models


def create_make_and_model(make_title: str, model_title: str) -> tuple[models.Make, models.CarModel]:
    make = models.Make.objects.create(title=make_title, slug=slugify(make_title))
    model = models.CarModel.objects.create(
        make=make,
        title=model_title,
        slug=slugify(model_title),
    )
    return make, model


def test_car_status_timestamp_updates(db):
    make, model = create_make_and_model("Audi", "A4")
    car = models.Car.objects.create(
        title="Test Car",
        make=make,
        model=model,
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
    make, model = create_make_and_model("BMW", "X5")
    car = models.Car.objects.create(
        title="Test Car",
        make=make,
        model=model,
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


def generate_test_image(width=4000, height=3000, color=(255, 0, 0), image_format="JPEG") -> bytes:
    buffer = BytesIO()
    image = Image.new("RGB", (width, height), color)
    image.save(buffer, format=image_format)
    buffer.seek(0)
    return buffer.read()


def test_car_image_is_optimised_on_save(db, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path

    make, model = create_make_and_model("Audi", "Q7")
    car = models.Car.objects.create(
        title="Optimised Car",
        make=make,
        model=model,
    car = models.Car.objects.create(
        title="Optimised Car",
        brand="Audi",
        model_name="Q7",
        manufacture_year=2021,
        price=50000,
        currency="USD",
        mileage_km=5000,
        contact_name="Manager",
        contact_phone="+375291112233",
    )

    upload = SimpleUploadedFile(
        "big-photo.png",
        generate_test_image(image_format="PNG"),
        content_type="image/png",
    )

    car_image = models.CarImage.objects.create(car=car, image=upload)

    car_image.image.open()
    with Image.open(car_image.image) as processed:
        assert max(processed.size) <= 2560
        assert processed.format == "JPEG"

    assert car_image.image.name.endswith(".jpg")


def test_only_single_primary_image_is_kept(db, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path

    make, model = create_make_and_model("Tesla", "Model S")
    car = models.Car.objects.create(
        title="Primary Car",
        make=make,
        model=model,
    car = models.Car.objects.create(
        title="Primary Car",
        brand="Tesla",
        model_name="Model S",
        manufacture_year=2022,
        price=90000,
        currency="USD",
        mileage_km=1000,
        contact_name="Manager",
        contact_phone="+375291112233",
    )

    first_image = models.CarImage.objects.create(
        car=car,
        image=SimpleUploadedFile("first.jpg", generate_test_image(1200, 800)),
        is_primary=True,
    )

    second_image = models.CarImage.objects.create(
        car=car,
        image=SimpleUploadedFile("second.jpg", generate_test_image(1200, 800)),
        is_primary=True,
    )

    first_image.refresh_from_db()
    second_image.refresh_from_db()

    assert second_image.is_primary is True
    assert first_image.is_primary is False
