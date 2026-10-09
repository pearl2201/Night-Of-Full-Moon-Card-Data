# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import mimetypes
import os
import re
from urllib.parse import urlparse

from scrapy.pipelines.files import FilesPipeline


def _slugify(value: str) -> str:
    value = re.sub(r"[^\w\-.]", "_", value, flags=re.UNICODE)
    value = re.sub(r"_+", "_", value).strip("_")
    return value


class CardImagePipeline(FilesPipeline):
    """Download each card image and name it after the card.

    `file_urls` is populated by the spider; results are stored under
    ``FILES_STORE`` (``output/images`` by default).
    """

    def file_path(self, request, response=None, info=None, *, item=None):
        key = None
        if item is not None:
            key = item.get("image_name")
        if not key:
            key = os.path.basename(urlparse(request.url).path) or "image"

        base = _slugify(os.path.splitext(key)[0]) or "image"

        # Fandom's image CDN serves WebP regardless of the URL's extension,
        # so derive the extension from the actual response instead.
        ext = ".webp"
        if response is not None:
            ctype = (
                response.headers.get(b"Content-Type", b"")
                .decode("latin-1")
                .split(";")[0]
                .strip()
            )
            ext = mimetypes.guess_extension(ctype) or ".webp"
            if ext == ".jpe":
                ext = ".jpg"

        return f"{base}{ext}"


class CleanupPipeline:
    """Attach the local image path and drop internal pipeline fields."""

    def process_item(self, item, spider=None):
        files = item.get("files") or []
        if files:
            item["image_file"] = files[0].get("path")
        item.pop("file_urls", None)
        item.pop("files", None)
        return item

