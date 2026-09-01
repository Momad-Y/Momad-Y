#!/usr/bin/env python3
"""Crop each featured project's source image to a uniform 16:9 thumbnail.

GitHub's markdown sanitizer strips `style` attributes, so CSS object-fit
can't normalize aspect ratios in a README, and setting both width and
height on <img> would stretch the image. Pre-cropping to a fixed ratio and
committing the result is the only way to get a visually uniform card grid.
"""
import io
import os

import requests
from PIL import Image

TARGET_RATIO = 16 / 9
OUTPUT_WIDTH = 800
OUTPUT_DIR = "assets/projects"

SOURCES = {
    "lyric-logic": "Lyric-Logic/main/imgs/web-app-example.png",
    "euc-rag-agent": "EUC-RAG-Agent/main/imgs/webapp.png",
    "nexchat": "NexChat/main/imgs/image_captioning_screenshot.png",
    "opticompanion": "OptiCompanion/main/images/Nothing-Phone-1-Home-Page-Mockup.png",
    "celebrity-cnn": "Celebrity-look-a-like-CNN/main/images/Real-Time Example.png",
    "chess-robots": "Magnus-Hikaru-Chess-Robots/main/media/hikaru/hikaru-rig-hero.png",
}


def crop_to_ratio(image):
    """Center-crop to TARGET_RATIO, then downscale to OUTPUT_WIDTH."""
    width, height = image.size
    if width / height > TARGET_RATIO:
        new_width = int(height * TARGET_RATIO)
        left = (width - new_width) // 2
        image = image.crop((left, 0, left + new_width, height))
    else:
        new_height = int(width / TARGET_RATIO)
        top = (height - new_height) // 2
        image = image.crop((0, top, width, top + new_height))
    return image.resize((OUTPUT_WIDTH, int(OUTPUT_WIDTH / TARGET_RATIO)), Image.LANCZOS)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for name, path in SOURCES.items():
        url = f"https://raw.githubusercontent.com/Momad-Y/{path}".replace(" ", "%20")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content)).convert("RGB")
        destination = os.path.join(OUTPUT_DIR, f"{name}.png")
        crop_to_ratio(image).save(destination, optimize=True)
        print(f"wrote {destination}")


if __name__ == "__main__":
    main()
