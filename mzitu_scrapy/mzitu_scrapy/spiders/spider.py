from scrapy import Request
from scrapy.spider import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from mzitu_scrapy.items import MzituScrapyItem


class Spider(CrawlSpider):
    name = 'mzitu'
    allowed_domains = ['mzitu.com']
    start_urls = ['http://www.mzitu.com/']
    rules = (
        Rule(LinkExtractor(allow=('http://www.mzitu.com/\d{1,6}',), deny=('http://www.mzitu.com/\d{1,6}/\d{1,6}')),
             callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        """
        :param response: 下载器返回的response
        :return:
        """
        meta = {}
        # max_num为页面最后一张图片的位置
        max_num = response.xpath(
            "descendant::div[@class='main']/div[@class='content']/div[@class='pagenavi']/a[last()-1]/span/text()").extract_first(
            default="N/A")
        meta['name'] = response.xpath("./*//div[@class='main']/div[1]/h2/text()").extract_first(default="N/A")
        meta['url'] = response.url
        for num in range(1, int(max_num)):
            page_url = response.url + '/' + str(num)
            self.logger.warning(page_url)
            yield Request(page_url, callback=self.img_url, meta=meta)

    def img_url(self, response, ):
        """取出图片URL 并添加进self.img_urls列表中
        :param response:
        :param img_url 为每张图片的真实地址
        """
        item = MzituScrapyItem()
        item['name'] = response.meta['name']
        item['url'] = response.meta['url']
        item['image_urls'] = response.xpath("descendant::div[@class='main-image']/descendant::img/@src").extract_first()
        # for img_url in img_urls:
        #     self.img_urls.append(img_url)
        # item['image_urls'] = self.img_urls
        yield item


#  way 1
if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    # process = CrawlerProcess({
    #     'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    # })
    process = CrawlerProcess(get_project_settings())
    process.crawl(Spider)
    process.start()  # the script will block here until the crawling is finished