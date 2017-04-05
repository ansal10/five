import logging
import os

from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('fiveapp')


class LoggerMiddleWare(MiddlewareMixin):

    def process_request(self, request):
        logger.info("\n\nURL : {}\nBODY : {}\nHTTP AUTHORIZATION : {}".format(request.path, request.body, request.META.get('HTTP_AUTHORIZATION', None)))
        return None

    def process_response(self, request, response):
        logger.info("\nResponse : {}".format(response.content))
        return response