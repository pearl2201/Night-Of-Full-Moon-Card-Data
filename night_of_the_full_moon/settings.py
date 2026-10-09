# Scrapy settings for night_of_the_full_moon project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "night_of_the_full_moon"

SPIDER_MODULES = ["night_of_the_full_moon.spiders"]
NEWSPIDER_MODULE = "night_of_the_full_moon.spiders"

ADDONS = {}


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = (
    "night_of_the_full_moon (+https://night-of-the-full-moon.fandom.com/)"
)

# The wiki's robots.txt is itself behind a Cloudflare challenge, so Scrapy
# cannot read it. We only call the public MediaWiki API (/api.php) and the
# image CDN, and throttle politely below.
ROBOTSTXT_OBEY = False

# Concurrency and throttling settings
CONCURRENT_REQUESTS_PER_DOMAIN = 4
DOWNLOAD_DELAY = 0.5

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "night_of_the_full_moon.middlewares.NightOfTheFullMoonSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "night_of_the_full_moon.middlewares.NightOfTheFullMoonDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "night_of_the_full_moon.pipelines.CardImagePipeline": 300,
    "night_of_the_full_moon.pipelines.CleanupPipeline": 400,
}

# Where downloaded card images are stored
FILES_STORE = "output/images"

# Export every scraped card to both JSON and CSV
FEEDS = {
    "output/cards.json": {
        "format": "json",
        "encoding": "utf8",
        "indent": 2,
        "overwrite": True,
    },
    "output/cards.csv": {
        "format": "csv",
        "encoding": "utf8",
        "overwrite": True,
    },
}

# Columns that go into the CSV / JSON, in this order. This also keeps the
# internal FilesPipeline fields (file_urls/files) out of the export.
FEED_EXPORT_FIELDS = [
    "name",
    "info",
    "image_url",
    "card_type",
    "shop_price",
    "stars",
    "effects",
    "playing_cost",
    "page_url",
    "image_name",
    "image_file",
]

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"
