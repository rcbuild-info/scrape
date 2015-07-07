# -*- coding: utf-8 -*-

# Scrapy settings for rcbi project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'rcbuild.info'

SPIDER_MODULES = ['rcbi.spiders']
NEWSPIDER_MODULE = 'rcbi.spiders'

DOWNLOAD_DELAY = 0.25

EXTENSIONS = {
    'scrapy.extensions.corestats.CoreStats': 500#,
    #'scrapy.extensions.closespider.CloseSpider': 500,
}
#CLOSESPIDER_PAGECOUNT=100

LOG_LEVEL="INFO"

ITEM_PIPELINES = {
    'rcbi.pipelines.JsonFileMergerPipeline': 800,
}

JSON_FILE_DIRECTORY = "/home/tannewt/code/rcbuild.info-parts"
PART_SKELETON_FILE = "/home/tannewt/code/rcbuild.info-part-skeleton/part.json"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'rcbi (+https://rcbuild.info)'

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware': 1,
}
HTTPCACHE_POLICY = "scrapy.extensions.httpcache.RFC2616Policy"
HTTPCACHE_ENABLED = True
