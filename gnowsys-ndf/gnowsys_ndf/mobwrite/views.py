# Create your views here.
import urllib
import socket

from django.conf import settings
from django.template import RequestContext, Context

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.http import HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404, render
from django.utils import simplejson
from django.contrib.sites.models import Site

import models
from django.views.decorators.csrf import csrf_exempt #textb


def processRequest(q):
    a = ''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((settings.MOBWRITE_HOST, settings.MOBWRITE_PORT))
    except socket.error, msg:
        s = None
    if s:
        s.send(q)
        while True:
            line = s.recv(1024)
            if not line:
                break
            a += line
        s.close()
    return a

@csrf_exempt    #textb
def mobwrite(request):
    models.mobwrite_core.logging.basicConfig()
    if not settings.DEBUG:
        models.mobwrite_core.LOG.setLevel(models.mobwrite_core.logging.ERROR)
    mobwrite = models.DjangoMobWrite()
    q = urllib.unquote(request.body)
    mode = None
    if q.find("p=") == 0:
        mode = "script"
    elif q.find("q=") == 0:
        mode = "text"
    else:
        return HttpResponseBadRequest("Missing q= or p=")
    q = q[2:]
    a = mobwrite.handleRequest(q)
    if mode == "text":
        a = a + "\n\n"
        content_type = "text/plain"
    else:
        a = a.replace("\\", "\\\\").replace("\"", "\\\"")
        a = a.replace("\n", "\\n").replace("\r", "\\r")
        a = "mobwrite.callback(\"%s\");" % a
        content_type = "application/javascript"
    response = HttpResponse(a, content_type=content_type)
    response['Pragma'] = 'No-cache'
    response['Expires'] = '-1'
    #should this be called that often?
    mobwrite.cleanup()
    models.mobwrite_core.logging.shutdown()
    return response

def new(request):
    url = '/t/%s/' % models.randomName()
    return HttpResponseRedirect(url)

def text(request, name):
    url = request.build_absolute_uri(request.path)
    #name = name.replace('.', '__')
    context = RequestContext(request, {'name': name, 'url': url})
    return render_to_response("editor.html", context)

def raw(request, name):
    t = models.fetchText(name)
    response = HttpResponse(t.text, content_type='text/plain')
    return response

def html(request, name):
    t = models.fetchText(name)
    response = HttpResponse(t.html(), content_type='text/html')
    return response
