from cloudfeaster import spider


class Spider(spider.Spider):

    @classmethod
    def get_metadata(cls):
        return {
            'url': 'https://pypi.python.org/pypi',
        }

    def crawl(self, browser):
        return spider.CrawlResponseOk({})
