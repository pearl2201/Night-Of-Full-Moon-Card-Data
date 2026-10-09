"""Spider that crawls every card in ``Category:Card`` on the
Night of the Full Moon Fandom wiki.

Why the MediaWiki API instead of scraping the wiki HTML pages?
--------------------------------------------------------------
The human-facing wiki pages (``/wiki/<Card>`` and ``/wiki/Category:Card``) are
protected by a Cloudflare JavaScript challenge, so plain HTTP clients (and
Scrapy) receive a "Just a moment..." interstitial instead of the real HTML.

Fandom's public MediaWiki API (``/api.php``) is *not* behind that challenge and
``action=parse`` returns the very same rendered HTML the browser would get -
including the ``<aside class="portable-infobox">`` and the description
paragraphs. So we get identical data, robustly.

The category's next/previous pagination is handled transparently via the API's
``continue`` parameter (``cmcontinue``).
"""

from urllib.parse import urlencode

import scrapy

from night_of_the_full_moon.items import NightOfTheFullMoonItem

API = "https://night-of-the-full-moon.fandom.com/api.php"
WIKI_BASE = "https://night-of-the-full-moon.fandom.com/wiki/"

# data-source attribute  ->  item field
SOURCE_MAP = {
    "card_type": "card_type",
    "card_price": "shop_price",
    "stars": "stars",
    "effects": "effects",
    "effect": "effects",
    "cost": "playing_cost",
}

# infobox label -> item field (fallback when data-source is missing/renamed)
LABEL_MAP = {
    "card type": "card_type",
    "shop prize": "shop_price",
    "shop price": "shop_price",
    "stars": "stars",
    "effects": "effects",
    "playing cost": "playing_cost",
}


def _clean(text: str | None) -> str | None:
    if text is None:
        return None
    text = " ".join(text.split())
    return text or None


class CardsSpider(scrapy.Spider):
    name = "cards"
    allowed_domains = [
        "night-of-the-full-moon.fandom.com",
        "static.wikia.nocookie.net",
    ]

    def __init__(self, category: str = "Category:Card", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = category

    # ------------------------------------------------------------------ #
    # Category listing (paginated through the API `continue` mechanism)
    # ------------------------------------------------------------------ #
    async def start(self):
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": self.category,
            "cmlimit": "500",
            "format": "json",
            "formatversion": "2",
        }
        yield scrapy.Request(
            f"{API}?{urlencode(params)}",
            callback=self.parse_category,
            dont_filter=True,
        )

    def parse_category(self, response):
        data = response.json()
        members = data.get("query", {}).get("categorymembers", [])
        for member in members:
            if member.get("ns") != 0:  # skip sub-categories / files / etc.
                continue
            title = member["title"]
            params = {
                "action": "parse",
                "page": title,
                "prop": "text",
                "format": "json",
                "formatversion": "2",
            }
            yield scrapy.Request(
                f"{API}?{urlencode(params)}",
                callback=self.parse_card,
                cb_kwargs={"title": title},
            )

        # Follow pagination (equivalent to "next" on the category page).
        cont = data.get("continue")
        if cont:
            params = {
                "action": "query",
                "list": "categorymembers",
                "cmtitle": self.category,
                "cmlimit": "500",
                "format": "json",
                "formatversion": "2",
                "cmcontinue": cont["cmcontinue"],
            }
            yield scrapy.Request(
                f"{API}?{urlencode(params)}",
                callback=self.parse_category,
                dont_filter=True,
            )

    # ------------------------------------------------------------------ #
    # Individual card
    # ------------------------------------------------------------------ #
    def parse_card(self, response, title):
        parsed = response.json().get("parse", {})
        html = parsed.get("text", "")
        if not html:
            self.logger.warning("No HTML for card %r", title)
            return

        sel = scrapy.Selector(text=html)
        item = NightOfTheFullMoonItem()
        item["name"] = title
        item["page_url"] = WIKI_BASE + title.replace(" ", "_")

        aside = sel.css("aside.portable-infobox")
        if aside:
            # Card name (infobox title)
            name = _clean(" ".join(aside.css("h2.pi-title ::text").getall()))
            if name:
                item["name"] = name

            # Card image
            img = aside.css("figure.pi-image img")
            link = aside.css("figure.pi-image a::attr(href)").get()
            if link:
                item["image_url"] = link.split("/revision/")[0]
                item["file_urls"] = [item["image_url"]]
            if img:
                item["image_name"] = (
                    img.attrib.get("data-image-key")
                    or img.attrib.get("data-image-name")
                )

            # Infobox key/value rows
            for row in aside.css("div.pi-data"):
                value = _clean(row.css("div.pi-data-value").xpath("string(.)").get())
                if not value:
                    continue
                source = (row.attrib.get("data-source") or "").strip().lower()
                label = _clean(" ".join(row.css("h3.pi-data-label ::text").getall()))
                field = SOURCE_MAP.get(source) or LABEL_MAP.get((label or "").lower())
                if field and not item.get(field):
                    item[field] = value

        # "Info" - the first non-empty description paragraph outside the infobox.
        for p in sel.css("div.mw-parser-output > p"):
            text = _clean(p.xpath("string(.)").get())
            if text:
                item["info"] = text
                break

        yield item
