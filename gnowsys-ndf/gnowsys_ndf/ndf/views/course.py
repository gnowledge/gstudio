''' -- imports from python libraries -- '''
# from datetime import datetime
import datetime

''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect #, HttpResponse uncomment when to use
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render_to_response #, render  uncomment when to use
from django.template import RequestContext
from django.template import TemplateDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site

from django_mongokit import get_database

try:
  from bson import ObjectId
except ImportError:  # old pymongo
  from pymongo.objectid import ObjectId

''' -- imports from application folders/files -- '''
from gnowsys_ndf.settings import GAPPS, MEDIA_ROOT
# from gnowsys_ndf.ndf.models import GSystemType, Node 
# from gnowsys_ndf.ndf.views.methods import get_node_common_fields
from gnowsys_ndf.ndf.models import Node, AttributeType, RelationType
from gnowsys_ndf.ndf.views.file import save_file
from gnowsys_ndf.ndf.views.methods import get_node_common_fields, parse_template_data
from gnowsys_ndf.ndf.views.notify import set_notif_val
from gnowsys_ndf.ndf.views.methods import get_property_order_with_value
from gnowsys_ndf.ndf.views.methods import create_gattribute, create_grelation



collection = get_database()[Node.collection_name]
GST_COURSE = collection.Node.one({'_type': "GSystemType", 'name': GAPPS[7]})
app = collection.Node.one({'_type': "GSystemType", 'name': GAPPS[7]})

def course(request, group_id, course_id=None):
    """
    * Renders a list of all 'courses' available within the database.
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
    
    if course_id is None:
      course_ins = collection.Node.find_one({'_type':"GSystemType", "name":"Course"})
      if course_ins:
        course_id = str(course_ins._id)

    if request.method == "POST":
      # Course search view
      title = GST_COURSE.name
      
      search_field = request.POST['search_field']
      course_coll = collection.Node.find({'member_of': {'$all': [ObjectId(GST_COURSE._id)]},
                                         '$or': [
                                            {'$and': [
                                              {'name': {'$regex': search_field, '$options': 'i'}}, 
                                              {'$or': [
                                                {'access_policy': u"PUBLIC"},
                                                {'$and': [{'access_policy': u"PRIVATE"}, {'created_by': request.user.id}]}
                                                ]
                                              }
                                              ]
                                            },
                                            {'$and': [
                                              {'tags': {'$regex':search_field, '$options': 'i'}},
                                              {'$or': [
                                                {'access_policy': u"PUBLIC"},
                                                {'$and': [{'access_policy': u"PRIVATE"}, {'created_by': request.user.id}]}
                                                ]
                                              }
                                              ]
                                            }
                                          ],
                                         'group_set': {'$all': [ObjectId(group_id)]}
                                     }).sort('last_update', -1)

      # course_nodes_count = course_coll.count()

      return render_to_response("ndf/course.html",
                                {'title': title,
                                 'appId':app._id,
                                 'searching': True, 'query': search_field,
                                 'course_coll': course_coll, 'groupid':group_id, 'group_id':group_id
                                }, 
                                context_instance=RequestContext(request)
                                )

    elif GST_COURSE._id == ObjectId(course_id):
      # Course list view
      title = GST_COURSE.name
      course_coll = collection.GSystem.find({'member_of': {'$all': [ObjectId(course_id)]}, 
                                             'group_set': {'$all': [ObjectId(group_id)]},
                                             '$or': [
                                              {'access_policy': u"PUBLIC"},
                                              {'$and': [
                                                {'access_policy': u"PRIVATE"}, 
                                                {'created_by': request.user.id}
                                                ]
                                              }
                                             ]
                                            })
      template = "ndf/course.html"
      variable = RequestContext(request, {'title': title, 'course_nodes_count': course_coll.count(), 'course_coll': course_coll, 'groupid':group_id, 'appId':app._id, 'group_id':group_id})
      return render_to_response(template, variable)

@login_required
def create_edit(request, group_id, node_id = None):
    """Creates/Modifies details about the given quiz-item.
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
    context_variables = { 'title': GST_COURSE.name,
                          'group_id': group_id,
                          'groupid':group_id
                      }

    if node_id:
        course_node = collection.Node.one({'_type': u'GSystem', '_id': ObjectId(node_id)})
    else:
        course_node = collection.GSystem()

    if request.method == "POST":
        # get_node_common_fields(request, course_node, group_id, GST_COURSE)
        course_node.save(is_changed=get_node_common_fields(request, course_node, group_id, GST_COURSE))
        return HttpResponseRedirect(reverse('course', kwargs={'appId':app._id,'group_id': group_id}))
        
    else:
        if node_id:
            context_variables['node'] = course_node
            context_variables['groupid']=group_id
            context_variables['group_id']=group_id
            context_variables['appId']=app._id
        return render_to_response("ndf/course_create_edit.html",
                                  context_variables,
                                  context_instance=RequestContext(request)
                              )

def course_detail(request, group_id, _id):
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
    course_node = collection.Node.one({"_id": ObjectId(_id)})
    if course_node._type == "GSystemType":
      return course(request, group_id, _id)
    return render_to_response("ndf/course_detail.html",
                                  { 'node': course_node,
                                    'groupid': group_id,
                                    'group_id':group_id,
                                    'appId':app._id
                                  },
                                  context_instance = RequestContext(request)
        )

# ===================================================================================

      
@login_required
def course_create_edit(request, group_id, app_id, app_set_id=None, app_set_instance_id=None, app_name=None):
  """
  Creates/Modifies document of given sub-types of Course(s).
  """

  auth = None
  if ObjectId.is_valid(group_id) is False :
    group_ins = collection.Node.one({'_type': "Group","name": group_id})
    auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
    if group_ins:
      group_id = str(group_ins._id)
    else :
      auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
      if auth :
        group_id = str(auth._id)
  else :
    pass

  app = None
  if app_id is None:
    app = collection.Node.one({'_type': "GSystemType", 'name': app_name})
    if app:
      app_id = str(app._id)
  else:
    app = collection.Node.one({'_id': ObjectId(app_id)})

  app_name = app.name 

  app_set = ""
  app_collection_set = []
  title = ""

  course_gst = None
  course_gs = None

  property_order_list = []

  template = ""
  template_prefix = "mis"

  if request.user:
    if auth is None:
      auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username)})
    agency_type = auth.agency_type
    agency_type_node = collection.Node.one({'_type': "GSystemType", 'name': agency_type}, {'collection_set': 1})
    if agency_type_node:
      for eachset in agency_type_node.collection_set:
        app_collection_set.append(collection.Node.one({"_id": eachset}, {'_id': 1, 'name': 1, 'type_of': 1}))      

  if app_set_id:
    course_gst = collection.Node.one({'_type': "GSystemType", '_id': ObjectId(app_set_id)}, {'name': 1, 'type_of': 1})
    template = "ndf/" + course_gst.name.strip().lower().replace(' ', '_') + "_create_edit.html"
    title = course_gst.name
    course_gs = collection.GSystem()
    course_gs.member_of.append(course_gst._id)

  if app_set_instance_id:
    course_gs = collection.Node.one({'_type': "GSystem", '_id': ObjectId(app_set_instance_id)})

  property_order_list = get_property_order_with_value(course_gs)

  if request.method == "POST":
    # [A] Save course-node's base-field(s)

    start_time = ""
    if request.POST.has_key("start_time"):
      #convert string into datetime object
      start_time = request.POST.get("start_time", "")
      start_time = datetime.datetime.strptime(start_time,"%m/%Y")
      #get month name (%b for abbreviation and %B for full name) and year and convert to str
      start_time = start_time.strftime("%b %Y")

    end_time = ""
    if request.POST.has_key("end_time"):
      end_time = request.POST.get("end_time", "")
      end_time = datetime.datetime.strptime(end_time,"%m/%Y")
      end_time = end_time.strftime("%b %Y")


    start_enroll = ""
    if request.POST.has_key("start_enroll"):
      start_enroll = request.POST.get("start_enroll", "")
      start_enroll = datetime.datetime.strptime(start_enroll,"%m/%d/%Y")
      start_enroll = start_enroll.strftime("%D")

    end_enroll = ""
    if request.POST.has_key("end_enroll"):
      end_enroll = request.POST.get("end_enroll", "")
      end_enroll = datetime.datetime.strptime(end_enroll,"%m/%d/%Y")
      end_enroll = end_enroll.strftime("%D")
      
    nussd_course_type = ""
    if request.POST.has_key("nussd_course_type"):
      nussd_course_type = request.POST.get("nussd_course_type", "")
      nussd_course_type = unicode(nussd_course_type)

    unset_ac_options = []
    if request.POST.has_key("unset-ac-options"):
      unset_ac_options = request.POST.getlist("unset-ac-options")

    else:
      unset_ac_options = ["dummy"] # Just to execute loop at least once for Course Sub-Types other than 'Announced Course'
    
    announce_to_colg_list = request.POST.get("announce_to_colg_list", "")
    colg_names = []
    colg_names = announce_to_colg_list.split(',')
    announce_to_colg_list = request.POST.get("announce_to_colg_list", "")
    colg_names = []
    colg_names = announce_to_colg_list.split(',')
    colg_gst = collection.Node.one({'_type': "GSystemType", 'name': 'College'})
    colg_list_cur = collection.Node.find({'name': {'$in': colg_names},'member_of':colg_gst._id},{'_id':1, 'name':1})

    #list of colleges selected
    colg_grp_list_cur = collection.Node.find({'_type':u"Group",'name': {'$in': colg_names}},{'_id':1, 'name':1})
    
    colg_PO = {}
    PO = {
      "Agra College": {"Mr. Rajaram Yadav": "yadav.rajaram2009@gmail.com"},
      "Arts College Shamlaji": {"Mr. Ashish Varia": "ashishvaria13@gmail.com"},
      "Baba Bhairabananda Mahavidyalaya": {"Mr. Mithilesh Kumar" : "mithu.ranchi@gmail.com"},
      "Balugaon College": {"Mr. Pradeep Pradhan" : "pradeep.bulu7@gmail.com"},
      "City Women's College": {"Ms. Itishri Panda", "itipanda85@gmail.com"},
      "Comrade Godavari Shamrao Parulekar College of Arts, Commerce & Science": {"Mr. Rahul Sable" : "rahulsab1991@gmail.com"},
      "Faculty of Arts": {"Mr. Jokhim" : "jokhim.lepcha@gmail.com", "Ms. Tusharika Kumbhar" : "tusharika_sai@yahoo.co.in"},
      "Gaya College":  {"Ms. Rishvana Sheik" : "sheik.rishvana@gmail.com"},
      "Govt. M. H. College of Home Science & Science for Women, Autonomous": {"Ms. Rajni Sharma" : "rajni009sharma@gmail.com"}, 
      "Govt. Mahakoshal Arts and Commerce College": {"Ms. Davis Yadav" : "davis.yadav23@gmail.com"},
      "Govt. Mahaprabhu Vallabhacharya Post Graduate College": {"Mr. Gaurav Sharma" : "sonu.12488@gmail.com"},
      "Govt. Rani Durgavati Post Graduate College": {"Mr. Asad Ullah" : "asad13ullah@gmail.com"},
      "Jamshedpur Women's College": {"Mr. Arun Agrawal" : "tissarun@gmail.com"},
      "Kalyan Post Graduate College": {"Mr. Praveen Kumar" : "nayak1307@gmail.com"},
      "Kamla Nehru College for Women": {"Ms. Tusharika Kumbhar" : "tusharika_sai@yahoo.co.in" , "Ms. Thaku Pujari" : "creativethaku@gmail.com"},
      "L. B. S. M. College": {"Mr. Charles Kindo" : "kindocmf@gmail.com"},
      "Mahila College": {"Mr. Sonu Kumar" : "sonu90kumar@gmail.com"},
      "Marwari College": {"Mr. Avinash Anand" : "avinashanand7@gmail.com"},
      "Matsyodari Shikshan Sanstha's Arts, Commerce & Science College": {"Ms. Jyoti Kapale" : "advocatejyotikapale@gmail.com"},
      "Ranchi Women's College": {"Mr. Avinash Anand" : "avinashanand7@gmail.com"},
      "Shiv Chhatrapati College": {"Mr. Swapnil Sardar" : "swapnil85sardar@gmail.com"},
      "Shri & Smt. PK Kotawala Arts College": {"Mr. Sawan Kumar" : "guptsawan1989@gmail.com"},
      "Shri VR Patel College of Commerce": {"Mr. Sushil Mishra" : "sushilmishra.prayag@gmail.com"},
      "Sree Narayana Guru College of Commerce": {"Ms. Bharti Bhalerao" : "bhaleraobharti3@gmail.com"},
      "Sri Mahanth Shatanand Giri College": {"Mr. Narendra Singh" : "narendrasingh.dheeraj@gmail.com"},
      "St. John's College": {"Mr. Himanshu Guru" : "guruhimanshu1987@gmail.com"},
      "The Graduate School College For Women": {"Mr. Pradeep Gupta" : "pkg.gupta141@gmail.com"},
      "Vasant Rao Naik Mahavidyalaya": {"Mr. Dayanand Waghmare": "tiss.dayawagh@gmail.com"},
      "Vivekanand Arts, Sardar Dalip Singh Commerce & Science College": {"Mr. Anis Ambade" : "anisambade@gmail.com"}
    }

    userObj = {}
    for each in colg_grp_list_cur:
      for key,val in PO.items():
        if (key == each.name):
          if val:
            try:
              for key1,val1 in val.items():
                userObj[(User.objects.get(email = val1))]=key1
            except:
              print "No PO exists"  
          else:
            print "No PO exists for ",each.name

    for colg_ids in colg_list_cur: 
      #for each selected college
      for each in unset_ac_options:
        #for each selected course to Announce
        if course_gst.name == u"Announced Course":
          # Code to be executed only for 'Announced Course' GSystem(s)
          sid, nm = each.split(">>")
          print "\n\nsid",sid
          course_gs = collection.Node.one({'_type': "GSystem", '_id': ObjectId(sid), 'member_of': course_gst._id})
          if not course_gs:
            course_gs = collection.GSystem()
          else:
            if " -- " in nm:
              nm = nm.split(" -- ")[0].lstrip().rstrip()
          c_name = unicode(nm + " -- " + nussd_course_type + " -- " + colg_ids.name+" -- " + start_time + " -- " + end_time)
          request.POST["name"] = c_name
        is_changed = get_node_common_fields(request, course_gs, group_id, course_gst)
        if is_changed:
          # Remove this when publish button is setup on interface
          course_gs.status = u"PUBLISHED"
        course_gs.save(is_changed=is_changed)

        #Send e-mail notification to POs of respective Colleges
        if course_gst.name == u"Announced Course":
          sitename=Site.objects.all()[0]
          if userObj:
            for key,val in userObj.items():
              activ="Course Announced"
              msg="\n\nGreetings "+val+","+"\nCourse Announced : " +nm+"("+nussd_course_type+")" +" for period "+start_time+" to "+end_time+"."+"\nStudent Enrollment can be done from "+\
                start_enroll+ " to "+ end_enroll+"."+"\n\nBest Regards,\n"+sitename.name.__str__()+" Management."
              set_notif_val(request,group_id,msg,activ,key)
          else:
            print "No email/PO"

      # [B] Store AT and/or RT field(s) of given course-node (i.e., course_gs)
        for tab_details in property_order_list:
          for field_set in tab_details[1]:
            # Fetch only Attribute field(s) / Relation field(s)
            if field_set.has_key('_id'):
              field_instance = collection.Node.one({'_id': field_set['_id']})
              field_instance_type = type(field_instance)
              if field_instance_type in [AttributeType, RelationType]:
                
                field_data_type = field_set['data_type']

                # Fetch field's value depending upon AT/RT and Parse fetched-value depending upon that field's data-type
                if field_instance_type == AttributeType:

                  if "File" in field_instance["validators"]:
                    # Special case: AttributeTypes that require file instance as it's value in which case file document's ObjectId is used
                    
                    if field_instance["name"] in request.FILES:
                      field_value = request.FILES[field_instance["name"]]

                    else:
                      field_value = ""
                    
                    # Below 0th index is used because that function returns tuple(ObjectId, bool-value)
                    if field_value != '' and field_value != u'':
                      file_name = course_gs.name + " -- " + field_instance["altnames"]
                      content_org = ""
                      tags = ""
                      field_value = save_file(field_value, file_name, request.user.id, group_id, content_org, tags, oid=True)[0]

                  else:
                    # Other AttributeTypes 
                    field_value = request.POST.get(field_instance["name"], "")

                  if field_instance["name"] in ["start_time","end_time"]: #Course Duration 
                    field_value = parse_template_data(field_data_type, field_value, date_format_string="%m/%Y")
                  elif field_instance["name"] in ["start_enroll", "end_enroll"]: #Student Enrollment DUration
                    field_value = parse_template_data(field_data_type, field_value, date_format_string="%m/%d/%Y")
                  elif field_instance["name"] in ["mast_tr_qualifications", "voln_tr_qualifications"]:
                    # Needs sepcial kind of parsing
                    field_value = []
                    tr_qualifications = request.POST.get(field_instance["name"], '')
                    
                    if tr_qualifications:
                      qualifications_dict = {}
                      tr_qualifications = [each.strip() for each in tr_qualifications.split(",")]
                      
                      for i, each in enumerate(tr_qualifications):
                        if (i % 2) == 0:
                          if each == "true":
                            qualifications_dict["mandatory"] = True
                          elif each == "false":
                            qualifications_dict["mandatory"] = False
                        else:
                          qualifications_dict["text"] = unicode(each)
                          field_value.append(qualifications_dict)
                          qualifications_dict = {}
                  elif field_instance["name"] in ["max_marks", "min_marks"]:
                    # Needed because both these fields' values are dependent upon evaluation_type field's value
                    evaluation_type = request.POST.get("evaluation_type", "")
                    if evaluation_type == u"Continuous":
                      field_value = None
                    field_value = parse_template_data(field_data_type, field_value, date_format_string="%m/%d/%Y %H:%M")
                  else:
                    field_value = parse_template_data(field_data_type, field_value, date_format_string="%m/%d/%Y %H:%M")
                  course_gs_triple_instance = create_gattribute(course_gs._id, collection.AttributeType(field_instance), field_value)
                else:
                  #i.e if field_instance_type == RelationType
                  if field_instance["name"] == "announced_for":
                    field_value = ObjectId(sid)
                    #Pass ObjectId of selected Course

                  elif field_instance["name"] == "acourse_for_college":
                    field_value = colg_ids._id
                    #Pass ObjectId of selected College
                  
                  course_gs_triple_instance = create_grelation(course_gs._id, collection.RelationType(field_instance), field_value)

    return HttpResponseRedirect(reverse(app_name.lower()+":"+template_prefix+'_app_detail', kwargs={'group_id': group_id, "app_id":app_id, "app_set_id":app_set_id}))
  
  univ = collection.Node.one({'_type': "GSystemType", 'name': "University"}, {'_id': 1})
  university_cur = collection.Node.find({'member_of': univ._id}, {'name': 1}).sort('name', 1)

  default_template = "ndf/course_create_edit.html"
  context_variables = { 'groupid': group_id, 'group_id': group_id,
                        'app_id': app_id, 'app_name': app_name, 'app_collection_set': app_collection_set, 
                        'app_set_id': app_set_id,
                        'title':title,
                        'university_cur':university_cur,
                        'property_order_list': property_order_list,
                      }

  if app_set_instance_id:
    course_gs.get_neighbourhood(course_gs.member_of)
    context_variables['node'] = course_gs

  try:
    return render_to_response([template, default_template], 
                              context_variables,
                              context_instance = RequestContext(request)
                            )
  
  except TemplateDoesNotExist as tde:
    error_message = "\n CourseCreateEditViewError: This html template (" + str(tde) + ") does not exists !!!\n"
    raise Http404(error_message)
  
  except Exception as e:
    error_message = "\n CourseCreateEditViewError: " + str(e) + " !!!\n"
    raise Exception(error_message)


def course_detail(request, group_id, app_id=None, app_set_id=None, app_set_instance_id=None, app_name=None):
  """
  custom view for custom GAPPS
  """
  # print "\n Found course_detail n gone inn this...\n\n"

  auth = None
  if ObjectId.is_valid(group_id) is False :
    group_ins = collection.Node.one({'_type': "Group","name": group_id})
    auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
    if group_ins:
      group_id = str(group_ins._id)
    else :
      auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username) })
      if auth :
        group_id = str(auth._id)
  else :
    pass

  app = None
  if app_id is None:
    app = collection.Node.one({'_type': "GSystemType", 'name': app_name})
    if app:
      app_id = str(app._id)
  else:
    app = collection.Node.one({'_id': ObjectId(app_id)})

  app_name = app.name 

  # print "\n coming in course detail... \n"
  # app_name = "mis"
  app_set = ""
  app_collection_set = []
  title = ""

  course_gst = None
  course_gs = None

  nodes = None
  node = None
  property_order_list = []
  is_link_needed = True         # This is required to show Link button on interface that link's Student's/VoluntaryTeacher's node with it's corresponding Author node

  template_prefix = "mis"
  context_variables = {}

  if request.user:
    if auth is None:
      auth = collection.Node.one({'_type': 'Author', 'name': unicode(request.user.username)})
    agency_type = auth.agency_type
    agency_type_node = collection.Node.one({'_type': "GSystemType", 'name': agency_type}, {'collection_set': 1})
    if agency_type_node:
      for eachset in agency_type_node.collection_set:
        app_collection_set.append(collection.Node.one({"_id": eachset}, {'_id': 1, 'name': 1, 'type_of': 1}))      


  if app_set_id:
    course_gst = collection.Node.one({'_type': "GSystemType", '_id': ObjectId(app_set_id)}, {'name': 1, 'type_of': 1})
    title = course_gst.name
  
    template = "ndf/course_list.html"

    if request.method=="POST":
      search = request.POST.get("search","")
      classtype = request.POST.get("class","")
      # nodes = list(collection.Node.find({'name':{'$regex':search, '$options': 'i'},'member_of': {'$all': [course_gst._id]}}))
      nodes = collection.Node.find({'member_of': course_gst._id, 'name': {'$regex': search, '$options': 'i'}})
    else:
      nodes = collection.Node.find({'member_of': course_gst._id, 'group_set': ObjectId(group_id)})

  if app_set_instance_id :
    template = "ndf/course_details.html"

    node = collection.Node.one({'_type': "GSystem", '_id': ObjectId(app_set_instance_id)})
    property_order_list = get_property_order_with_value(node)
    node.get_neighbourhood(node.member_of)
  context_variables = { 'groupid': group_id, 
                        'app_id': app_id, 'app_name': app_name, 'app_collection_set': app_collection_set, 
                        'app_set_id': app_set_id,
                        'title':title,
                        'nodes': nodes, 'node': node,
                        'property_order_list': property_order_list,
                        'is_link_needed': is_link_needed
                      }

  try:
    # print "\n template-list: ", [template, default_template]
    # template = "ndf/fgh.html"
    # default_template = "ndf/dsfjhk.html"
    # return render_to_response([template, default_template], 
    return render_to_response(template, 
                              context_variables,
                              context_instance = RequestContext(request)
                            )
  
  except TemplateDoesNotExist as tde:
    # print "\n ", tde
    error_message = "\n CourseDetailListViewError: This html template (" + str(tde) + ") does not exists !!!\n"
    raise Http404(error_message)
  
  except Exception as e:
    error_message = "\n CourseDetailListViewError: " + str(e) + " !!!\n"
    raise Exception(error_message)