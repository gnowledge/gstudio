''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response #, render  uncomment when to use
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required


from gnowsys_ndf.ndf.models import *

db = get_database()
collection = db['Nodes']

def custom_app_view(request, group_id, app_name, app_id, app_set_id=None):
    """
    custom view for custom GAPPS
    """
    app_collection_set = [] 
    app = collection.Node.find_one({"_id":ObjectId(app_id)})
    app_set = ""
    nodes = ""
    app_menu = ""
    app_set_template = ""
    for eachset in app.collection_set:
	 app_set = collection.Node.find_one({"_id":eachset})
	 app_collection_set.append({"id":str(app_set._id),"name":app_set.name}) 	
    if app_set_id:
        classtype = ""
        app_set_template = "yes"
        systemtype_name = collection.Node.find_one({"_id":ObjectId(app_set_id)}).name
        if request.method=="POST":
            search = request.POST.get("search","")
            classtype = request.POST.get("class","")
            nodes = list(collection.Node.find({'name':{'$regex':search},'_type':systemtype_name}))
        else :
            nodes = list(collection.Node.find({'_type':systemtype_name}))
    else :
        app_menu = "yes"
    template = "ndf/custom_template_for_app.html"
    variable = RequestContext(request, {'groupid':group_id, 'app_name':app_name, 'app_id':app_id, "app_collection_set":app_collection_set,"app_set_id":app_set_id,"nodes":nodes, "app_menu":app_menu, "app_set_template":app_set_template})
    return render_to_response(template, variable)
      

def custom_app_new_view(request, group_id, app_name, app_id, app_set_id=None):
    """
    custom view for custom GAPPS
    """
    app_collection_set = [] 
    app = collection.Node.find_one({"_id":ObjectId(app_id)})
    app_set = ""
    nodes = ""
    systemtype = ""
    systemtype_name = ""
    systemtype_attributetype_set = []
    systemtype_relationtype_set = []
    for eachset in app.collection_set:
	 app_set = collection.Node.find_one({"_id":eachset})
	 app_collection_set.append({"id":str(app_set._id),"name":app_set.name}) 	
    if app_set_id:
        systemtype = collection.Node.find_one({"_id":ObjectId(app_set_id)})
        systemtype_name = systemtype.name
        for each in systemtype.attribute_type_set:
            systemtype_attributetype_set.append({"type":each.name,"type_id":str(each._id),"value":each.data_type})
        for each in systemtype.relation_type_set:
            object_type = [ {"name":rtot.name, "id":ObjectId(rtot._id)} for rtot in collection.Node.find({"_type":collection.Node.find_one({"_id":each.object_type}).name}) ]
            systemtype_relationtype_set.append({"rt_name":each.name,"type_id":str(each._id),"object_type":object_type})
 
          
    template = "ndf/custom_template_for_app.html"
    variable = RequestContext(request, {'groupid':group_id, 'app_name':app_name, 'app_id':app_id, "app_collection_set":app_collection_set, "app_set_id":app_set_id, "nodes":nodes, "systemtype_attributetype_set":systemtype_attributetype_set, "systemtype_relationtype_set":systemtype_relationtype_set, "create_new":"yes", "app_set_name":systemtype_name})
    return render_to_response(template, variable)
      
 
