# -*- coding: utf-8 -*-
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from pprint import pprint, pformat
import argparse


from scrapy_rarbg_tv_spider import RarbgTvSpider

import logging

logger = logging.getLogger(__name__)


PROXY = None  # change_me
# PROXY = None


def build_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('showname', help='tv show name to search for')
    parser.add_argument(
        '-f', '--format', help='output format [json|csv]', nargs='?', default='json')
    parser.add_argument('--proxy_check_run', help='proxy_check_run',
                        default=False, action='store_true')
    parser.add_argument('output_file', help='output filename')

    return parser


def main():
    configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})

    args = build_argparser().parse_args()
    logger.info("args: {}".format(pformat(args.__dict__)))

    runner = CrawlerRunner({
        'USER_AGENT': '"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"',
        # 'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
        # 'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0',
        'FEED_FORMAT': args.format,
        'FEED_URI': args.output_file,
        'HTTPPROXY_ENABLED': True,
        # 'DOWNLOADER_MIDDLEWARES': {'middlewares_rarbg_spider.ProxyMiddleware': 100},
        "ITEM_PIPELINES": {'middlewares_rarbg_spider.ExportPipeline': 300}
    })

    d = runner.crawl(RarbgTvSpider, showname=args.showname,
                     proxy=PROXY, proxy_check_run=args.proxy_check_run)
    d.addBoth(lambda _: reactor.stop())

    reactor.run()


if __name__ == '__main__':
    main()
