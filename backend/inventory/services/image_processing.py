"""Utilities for normalising and optimising uploaded vehicle images."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path
from PIL import Image, ImageOps

from django.core.files.base import ContentFile

MAX_IMAGE_SIZE = (2560, 2560)
JPEG_QUALITY = 85


def optimise_car_image(file_obj) -> tuple[str, ContentFile]:
    """Return an optimised JPEG version of the uploaded file.

    The function performs the following adjustments:

    * honours EXIF orientation to avoid rotated previews;
    * limits the longest image edge to 2560px to reduce payload size while
      keeping enough resolution for marketplaces;
    * converts the picture to RGB and stores it as a high-quality JPEG.

    Parameters
    ----------
    file_obj:
        An instance of ``File`` or ``InMemoryUploadedFile`` coming from
        ``ImageField``.

    Returns
    -------
    tuple[str, ContentFile]
        Filename (with .jpg extension) and the in-memory optimised payload.
    """

    original_name = getattr(file_obj, "name", "car-image")
    base_name = Path(original_name).stem

    file_obj.seek(0)
    image = Image.open(file_obj)

    # Apply orientation and convert for uniform encoding
    image = ImageOps.exif_transpose(image)
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")

    image.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)

    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    image.close()
    buffer.seek(0)

    optimised_name = f"{base_name}.jpg"
    return optimised_name, ContentFile(buffer.read(), name=optimised_name)

