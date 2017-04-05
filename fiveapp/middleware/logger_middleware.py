
from django.utils.deprecation import MiddlewareMixin

from fiveapp.utils import now


class LoggerMiddleWare(MiddlewareMixin):

    def process_request(self, request):
        print "\n\n(%s):\tRequest path : %s" % (now(), request.path)
        print "Request body : %s" % (request.body)
        print "Request HTTP_AUTHORIZATION : %s" % (request.META.get('HTTP_AUTHORIZATION', None))

        return None

    def process_response(self, request, response):
        print "Response: %s" % (response.content)
        return response