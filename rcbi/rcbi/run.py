import argparse

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

ALL_SPIDERS = {"small": ["infinitefpv", "voodooquads", "shendrones", "demonframes", "lizardrc", "miniquadfpv", "hoverthings", "impulserc", "fpvreconn", "armattan", "dronematters", "flitetest", "boltrceu", "miniquadbros"],
               "medium": ["multirotorparts", "buzzhobbies", "flyingrobot", "uavobjects", "rotorgeeks", "fpvmodel", "multirotormania", "readytoflyquads", "flyduino", "banggood", "getfpv"],
               "large": ["readymaderc", "multirotorsuperstore", "liftrc", "boltrc", "myrcmart"],
               "huge": ["hobbyking", "innov8tivedesigns"]}

parser = argparse.ArgumentParser()
parser.add_argument("spider_size")
args = parser.parse_args()

process = CrawlerProcess(get_project_settings())

spiders = []
if args.spider_size == "all":
  for size in ALL_SPIDERS:
    spiders.extend(ALL_SPIDERS[size])
else:
  spiders = ALL_SPIDERS[args.spider_size]

for spider in spiders:
  process.crawl(spider)
process.start()
