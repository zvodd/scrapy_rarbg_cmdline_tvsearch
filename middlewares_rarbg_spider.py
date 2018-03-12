from pprint import pprint
import logging

logger = logging.getLogger(__name__)

ITEMS = []


class ExportPipeline(object):
    def process_item(self, item, spider):
        ITEMS.append(item)
        return item

    def close_spider(self, spider):
        pprint(ITEMS)


class ProxyMiddleware(object):
    def process_request(self, request, spider):
        proxy = getattr(spider, 'proxy', None)
        if proxy is not None:
            logger.info("Using proxy '{}' for request '{}'".format(proxy, request))
            request.meta['proxy'] = proxy
        else:
            logger.info("NOT using proxy for request '{}'".format(request))
