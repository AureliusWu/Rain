"""Decode raster assets and describe their display pixels, independently of PNG compression."""
import struct
from tools.asset_paths import sha256


def image_metadata(image):
    image.load()
    rgba = image.convert("RGBA")
    return {"width": image.width, "height": image.height, "mode": image.mode,
            "format": image.format or "PNG", "has_alpha": "A" in image.getbands(),
            "pixel_sha256": sha256(struct.pack(">II", *image.size) + rgba.tobytes())}
