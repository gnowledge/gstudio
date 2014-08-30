''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.utils import translation
from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django_mongokit import get_database
from gnowsys_ndf.ndf.views.methods import *
from gnowsys_ndf.settings import GAPPS,GSTUDIO_SITE_DEFAULT_LANGUAGE

import os.path

import json

db = get_database()
collection = db[Node.collection_name]
GAPP = collection.Node.one({'$and':[{'_type':'MetaType'},{'name':'GAPP'}]}) # fetching MetaType name GAPP

def lang_pref(request):
    url=request.GET.get('url','')
    appid=request.GET.get('appid','')
    group_id=request.GET.get('group_id','')
    lan_dict={}
    auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
    if auth:
        lan_dict['primary']=request.LANGUAGE_CODE
        lan_dict['default']=u"en"
        auth.preferred_languages=lan_dict
        auth.modified_by=request.user.id
        auth.save()
    if appid:
        appname=collection.Node.one({'_id':ObjectId(str(appid))})
        return HttpResponseRedirect("/home/"+appname.name.lower())
    if not appid:
        return HttpResponseRedirect(url)
