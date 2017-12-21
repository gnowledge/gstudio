''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
# from django.utils import translation
# from django.http import HttpResponse
# from django.http import StreamingHttpResponse
# from django.shortcuts import render_to_response, render
# from django.template import RequestContext
# from django.contrib.auth.models import User
# from django.contrib.auth.decorators import user_passes_test

# from gnowsys_ndf.settings import GAPPS, GSTUDIO_SITE_DEFAULT_LANGUAGE
from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.ndf.views.methods import get_execution_time

# import os.path
# import json

GAPP = node_collection.one({'$and':[{'_type':'MetaType'},{'name':'GAPP'}]}) # fetching MetaType name GAPP

@get_execution_time
def lang_pref(request):
    url=request.GET.get('url','')
    appid=request.GET.get('appid','')
    group_id=request.GET.get('group_id','')
    lan_dict={}
    auth = node_collection.one({'_type': 'Author', 'name': unicode(request.user.username) })
    if auth:
        lan_dict['primary']=request.LANGUAGE_CODE
        lan_dict['default']=u"en"
        auth.preferred_languages=lan_dict
        if not auth.agency_type: 
            auth.agency_type = "Other"  # Sets default value for agency_type as "Other"
        auth.modified_by=request.user.id
        auth.save(groupid=group_id)
    if appid:
        appname = node_collection.one({'_id': ObjectId(str(appid))})
        return HttpResponseRedirect("/home/"+appname.name.lower())
    if not appid:
        return HttpResponseRedirect(url)
