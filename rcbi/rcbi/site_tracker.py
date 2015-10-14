import email.utils as eut
import datetime
import json
import logging
import os.path
from scrapy import signals
from scrapy.exceptions import NotConfigured

logger = logging.getLogger(__name__)

class SiteTracker(object):

  def __init__(self, root):
    self.crawl_start = {}
    self.root_path = root

  @classmethod
  def from_crawler(cls, crawler):
    root = os.path.realpath(crawler.settings["JSON_FILE_DIRECTORY"])
    ext = cls(root)

    # connect the extension object to signals
    crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
    crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)

    # return the extension object
    return ext

  def spider_opened(self, spider):
    self.crawl_start[spider.name] = datetime.datetime.now()

  def spider_closed(self, spider, reason):
    if reason != "finished":
      logger.info("Site not updated because scrape was not completed.")
      return

    if len(spider.allowed_domains) > 1:
      logger.error("Too many allowed domains.")
      return

    fn = os.path.join(self.root_path, "_site/", spider.allowed_domains[0] + ".json")
    site_info = {"version": 1,
                 "last_crawl": None}
    if os.path.isfile(fn):
      with open(fn, "r") as f:
        site_info = json.load(f)
    site_info["last_crawl"] = self.crawl_start[spider.name].isoformat(' ')

    with open(fn, "w") as f:
        f.write(json.dumps(site_info, indent=1, sort_keys=True, separators=(',', ': ')))
