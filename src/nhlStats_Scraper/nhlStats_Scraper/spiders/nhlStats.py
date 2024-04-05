import scrapy


class NHLStatsSpider(scrapy.Spider):
    name = "NHLStats"
    allowed_domains = ["nhl.com/stats"]
    start_urls = ["https://nhl.com/stats/teams"]

    def parse(self, response):
        pass