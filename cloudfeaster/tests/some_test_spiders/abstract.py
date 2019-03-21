from cloudfeaster import spider


class BaseSpider(spider.Spider):
    pass


class Spider(BaseSpider):

    @classmethod
    def get_metadata(cls):
        return {
            'url': 'https://pypi.python.org/pypi',
        }

    def crawl(self, browser):
        return spider.CrawlResponseOk({})
