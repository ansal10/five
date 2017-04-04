
from django.utils.deprecation import MiddlewareMixin


class LoggerMiddleWare(MiddlewareMixin):

    def process_request(self, request):
        print "Request body : %s" % (request.body)
        print "Request Meta : %s" % (request.META)

        return None

    def process_response(self, request, response):
        print "Response: %s" % (response.content)
        return response