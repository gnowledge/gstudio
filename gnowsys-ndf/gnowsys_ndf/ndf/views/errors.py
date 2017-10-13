from django.shortcuts import render_to_response
from django.template import RequestContext
# To pass custom Error/Info/Warning messages on Error templates, pass in the context variables

def handler404(request):
    # print "\nrequest: ", request
    response = render_to_response('404.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response


def handler500(request):
    response = render_to_response('500.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 500
    return response

def handlerPermissionDenied(request):
    response = render_to_response('403.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 403
    return response
