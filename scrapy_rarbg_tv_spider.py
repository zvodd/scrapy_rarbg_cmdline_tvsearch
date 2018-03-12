# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.http.cookies import CookieJar
import logging
from pprint import pprint, pformat

logger = logging.getLogger(__name__)


class RarbgTvSpider(scrapy.Spider):
    name = 'rarbg_tv'
    base_domain = 'http://rarbg.to'


    def __init__(self, *args, **kwargs):
        super(RarbgTvSpider, self).__init__(*args, **kwargs)

        showname = kwargs['showname']
        tmp = showname.split(' ')
        tmp = ('+').join(tmp)

        self.proxy = kwargs['proxy']
        logger.info(
            "Spider '{}' setting proxy to '{}'".format(self, self.proxy))

        self.search_term = tmp

        self.proxy_check_run = kwargs.get('proxy_check_run', False)


    def start_requests(self):
        if self.proxy_check_run:
            yield self.create_request("http://freegeoip.net/json/", callback=self.check_proxy_parse)
        else:
            url = '{}/torrents.php?search={}&category%5B%5D=18&category%5B%5D=41&category%5B%5D=49'.format(
                self.base_domain, self.search_term)
            yield self.create_request(url)


    def check_proxy_parse(self, response):
        logger.info("Response Body:\n{}\n".format(pformat(response.body)))
        return


    def parse(self, response):
        places = list(set([response.request.url] +
                          response.request.meta.get('redirect_urls', [])))
        if any(map(lambda x: x.find("threat_defence.php") > -1, places)):
            logger.info("Got caught by the rate limiter!!")
            logger.info("Urls: {}".format(places))
            logger.info("Response Body:\n{}\n".format(pformat(response.body)))

        table_ents = response.xpath(
            "//table[@class='lista2t']/.//tr[@class='lista2']/td[2]/a[1]")
        for torrent in table_ents:
            yield {"torrent": {"title": torrent.xpath('@title').extract_first(),
                               "href": torrent.xpath('@href').extract_first()}}

        # np = response.xpath("//div[@id='pager_links']/a")
        # if len(np) > 1:
        #     np = np[-1]
        # else:
        #     np = None
        # if np and np.xpath('text()').extract_first() is not '»':
        #     nextPageLink = np.xpath('@href').extract_first()
        #     nextPageLink = "{}{}".format(self.base_domain, nextPageLink)
        np = response.xpath('//a[@title="next page"]')
        if np and np.xpath('text()').extract_first() is '»':
            nextPageLink = np.xpath('@href').extract_first()
            nextPageLink = "{}{}".format(self.base_domain, nextPageLink)
            yield self.create_request(nextPageLink, response)


    def create_request(self, url, response=None, **kwargs):
        if response is not None:
            cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
            cookieJar.extract_cookies(response, response.request)
        else:
            cookieJar = CookieJar()
        kwargs.update(meta={'dont_merge_cookies': True,
                            'cookie_jar': cookieJar})
        request = Request(url, **kwargs)
        cookieJar.add_cookie_header(request)
        return request
