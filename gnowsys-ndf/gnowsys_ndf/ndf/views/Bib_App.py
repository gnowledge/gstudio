from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import render_to_response #render  uncomment when to use
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django_mongokit import get_database
from django.contrib.auth.models import User
from django.contrib.sites.models import Site


try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

from gnowsys_ndf.settings import GAPPS, MEDIA_ROOT
from gnowsys_ndf.ndf.models import GSystemType, Node 
from gnowsys_ndf.ndf.views.methods import get_node_common_fields
from gnowsys_ndf.ndf.views.notify import set_notif_val
from gnowsys_ndf.ndf.views.methods import *
from gnowsys_ndf.ndf.models import *
collection = get_database()[Node.collection_name]
sitename=Site.objects.all()
if sitename :
    sitename = sitename[0]
else : 
    sitename = ""

db = get_database()
collection = db[Node.collection_name]
collection_tr = db[Triple.collection_name]

history_manager = HistoryManager()
rcs = RCS()
Bibtex_entries=[]
dictionary={'article':["author","title","journal","year","volume","number","pages","month","key","note"]}
Bibtex_entries.append(dictionary)
dictionary={'book':["author","title","publisher","year","volume","series","address","edition","month","note","key"]}
Bibtex_entries.append(dictionary)
dictionary={'booklet':["title","author","howpublished","address","month","year","note","key"]}
Bibtex_entries.append(dictionary)
dictionary={'conference':["author","title","booktitle","year","editor","pages","organisation","publisher","month","note","key"]}
Bibtex_entries.append(dictionary)
dictionary={'inbook':["author","title","chapter","pages","publisher","year","volume","series","address","edition","month","note","key"]}
Bibtex_entries.append(dictionary)
dictionary={'incollection':["author","title","booktitle","year","editor","pages","organisation","publisher","address","month","note","key"]}
Bibtex_entries.append(dictionary)
dictionary={'inproceedings':["author","title","booktitle","year","editor","pages","organisation","publisher","address","month","note","key"]}
Bibtex_entries.append(dictionary)
dictionary={'manual':["title","author","organisation","address","edition","month","year","note","key"]}
Bibtex_entries.append(dictionary)
dictionary={'masterthesis':["author","title","school","year","address","month","note","key"]}
Bibtex_entries.append(dictionary)
dictionary={'misc':["author","title","howpublished","month","year","note","key"]}
Bibtex_entries.append(dictionary)
dictionary={'phdthesis':["author","title","school","year","address","month","note","key"]}
Bibtex_entries.append(dictionary)
dictionary={'proceedings':["title","year","editor","publisher","organisation","address","month","note","key"]}
Bibtex_entries.append(dictionary)
dictionary={'techreport':["author","title","institution","year","type","number","address","month","note","key"]}
Bibtex_entries.append(dictionary)
dictionary={'unpublished':["author","title","note","month","year","key"]}
Bibtex_entries.append(dictionary) 

##Bib_App function

def Bib_App(request, group_id):
    """
    Renders the main page of the app
    """
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False :
      group_ins = collection.Node.find_one({'_type': "Group","_id": group_id})
      auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
      if group_ins:
        group_id = str(group_ins._id)
      else :
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if auth :
          group_id = str(auth._id)
    else :
        pass
    title = "Bibliographic Citations"
    template = "ndf/Bib_App.html"
    variable = RequestContext(request,{'title': title, 'group_id': group_id, 'groupid': group_id})
    return render_to_response(template,variable)


def view_entries(request, group_id,node_id=None):
    '''
    renders the list view of all entries of a specific type when node_id is known
    '''
  
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False :
      group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
      auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
      if group_ins:
        group_id = str(group_ins._id)
      else :
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if auth :
          group_id = str(auth._id)
    else :
        pass
    
    if node_id is None:
        num = int(request.GET.get('num'))
        entry=Bibtex_entries[num]
        ''' for retreiving the name of the entry from the corresponding number
        '''
        for name, value in entry.iteritems():
            title=name
        GST_ENTRY = collection.Node.one({'_type': "GSystemType", 'name':name})
        title=GST_ENTRY.name
    else:
        GST_ENTRY=collection.Node.one({'_id':'node_id'})
        title=GST_ENTRY.name

    entry_inst = collection.GSystem.find({'member_of': {'$all': [GST_ENTRY._id]}, 'group_set': {'$all': [ObjectId(group_id)]},'status':u'PUBLISHED'})
    template = "ndf/view_entries.html"
    variable = RequestContext(request, {'entry_inst': entry_inst, 'group_id': group_id, 'groupid': group_id,'title':title,'num':num})

    return render_to_response(template,variable)


def view_entry(request,group_id,node_id):
    ''' renders list view of entries of a specific bibtex type when the type is known
    '''
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False :
      group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
      auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
      if group_ins:
        group_id = str(group_ins._id)
      else :
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if auth :
          group_id = str(auth._id)
    else :
        pass
    GST_BIBTEX=collection.Node.one({'_id':ObjectId(node_id)})
    title=GST_BIBTEX.name
    entry_inst=collection.GSystem.find({'member_of':{'$all':[GST_BIBTEX._id]},'group_set':{'$all':[ObjectId(group_id)]},'status':u'PUBLISHED'})
    template="ndf/view_entries.html"
    variable = RequestContext(request, {'entry_inst': entry_inst, 'group_id': group_id, 'groupid': group_id,'title':title})
    return render_to_response(template,variable)

def view_sentry(request,group_id,node_id):
    ''' for displaying a specific entry
    '''
    ins_objectid=ObjectId()
    if ins_objectid.is_valid(group_id) is False:
        group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else :
        pass
    GST_SENTRY=collection.Node.one({'_id':ObjectId(node_id)})
    GST_one=collection.Node.one({'_type':'AttributeType','name':'BibTex_entry'})
    gst_bibtex=GST_SENTRY.member_of
    ''' converts [ObjectId('node_id')] to node_id
    '''
    s=str(gst_bibtex)
    list(s)
    gst_bibtex=(s[11:-3])
    gst_bibtex=unicode(gst_bibtex, "UTF-8")
    gst_bibtex=collection.Node.one({'_id':ObjectId(gst_bibtex)})
    gst_id=GST_SENTRY._id
    GST_SAttribute=collection.Node.one({'subject':GST_SENTRY._id,'attribute_type':GST_one._id})
    Bibtex=GST_SAttribute.object_value
    gst_note=GST_SENTRY.content_org
    variable=RequestContext(request,{'name':GST_SENTRY.name,'gst_note':gst_note,'Bibtex':Bibtex,'group_id':group_id,'groupid':group_id,'title':gst_bibtex.name})
    template="ndf/view_sentry.html"
    print "before return"
    return render_to_response(template,variable)


def create_entries(request, group_id):
    ''' for creating a new bibtex entry_list
    '''

    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False :
        group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else :
        pass
        ''' for retreiving the fields of a particular bibtex entry 
        '''
    num = int(request.GET.get('num'))
    entry=Bibtex_entries[num]
    for name, value in entry.iteritems():
        title=name
        list_item=value
    GST_BIBTEX = collection.Node.one({'_type': 'GSystemType', 'name': title})
    GST_ENTRY=collection.Node.one({'_type':'AttributeType','name':'BibTex_entry'})
    GST_LIST=collection.Node.one({'_type':'AttributeType','name':'entry_list'})
    GST_CITATION=collection.Node.one({'_type':'AttributeType','name':'Citation'})
    context_variables = { 'title': title,
                          'group_id': group_id,
                          'groupid': group_id,
                          'list_item':list_item,
                          'num':num
                      }
    entry_node = collection.GSystem()  
    cite=""
    i=0
    value=""
    if request.method == "POST":
        name=request.POST.get("name")
        entry_node.name=name
        citation_key=request.POST.get("citation_key")
        var="@"+title+"{"+citation_key
        value += "name$"+name+"%citation_key$"+citation_key+"%"
        for each in list_item:
            c = request.POST.get(each,"")
            var += " , "+each+" = "+" { "+c+" }"
            value += each + "$" + c + "%"
            i = i+1
            if (each == 'author' and c!= ""):
                cite += c +"."
            if(each == 'title' and c!= ""):
                cite += c+'.'
            if(each == 'year' and c != ""):
                cite += "("+c+") "
            if(each=='publisher' and c!=""):
                cite += "publisher:"+ c + ","
            if(each == 'volume' and c!=""):
                cite += "volume:"+c +","
            if(each == 'edition' and c!=""):
                cite += "edition:"+c+","
            if(each == 'pages' and c!=""):
                cite += "page "+c+","

        var +="}"
        get_node_common_fields(request,entry_node,group_id,GST_BIBTEX)

        entry_node.status=u'PUBLISHED'
        
        entry_node.save()
        '''
        creating a GAttribute of AttributeType BibTex_entry for the already created GSystem
        '''
        GST_current=collection.Node.one({'name':name,'member_of':title})
        Bibtex_entry=collection.GAttribute()
        Bibtex_entry.name=unicode(name)
        Bibtex_entry.subject=ObjectId(entry_node._id)
        Bibtex_entry.attribute_type=GST_ENTRY
        Bibtex_entry.object_value=unicode(var)
        Bibtex_entry.save()
        '''
        creating a GAttribute of AttributeType Citation for the already created GSystem
        '''
        cite_key=collection.GAttribute()
        cite_key.name=unicode(name)
        cite_key.subject=ObjectId(entry_node._id)
        cite_key.attribute_type=GST_CITATION
        cite_key.object_value=unicode(cite)
        cite_key.save()
        '''
        creating a GAttribute of AttributeType entry_list for the already created GSystem
        '''
        entry_list=collection.GAttribute()
        entry_list.name=unicode(name)
        entry_list.subject=ObjectId(entry_node._id)
        entry_list.attribute_type=GST_LIST
        entry_list.object_value=unicode(value)
        entry_list.save()
        return HttpResponseRedirect(reverse('view_entry', kwargs={'group_id': group_id, 'node_id': GST_BIBTEX._id}))
    else:     
        return render_to_response("ndf/create_edit_entries.html",
                                  context_variables,
                                  context_instance=RequestContext(request))




def delete_sentry(request, group_id, node_id):
    """Change the status to Hidden.
    """
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False :
        group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else :
        pass
    gst_entry=collection.Node.one({'_id':ObjectId(node_id)})
    gst_bibtex=gst_entry.member_of
    ''' converts [ObjectId('node_id')] to node_id
    '''
    s=str(gst_bibtex)
    list(s)
    gst_bibtex=(s[11:-3])
    gst_bibtex=unicode(gst_bibtex, "UTF-8")
    op = collection.update({'_id': ObjectId(node_id)}, {'$set': {'status': u"HIDDEN"}})
    
    return HttpResponseRedirect(reverse('view_entry', kwargs={'group_id': group_id,'node_id':gst_bibtex}))
                          


def edit_entry(request,group_id,node_id):
    '''for editing entries
    '''
    ins_objectid  = ObjectId()
    if ins_objectid.is_valid(group_id) is False :
        group_ins = collection.Node.find_one({'_type': "Group","name": group_id})
        auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
        if group_ins:
            group_id = str(group_ins._id)
        else :
            auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
            if auth :
                group_id = str(auth._id)
    else :
        pass

    GST_ENTRY=collection.Node.one({'name':'entry_list','_type':'AttributeType'})
    entry_list=collection.Node.one({'subject':ObjectId(node_id),'attribute_type':GST_ENTRY._id})
    GST_current=collection.Node.one({'_id':ObjectId(node_id)})
    gst_bibtex=GST_current.member_of
    ''' converts [ObjectId('node_id')] to node_id
    '''
    s=str(gst_bibtex)
    list(s)
    gst_bibtex=(s[11:-3])
    gst_bibtex=unicode(gst_bibtex, "UTF-8")
    gst_entry=collection.Node.one({'_id':ObjectId(gst_bibtex)})
    title=gst_entry.name
    entry=entry_list.object_value
    ''' for creating the list of items that has to be displayed from the GAttribute of AttributeType Citation
    '''
    tags=[]
    values=[]
    args=entry.split("%")
    for each in args:
        tags.append(each.split('$')[0])
        try:
            values.append(each.split('$')[1])
        except:
            u="not found"
    content_org=GST_current.content_org    
    value=""
    Name=str(gst_entry.name)
    i=0
    key=""
    value=""
    list_item=tags 
    cite=""
    if request.method == "POST":
        name=request.POST.get("name")
        citation_key=request.POST.get("citation_key")
        var="@"+title+"{"+citation_key
        value += "name$"+name+"%citation_key$"+citation_key+"%"
        i=2
        for each in list_item[2:]:
            c = request.POST.get(each,"")
            var += " , "+each+" = "+" { "+c+" }"
            value += each + "$" + c + "%"
            i = i+1
            if (each == 'author' and c!=""):
                cite += c +"."
            if(each == 'title' and c!= ""):
                cite += c+'.'
            if(each == 'year' and c != ""):
                cite += "("+c+") "
            if(each=='publisher' and c!=""):
                cite += "publisher:"+ c + ","
            if(each == 'volume' and c!=""):
                cite += "volume:"+c +","
            if(each == 'edition' and c!=""):
                cite += "edition:"+c+","
            if(each == 'pages' and c!=""):
                cite += "page "+c+","

        var +="}"
        
        GST_current.save()
        Bibtex=collection.Node.one({'name':'BibTex_entry','_type':'AttributeType'})
        Bibtex_entry=collection.Node.one({'subject':GST_current._id,'attribute_type':Bibtex._id})
        Bibtex_entry.object_value=unicode(var)
        Bibtex_entry.save()
        Citation=collection.Node.one({'name':'Citation','_type':'AttributeType'})
        cite_key=collection.Node.one({'subject':GST_current._id,'attribute_type':Citation._id})
        cite_key.object_value=unicode(cite)
        cite_key.save()
        entry=collection.Node.one({'name':'entry_list','_type':'AttributeType'})
        entry_list=collection.Node.one({'subject':GST_current._id,'attribute_type':entry._id})
        entry_list.object_value=unicode(value)
        entry_list.save()
        return HttpResponseRedirect(reverse('view_entry', kwargs={'group_id': group_id, 'node_id': gst_entry._id}))

    ''' sending both the dictionaries as zip to iterate them simultaneously
    '''
    zipped=zip(tags,values)
    variable=RequestContext(request,{'group_id':group_id,'groupid':group_id,'title':GST_current.name ,'tags':tags,'values':values,'zipped':zipped,'content_org':content_org})
    template="ndf/edit_entry.html"
    return render_to_response(template,variable)
    
