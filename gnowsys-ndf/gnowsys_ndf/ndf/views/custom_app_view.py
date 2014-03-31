''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response #, render  uncomment when to use
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required


from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import *

db = get_database()
collection = db['Nodes']

def custom_app_view(request, group_id, app_name, app_id, app_set_id=None, app_set_instance_id=None):
    """
    custom view for custom GAPPS
    """
    app_collection_set = [] 
    atlist = []
    rtlist = []
    app = collection.Node.find_one({"_id":ObjectId(app_id)})
    app_set = ""
    nodes = ""
    nodes_dict = ""
    app_menu = ""
    app_set_template = ""
    app_set_instance_template = ""
    app_set_instance_name = ""
    app_set_name = ""
    title = ""
    tags = ""
    content = ""
    for eachset in app.collection_set:
	 app_set = collection.Node.find_one({"_id":eachset})
	 app_collection_set.append({"id":str(app_set._id),"name":app_set.name}) 	
    if app_set_id:
        classtype = ""
        app_set_template = "yes"
        systemtype = collection.Node.find_one({"_id":ObjectId(app_set_id)})
        systemtype_name = systemtype.name
        title = systemtype_name
        if request.method=="POST":
            search = request.POST.get("search","")
            classtype = request.POST.get("class","")
            nodes = list(collection.Node.find({'name':{'$regex':search, '$options': 'i'},'member_of': {'$all': [systemtype._id]},'_type':'GSystem'}))
        else :
            nodes = list(collection.Node.find({'member_of': {'$all': [systemtype._id]},'_type':'GSystem','group_set':{'$all': [ObjectId(group_id)]}}))
        nodes_dict = []
        for each in nodes:
            nodes_dict.append({"id":str(each._id), "name":each.name, "created_by":User.objects.get(id=each.created_by).username, "created_at":each.created_at})
    else :
        app_menu = "yes"
        title = app_name
    if app_set_instance_id :
        app_set_instance_template = "yes"
        app_set_template = ""
        systemtype_attributetype_set = []
        systemtype_relationtype_set = []
        system = collection.Node.find_one({"_id":ObjectId(app_set_instance_id)})
        systemtype = collection.Node.find_one({"_id":ObjectId(app_set_id)})
        for each in systemtype.attribute_type_set:
            systemtype_attributetype_set.append({"type":each.name,"type_id":str(each._id),"value":each.data_type})
        for each in systemtype.relation_type_set:
            systemtype_relationtype_set.append({"rt_name":each.name,"type_id":str(each._id)})

        for eachatset in systemtype_attributetype_set :
            for eachattribute in collection.Node.find({"_type":"GAttribute", "subject":system._id, "attribute_type.$id":ObjectId(eachatset["type_id"])}):
                atlist.append({"type":eachatset["type"],"type_id":eachatset["type_id"],"value":eachattribute.object_value})
        for eachrtset in systemtype_relationtype_set :
            for eachrelation in collection.Node.find({"_type":"GRelation", "subject":system._id, "relation_type.$id":ObjectId(eachrtset["type_id"])}):
                right_subject = collection.Node.find_one({"_id":ObjectId(eachrelation.right_subject)})
                rtlist.append({"type":eachrtset["rt_name"],"type_id":eachrtset["type_id"],"value_name": right_subject.name,"value_id":str(right_subject._id)})

        tags = ",".join(system.tags)
        content = system.content
        app_set_name = systemtype.name
        app_set_instance_name = system.name
        title =  systemtype.name +"-" +system.name
    template = "ndf/custom_template_for_app.html"
    variable = RequestContext(request, {'groupid':group_id, 'app_name':app_name, 'app_id':app_id, "app_collection_set":app_collection_set,"app_set_id":app_set_id,"nodes":nodes_dict, "app_menu":app_menu, "app_set_template":app_set_template, "app_set_instance_template":app_set_instance_template, "app_set_name":app_set_name, "app_set_instance_name":app_set_instance_name, "title":title, "app_set_instance_atlist":atlist, "app_set_instance_rtlist":rtlist, 'tags':tags, "content":content})
    return render_to_response(template, variable)
      
@login_required
def custom_app_new_view(request, group_id, app_name, app_id, app_set_id=None):
    """
    create new instance of app_set of apps view for custom GAPPS
    """
    app_collection_set = [] 
    app = collection.Node.find_one({"_id":ObjectId(app_id)})
    app_set = ""
    nodes = ""
    systemtype = ""
    systemtype_name = ""
    systemtype_attributetype_set = []
    systemtype_relationtype_set = []
    title = ""
    file_st_ids = []
    app_type_of_id = ""
    File = 'False'
    print app_set_id,"test-app-id"
    for eachset in app.collection_set:
	 app_set = collection.Node.find_one({"_id":eachset})
	 app_collection_set.append({"id":str(app_set._id),"name":app_set.name}) 	
    if app_set_id:
        systemtype = collection.Node.find_one({"_id":ObjectId(app_set_id)})
        systemtype_name = systemtype.name
        title = systemtype_name + " - new"
        for each in systemtype.attribute_type_set:
            systemtype_attributetype_set.append({"type":each.name,"type_id":str(each._id),"value":each.data_type})
        for eachrt in systemtype.relation_type_set:
            object_type = [ {"name":rtot.name, "id":str(rtot._id)} for rtot in collection.Node.find({'member_of': {'$all': [ collection.Node.find_one({"_id":eachrt.object_type[0]})._id]}}) ]
            systemtype_relationtype_set.append({"rt_name":eachrt.name,"type_id":str(eachrt._id),"object_type":object_type})
    
    request_at_dict = {}
    request_rt_dict = {}

    files_sts = ['File','Image','Video']
    if app_set_id:
        app = collection.Node.one({'_id':ObjectId(app_set_id)})
        for each in files_sts:
            node_id = collection.Node.one({'name':each})._id
            if node_id in app.type_of:
                File = 'True'
        
    print app.type_of,"test",file_st_ids
    if request.method=="POST":
        tags = request.POST.get("tags","")
        content_org = unicode(request.POST.get("content_org",""))
        name = request.POST.get("name","")
        for each in systemtype_attributetype_set:
            request_at_dict[each["type_id"]] = request.POST.get(each["type_id"],"")
        for eachrtset in systemtype_relationtype_set:
            request_rt_dict[eachrtset["type_id"]] = request.POST.get(eachrtset["type_id"],"")

        
        if app.type_of in file_st_ids:
            newgsystem = collection.File() #creating File object ot store files
        else:
            newgsystem = collection.GSystem()

        newgsystem.name = name
        newgsystem.member_of=[ObjectId(app_set_id)]
        newgsystem.created_by = request.user.id
        newgsystem.group_set.append(ObjectId(group_id))
        if tags:
             newgsystem.tags = tags.split(",")
        if content_org:
            usrname = request.user.username
            filename = slugify(newgsystem.name) + "-" + usrname
            newgsystem.content = org2html(content_org, file_prefix=filename)
        newgsystem.save()
        for key,value in request_at_dict.items():
            attributetype_key = collection.Node.find_one({"_id":ObjectId(key)})
            newattribute = collection.GAttribute()
            newattribute.subject = newgsystem._id
            newattribute.attribute_type = attributetype_key
            newattribute.object_value = value
 #           newattribute.name = unicode(newgsystem.name+"- "+attributetype_key.name+"-"+value)
            newattribute.save()
        for key,value in request_rt_dict.items():
            if key:
                relationtype_key = collection.Node.find_one({"_id":ObjectId(key)})
            if value:
                right_subject = collection.Node.find_one({"_id":ObjectId(value)})
                newrelation = collection.GRelation()
                newrelation.subject = newgsystem._id
                newrelation.relation_type = relationtype_key
                newrelation.right_subject = right_subject._id
#            newrelation.name = unicode(newgsystem.name+"- "+relationtype_key.name+"-"+right_subject.name)
                newrelation.save()
        return HttpResponseRedirect(reverse('GAPPS_set', kwargs={'group_id': group_id, 'app_name': app_name, "app_id":app_id, "app_set_id":app_set_id}))
          
    template = "ndf/custom_template_for_app.html"
    variable = RequestContext(request, {'groupid':group_id, 'app_name':app_name, 'app_id':app_id, "app_collection_set":app_collection_set, "app_set_id":app_set_id, "nodes":nodes, "systemtype_attributetype_set":systemtype_attributetype_set, "systemtype_relationtype_set":systemtype_relationtype_set, "create_new":"yes", "app_set_name":systemtype_name, 'title':title, 'File':File})
    return render_to_response(template, variable)
      
 
