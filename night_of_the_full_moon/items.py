# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item


class NightOfTheFullMoonItem(Item):
    """A single Night of the Full Moon card."""

    # Required
    name = Field()

    # Requested fields (may be missing on some cards)
    info = Field()
    image_url = Field()
    card_type = Field()
    shop_price = Field()
    stars = Field()
    effects = Field()

    # Bonus field found in the same infobox
    playing_cost = Field()

    # Convenience / local image bookkeeping
    page_url = Field()
    image_name = Field()
    image_file = Field()

    # Used internally by the FilesPipeline (removed before export)
    file_urls = Field()
    files = Field()
