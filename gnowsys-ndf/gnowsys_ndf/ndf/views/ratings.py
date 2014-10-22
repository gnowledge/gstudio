from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from gnowsys_ndf.ndf.models import get_database
from gnowsys_ndf.ndf.models import Node
from django.contrib.auth.models import User
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

import json

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

db = get_database()
col_Group = db[Node.collection_name]
sitename=Site.objects.all()[0]

def ratings(request,group_id):
    rating=request.POST.get('rating', '')
    node=col_Group.Node.one({'_id':ObjectId(group_id)})
    ratedict={}
    if rating:
        ratedict['score']=int(rating)
    else:
        ratedict['score']=0
    ratedict['user_id']=request.user.id
    ratedict['ip_address']=request.META['REMOTE_ADDR']
    fl=0
    for each in node.rating:
        if each['user_id'] == request.user.id:
            if rating:
                each['score']=int(rating)
            else:
                each['score']=0
            fl=1
    if not fl:
        node.rating.append(ratedict)
    node.save()
    vars=RequestContext(request,{'node':node})
    template="ndf/rating.html"
    return render_to_response(template, vars)
    
    
