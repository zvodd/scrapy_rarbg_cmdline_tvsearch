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
        search_uri_frag = showname.split(' ')
        search_uri_frag = ('+').join(search_uri_frag)

        self.proxy = kwargs['proxy']
        logger.info(
            "Spider '{}' setting proxy to '{}'".format(self, self.proxy))

        self.search_term = search_uri_frag

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

        np = response.xpath('//a[@title="next page"]')
        if np and np.xpath('text()').extract_first() is '»':
            next_page_link = np.xpath('@href').extract_first()
            next_page_link = "{}{}".format(self.base_domain, next_page_link)
            yield self.create_request(next_page_link, response)


    def create_request(self, url, response=None, **kwargs):
        # This function could be replaced by using CookiesMiddleware instead.
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
