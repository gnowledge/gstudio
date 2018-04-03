''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

try:
  from bson import ObjectId
except ImportError:  # old pymongo
  from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import node_collection, triple_collection, counter_collection, benchmark_collection
from gnowsys_ndf.ndf.models import Node, db, AttributeType, RelationType, GSystem, GSystemType
from gnowsys_ndf.settings import GSTUDIO_AUTHOR_AGENCY_TYPES, LANGUAGES, OTHER_COMMON_LANGUAGES, GSTUDIO_DEFAULT_SYSTEM_TYPES_LIST
from gnowsys_ndf.settings import GSTUDIO_DEFAULT_LICENSE, GSTUDIO_DEFAULT_LANGUAGE, GSTUDIO_DEFAULT_COPYRIGHT
from gnowsys_ndf.ndf.views.methods import create_gattribute, create_grelation
from gnowsys_ndf.ndf.templatetags.ndf_tags import get_relation_value, get_attribute_value


class Command(BaseCommand):

  help = " This script will add new field(s) into already existing documents " \
      + "(only if they doesn't exists) in your database."

  def handle(self, *args, **options):

    # Keep latest changes in field(s) to be added at top

    # updating project_config for Groups
    proj_config = node_collection.collection.update({'_type':{'$in': [u'Author', u'Group']},'project_config': {'$exists': False} },{'$set': {'project_config': {} }}, upsert=False, multi=True)

    # updating visited_nodes for Counter instances
    counter_objs = counter_collection.collection.update({'_type': 'Counter',
        'visited_nodes': {'$exists': False}},
        {'$set': {'visited_nodes': {}}},upsert=False, multi=True)  
    if counter_objs['nModified']:
        print "\n Updated Counters adding field: visited_nodes for " + counter_objs['nModified'].__str__() + " instances."
          

    # updating access_policy from inconsistent values like 'public', 'Public' to 'PUBLIC'
    all_ap = node_collection.collection.update({'_type': {'$nin': [u'ToReduceDocs']},
     'access_policy': {'$in': [u'public', u'Public', '', None]}},
      {'$set':{'access_policy': u'PUBLIC'} }, upsert=False, multi=True)
    if all_ap['nModified']:
        print "\n `access_policy`: Replaced non u'PUBLIC' values of public nodes to u'PUBLIC' for : " + all_ap['nModified'].__str__() + " instances."

    # --------------------------------------------------------------------------
    # All Triples - Replacing <'lang': ''> field to <'language': []>
    # i.e: removing first 'lang' then adding 'language' with data type: (basestring, basestring)
    all_tr = triple_collection.collection.update({'lang': {'$exists': True}}, {'$unset':{'lang': None}, '$set':{'language': GSTUDIO_DEFAULT_LANGUAGE} }, upsert=False, multi=True)
    if all_tr["updatedExisting"] and all_tr["nModified"]:
        print "\n Replaced 'lang' fields to 'language' for : " + all_tr['nModified'].__str__() + " Triples (AttributeType and RelationType) instances."


    # Adds "legal" field (with default values) to all documents belonging to GSystems.
    all_gs = node_collection.collection.update({'_type': {'$in' : ['GSystem', 'Group', 'Author', 'File']},
                 '$or': [{'legal': {'$exists': False}}, {'license': {'$exists': True}}],
                },
        {'$set': {'legal': {'copyright': GSTUDIO_DEFAULT_COPYRIGHT, 'license': GSTUDIO_DEFAULT_LICENSE}}, 
        '$unset': {'license': None}},upsert=False, multi=True)  


    # all_gs = node_collection.find({'_type': {'$in' : ['GSystem', 'Group', 'Author', 'File']},
    #              '$or': [{'legal': {'$exists': False}}, {'license': {'$exists': True}}],
    #             })
    # all_gs_count = all_gs.count()
    # if all_gs:
    #     print "\n Total GSystems found to update 'legal' field: ", all_gs.count()
    #     for index, each_gs in enumerate(all_gs):
    #         try:
    #             print "\n GSystem: ", index, ' of ', all_gs_count
    #             each_gs.legal = {'copyright': each_gs.license, 'license': GSTUDIO_DEFAULT_LICENSE}
    #             each_gs.pop('license')
    #             each_gs.save()
    #         except AttributeError as noLicense:
    #             print "\n No license found for: ", each_gs._id
    #             pass

    # --------------------------------------------------------------------------
    # Adding <'relation_type_scope': []> field to all RelationType objects
    print "\nUpdating RelationTypes and AttributeTypes."
    rt_res = node_collection.collection.update({'_type': 'RelationType', \
        'relation_type_scope': {'$exists': False} }, \
        {'$set': {'relation_type_scope': [], 'object_scope': [],\
         'subject_scope': [] }}, upsert=False, multi=True)

    if rt_res['updatedExisting']: # and res['nModified']:
        print "\n Added 'scope' fields to " + rt_res['n'].__str__() + " RelationType instances."

    at_res = node_collection.collection.update({'_type': 'AttributeType',\
     'attribute_type_scope': {'$exists': False} }, \
     {'$set': {'attribute_type_scope': [], 'object_scope': [],\
      'subject_scope': [] }}, upsert=False, multi=True)
    if at_res['updatedExisting']: # and res['nModified']:
        print "\n Added 'scope' fields to " + at_res['n'].__str__() + " AttributeType instances."

    print "\nUpdating GRelations and GAttributes."
    grel_res = triple_collection.collection.update({'_type': 'GRelation',\
     '$or': [{'relation_type_scope': {'$eq': None}}, {'subject_scope': \
     {'$exists': False}}, {'object_scope': {'$exists': False}}]},\
     {'$unset': { 'right_subject_scope': ""} , '$set': \
     {'relation_type_scope': {}, 'object_scope': None,\
     'subject_scope': None }}, upsert=False, multi=True)
    if grel_res['updatedExisting']: # and grel_res['nModified']:
        print "\n Added 'scope' fields to " + grel_res['n'].__str__() + " GRelation instances."

    gattr_res = triple_collection.collection.update({'_type': 'GAttribute',\
     '$or': [{'attribute_type_scope': {'$eq': None}}, {'subject_scope': \
     {'$exists': False}}, {'object_scope': {'$exists': False}}]}, \
     {'$unset': { 'object_value_scope': ""} , '$set': \
     {'attribute_type_scope': {}, 'object_scope': None, \
     'subject_scope': None }}, upsert=False, multi=True)
    if gattr_res['updatedExisting']: # and gattr_res['nModified']:
        print "\n Added 'scope' fields to " + gattr_res['n'].__str__() + " GAttribute instances."
    # --------------------------------------------------------------------------

    # updating GRelation nodes to replace relation_type's data of DBRef with ObjectId.
    #
    # all_grelations = triple_collection.find({'_type': 'GRelation'}, time_out=False)
    # all_grelations = triple_collection.find({'_type': 'GRelation','relation_type': {'$type': 'object'}})
    all_grelations = triple_collection.find({
                                            '_type': 'GRelation',
                                            'relation_type': {'$not': {'$type': "objectId"}}
                                            }, time_out=False)

    print "\n Working on Triples data. \n Total GRelations found: ", all_grelations.count()
    print "\n This will take few minutes. Please wait.."
    for each_grelation in all_grelations:
        # print each_grelation
        print '.',
        rt_obj = RelationType(db.dereference(each_grelation.relation_type))
        each_grelation.relation_type = rt_obj._id
        try:
            # each_grelation.save(triple_node=rt_obj,triple_id=rt_obj._id)
            each_grelation.save()
        except Exception as er:
            print "\n Error Occurred while updating Triples data. ", er
            pass

    # updating GRelation nodes to replace relation_type's data of DBRef with ObjectId.
    #
    # all_gattributes = triple_collection.find({'_type': 'GAttribute'}, time_out=False)
    # all_gattributes = triple_collection.find({'_type': 'GAttribute', 'attribute_type': {'$type': 'object'}})
    all_gattributes = triple_collection.find({
                                            '_type': 'GAttribute',
                                            'attribute_type': {'$not': {'$type': "objectId"}}
                                            }, time_out=False)

    print " Total GAttributes found: ", all_gattributes.count()
    print "\n This will take few minutes. Please wait.."
    for each_gattribute in all_gattributes:
        print '.',
        at_obj = AttributeType(db.dereference(each_gattribute.attribute_type))
        each_gattribute.attribute_type = at_obj._id
        # each_gattribute.save(triple_node=at_obj,triple_id=at_obj._id)
        each_gattribute.save()
    # --------------------------------------------------------------------------

    # adding 'assessments' in Counter instances:
    # 'assessment': {
    #             'offered_id': {'total': int, 'correct': int, 'incorrect': int}
    #             }


    ctr_res = counter_collection.collection.update({
                    '_type': 'Counter',
                    '$or': [{'assessment': {'$exists': False}}, {'assessment': {'$not': {'$type': "array"}}}]
                },
                {
                    '$set': {
                            'assessment': [],
                        }
                },
                upsert=False, multi=True)

    if ctr_res['updatedExisting']: # and ctr_res['nModified']:
        print "\n Added 'assessment' field to " + ctr_res['n'].__str__() + " Counter instances."

    benchmark_rec = benchmark_collection.update({'locale': {'$exists': False}}, {'$set':{'locale': 'en'} }, upsert=False, multi=True)

    if benchmark_rec['updatedExisting']: # and benchmark_rec['nModified']:
        print "\n Added 'locale' field to " + benchmark_rec['n'].__str__() + " Benchmark instances."


    # adding 'if_file' in GSystem instances:
    # 'if_file': {
    #         'mime_type': None,
    #         'original': {'_id': None, 'relurl': None},
    #         'mid': {'_id': None, 'relurl': None},
    #         'thumbnail': {'_id': None, 'relurl': None}
    #     },
    gsres = node_collection.collection.update({
                    '_type': {'$in': [u'GSystem'] + GSystem.child_class_names()},
                    'if_file': {'$exists': False}
                },
                {
                    '$set': {
                            'if_file': {
                                'mime_type': None,
                                'original': {'id': None, 'relurl': None},
                                'mid': {'id': None, 'relurl': None},
                                'thumbnail': {'id': None, 'relurl': None}
                            },
                        }
                },
                upsert=False, multi=True)

    if gsres['updatedExisting']: # and gsres['nModified']:
        print "\n Added 'if_file' field to " + gsres['n'].__str__() + " GSystem instances."


    # Adds "legal" field (with default values) to all documents belonging to GSystems.
    all_gs = node_collection.find({'_type': {'$in' : ['GSystem', 'Group', 'Author', 'File']},
                 '$or': [{'legal': {'$exists': False}}, {'license': {'$exists': True}}],
                })
    all_gs_count = all_gs.count()
    print "\n Total GSystems found to update 'legal' field: ", all_gs_count
    for index, each_gs in enumerate(all_gs):
        try:
            print "\n GSystem: ", index, ' of ', all_gs_count
            each_gs.legal = {'copyright': each_gs.license, 'license': GSTUDIO_DEFAULT_LICENSE}
            each_gs.pop('license')
            each_gs.save()
        except AttributeError as noLicense:
            print "\n No license found for: ", each_gs._id
            pass



    # --------------------------------------------------------------------------
    # Adding <'origin': []> field to all objects and inheritance of GSystem class
    # fetching all GSystem and it's inheritance class objects
    # all_gsystem_inherited_nodes = node_collection.find({'_type': {'$in': [u'GSystem', u'File', u'Group']}, 'origin': {'$exists': False} })

    res = node_collection.collection.update({'_type': {'$in': [u'GSystem', u'File', u'Group']}, 'origin': {'$exists': False} }, {'$set': {'origin': [] }}, upsert=False, multi=True)

    if res['updatedExisting']: # and res['nModified']:
        print "\n Added 'origin' field to " + res['n'].__str__() + " GSystem instances."

    # -----------------------------------------------------------------------------

    # Updating language fields data type:
    # - Firstly, replacing None to ('en', 'English')
    node_collection.collection.update({ '_type': {'$in': ['AttributeType',\
     'RelationType', 'MetaType', 'ProcessType', 'GSystemType', 'GSystem',\
      'File', 'Group', 'Author']}, 'language': {'$in': [None, '', u'']} },\
       {"$set": {"language": ('en', 'English')}}, upsert=False, multi=True)

    # language tuple gets save as list type.
    all_nodes = node_collection.find({'_type': {'$in': ['AttributeType',\
     'RelationType', 'MetaType', 'ProcessType', 'GSystemType', 'GSystem',\
      'File', 'Group', 'Author']}, 'language': {'$ne': ['en', 'English']} })

    all_languages = list(LANGUAGES) + OTHER_COMMON_LANGUAGES
    all_languages_concanated = reduce(lambda x, y: x+y, all_languages)

    # iterating over each document in the cursor:
    # - Secondly, replacing invalid language values to valid tuple from settings
    for each_node in all_nodes:
        if each_node.language and (each_node.language in all_languages_concanated):
            for each_lang in all_languages:
                if each_node.language in each_lang:
                    # printing msg without checking update result for performance.
                    print "Updated language field of: ", each_node.name
                    print "\tFrom", each_node.language, " to: ", each_lang, '\n'
                    node_collection.collection.update({'_id': each_node._id}, {"$set": {"language": each_lang}}, upsert=False, multi=False)

    # --- END of Language processing ---


    # adding all activated and logged-in user's id into author_set of "home" and "desk" group ---
    all_authors = node_collection.find({"_type": "Author"})
    authors_list = [auth.created_by for auth in all_authors]

    # updating author_set of desk and home group w.ref. to home group's author_set
    home_group = node_collection.one({"_type":"Group", "name": "home"})
    if home_group:
        prev_home_author_set = home_group.author_set
        total_author_set = list(set(authors_list + home_group.author_set))

        result = node_collection.collection.update({"_type": "Group", "name": {"$in": [u"home", u"desk"]}, "author_set": {"$ne": total_author_set} }, {"$set": {"author_set": total_author_set}}, upsert=False, multi=True )

        if result['updatedExisting']: # and result['nModified']:
            home_group.reload()
            print "\n Updated author_set of 'home' and 'desk' group:" + \
                "\n\t - Previously it was   : " + str(len(prev_home_author_set)) + " users."\
                "\n\t - Now it's updated to : " + str(len(home_group.author_set)) + " users."


    # --------------------------------------------------------------------------
    # 'group_admin' of group should not be empty. So updating one for [] with creator of group.
    all_groups = node_collection.find({'_type': 'Group'})
    for each_group in all_groups:
        if not each_group.group_admin:
            res = node_collection.collection.update({'_id': ObjectId(each_group._id)}, {'$set': {'group_admin': [each_group.created_by]}}, upsert=False, multi=False)

            if res['updatedExisting']:
                each_group.reload()
                print 'updated group_admin of: ' + each_group.name + ' from [] to :' + unicode(each_group.group_admin)


    # --------------------------------------------------------------------------
    # removing <'partner': bool> field from Group objects
    res = node_collection.collection.update({'_type': {'$in': ['Group']}}, {'$unset': {'partner': False }}, upsert=False, multi=True)

    if res['updatedExisting']: # and res['nModified']:
        print "\n Removed 'partner' field from " + res['n'].__str__() + " Group instances."


    # --------------------------------------------------------------------------
    # Adding <'moderation_level': -1> field to Group objects
    res = node_collection.collection.update({'_type': {'$in': ['Group']}, 'edit_policy': {'$nin': ['EDITABLE_MODERATED']}, 'moderation_level': {'$exists': False}}, {'$set': {'moderation_level': -1 }}, upsert=False, multi=True)

    if res['updatedExisting']: # and res['nModified']:
        print "\n Added 'moderation_level' field to " + res['n'].__str__() + " Group instances."


    # -----------------------------------------------------------------------------
    # Replacing invalid value of agency_type field belonging to Author node by "Other"
    res = node_collection.collection.update(
        {"_type": "Author", "agency_type": {"$nin": GSTUDIO_AUTHOR_AGENCY_TYPES}},
        {"$set": {"agency_type": u"Other"}},
        upsert=False, multi=True
    )
    if res['updatedExisting']: # and res['nModified']:
        print "\n Replacing invalid value of agency_type field belonging to Author node by 'Other'" + \
            "... #" + res["n"].__str__() + " records updated."


    # -----------------------------------------------------------------------------
    # From existing RelationType instance(s), finding Binary relationships
    # and Setting their "member_of" field's value as "Binary" (MetaType)
    mt_binary = node_collection.one({
        '_type': "MetaType", 'name': "Binary"
    })
    if mt_binary:
        res = node_collection.collection.update({
            "_type": "RelationType", "object_type.0": {"$not": {"$type": 4}}
        }, {
            "$set": {"member_of": [mt_binary._id]}
        },
            upsert=False, multi=True
        )
        if res["updatedExisting"]: # and res["nModified"]:
            print "\n 'member_of' field updated in following RelationType " \
                + "instance(s) representing 'Binary Relationships':", res["n"]

    # Replacing object_type of "trainer_of_course" & "master_trainer_of_course"
    # relationship from "Announced Course" to "NUSSD Course"
    nussd_course = node_collection.one({
        '_type': "GSystemType", 'name': "NUSSDCourse"
    })
    if nussd_course:
        nussd_course_id = nussd_course._id
        res = node_collection.collection.update({
            '_type': "RelationType", 'name': "trainer_of_course", "object_value": {"$nin": [nussd_course_id]}
        }, {
            '$set': {'object_type': [nussd_course_id]}
        },
            upsert=False, multi=False
        )
        if res['updatedExisting']: # and res['nModified']:
            print "\n Replaced object_type of 'trainer_of_course' relationship" \
                + " from 'Announced Course' to 'NUSSD Course'."

        res = node_collection.collection.update({
            '_type': "RelationType", 'name': "master_trainer_of_course", "object_value": {"$nin": [nussd_course_id]}
        }, {
            '$set': {'object_type': [nussd_course_id]}
        },
            upsert=False, multi=False
        )
        if res['updatedExisting']: # and res['nModified']:
            print "\n Replaced object_type of 'master_trainer_of_course' relationship" \
                + " from 'Announced Course' to 'NUSSD Course'."

    # Appending attribute_type_set and relation_type_set fields to existing MetaType nodes
    res = node_collection.collection.update(
        {'_type': "MetaType", "attribute_type_set": {"$exists": False}, "relation_type_set": {"$exists": False}},
        {'$set': {'attribute_type_set': [], 'relation_type_set': []}},
        upsert=False, multi=True
    )
    if res['updatedExisting']: # and res['nModified']:
        print "\n Appending attribute_type_set and relation_type_set fields to existing MetaType nodes."

    # Renames RelaionType names -- "has_corresponding_task" to "has_current_approval_task"
    res = node_collection.collection.update(
        {'_type': "RelationType", 'name': u"has_corresponding_task"},
        {'$set': {'name': u"has_current_approval_task"}},
        upsert=False, multi=False
    )
    if res['updatedExisting']: # and res['nModified']:
        print "\n 'name' field updated of RelationType (Renamed from has_corresponding_task to has_current_approval_task)"

    # Replaces "for_acourse" RelationType's object_cardinality field's value from 1 to 100
    res = node_collection.collection.update(
        {'_type': "RelationType", 'name': "for_acourse"},
        {'$set': {'object_cardinality': 100}},
        upsert=False, multi=False
    )

    if res['updatedExisting']: # and res['nModified']:
        print "\n Replaced 'for_acourse' RelationType's 'object_cardinality' field's value from 1 to 100."

    file_gst = node_collection.one({'_type':'GSystemType', 'name': 'File'})
    pandora_video_st = node_collection.one({'_type':'GSystemType', 'name':'Pandora_video'})
    # Update the url field of all nodes
    # if pandora_video_st:
    #     nodes = node_collection.find({'member_of': {'$nin':[pandora_video_st._id],'$in':[file_gst._id]},'access_policy':'PUBLIC' })
    #     site = Site.objects.get(pk=1)
    #     site = site.domain.__str__()
    #     site = "127.0.0.1:8000" if (site == u'example.com') else site

    #     count = 0

    #     for each in nodes:
    #         grp_name = node_collection.one({'_id': ObjectId(each.group_set[0]) }).name
    #         if "/" in each.mime_type:
    #             filetype = each.mime_type.split("/")[1]

    #             url_link = "http://" + site + "/" + grp_name.replace(" ","%20").encode('utf8') + "/file/readDoc/" + str(each._id) + "/" + str(each.name) + "." + str(filetype)

    #             if each.url != unicode(url_link):
    #                 node_collection.collection.update({'_id':each._id},{'$set':{'url': unicode(url_link) }})
    #                 count = count + 1

    #     if count:
    #         print "\n 'url' field updated in following no. of documents: ", count

    # Update pandora videos 'member_of', 'created_by', 'modified_by', 'contributors' field
    if User.objects.filter(username='nroer_team').exists():
        auth_id = User.objects.get(username='nroer_team').pk
        if auth_id and pandora_video_st:
            res = node_collection.collection.update(
                {'_type': 'File', 'member_of': {'$in': [pandora_video_st._id]}, 'created_by': {'$ne': auth_id} },
                {'$set': {'created_by': auth_id, 'modified_by': auth_id, 'member_of':[file_gst._id, pandora_video_st._id]}, '$push': {'contributors': auth_id} },
                upsert=False, multi=True
            )

            if res['updatedExisting']: # and res['nModified']:
                print "\n 'created_by, modified_by & contributors' field updated for pandora videos in following no. of documents: ", res['n']


    # Update prior_node for each node in DB who has its collection_set
    all_nodes = node_collection.find({'_type': {'$in': ['GSystem', 'File', 'Group']},'collection_set': {'$exists': True, '$not': {'$size': 0}} })
    count = 0
    for each in all_nodes:
        if each.collection_set:
            for l in each.collection_set:
                obj = node_collection.one({'_id': ObjectId(l) })
                if obj:
                    if each._id not in obj.prior_node:
                        node_collection.collection.update({'_id':obj._id},{'$push':{'prior_node': ObjectId(each._id) }})
                        count = count + 1

    if count:
        print "\n prior_node field updated in following no. of documents: ", count

    # Updating names (Stripped) in all theme , theme_items and topic documents
    theme_GST = node_collection.one({'_type':'GSystemType','name': 'Theme'})
    theme_item_GST = node_collection.one({'_type':'GSystemType','name': 'theme_item'})
    topic_GST = node_collection.one({'_type':'GSystemType','name': 'Topic'})
    if theme_GST and theme_item_GST and topic_GST:
        nodes = node_collection.find({'member_of': {'$in': [theme_GST._id, theme_item_GST._id,topic_GST._id]} })
        count = 0
        for each in nodes:
            if each.name != each.name.strip():
                node_collection.collection.update({'_id':ObjectId(each._id)},{'$set': {'name': each.name.strip()} })
                count = count + 1

        if count:
            print "\n Name field updated (Stripped) in following no. of documents: ", count

    # Update's "status" field from DRAFT to PUBLISHED for all TYPE's node(s)
    res = node_collection.collection.update(
        {'_type': {'$in': ["MetaType", "GSystemType", "RelationType", "AttributeType"]}, 'status': u"DRAFT"},
        {'$set': {'status': u"PUBLISHED"}},
        upsert=False, multi=True
    )
    if res['updatedExisting']: # and res['nModified']:
        print "\n 'status' field updated for all TYPE's node(s) in following no. of documents: ", res['n']

    # Update object_value of GAttribute(s) of "Assignee" AttributeType
    # Find those whose data-type is not list/Array
    # Replace those as list of value(s)
    assignee_at = node_collection.one(
        {'_type': "AttributeType", 'name': "Assignee"}
    )
    assignee_at = False
    if assignee_at:
        res = 0
        assignee_cur = triple_collection.find(
            {'_type': "GAttribute", 'attribute_type': assignee_at._id}
        )

        for each in assignee_cur:
            # If string
            ul_sv = []
            if type(each.object_value) in [str, unicode]:
                if "," in each.object_value and "[" in each.object_value and "]" in each.object_value:
                    ul_sv = each.object_value.strip("[]").replace(", ", ",").replace(" ,", ",").split(",")
                elif "," in each.object_value:
                    ul_sv = each.object_value.replace(", ", ",").replace(" ,", ",").split(",")
                elif "[" in each.object_value or "]" in each.object_value:
                    ul_sv = each.object_value.strip("[]").split(",")

                ul_id = []
                for u in ul_sv:
                    if not u.isdigit():
                        user = User.objects.get(username=u)
                    else:
                        user = User.objects.get(id=int(u))
                    if user:
                        if user.id not in ul_id:
                            ul_id.append(user.id)

                upres = triple_collection.collection.update(
                            {'_id': each._id},
                            {'$set': {'object_value': ul_id}},
                            upsert=False, multi=False
                        )
                res += upres['n']

            # If list
            elif type(each.object_value) == list:
                ul_id = []
                for u in each.object_value:
                    if type(u) in [str, unicode] and not u.isdigit():
                        if u.strip("[]"):
                            user = User.objects.get(username=u)
                    elif type(u) in [str, unicode] and u.isdigit():
                        if u.strip("[]"):
                            user = User.objects.get(id=int(u))
                    else:
                        user = User.objects.get(id=int(u))

                    if user:
                        if user.id not in ul_id:
                            ul_id.append(user.id)

                upres = triple_collection.collection.update(
                            {'_id': each._id},
                            {'$set': {'object_value': ul_id}},
                            upsert=False, multi=False
                        )
                res += upres['n']

        if res:
            print "\n Updated following no. of Assignee GAttribute document(s): ", res

    # Updates already created has_profile_pic grelations' status - Except latest one (PUBLISHED) others' are set to DELETED
    has_profile_pic = node_collection.one({'_type': "RelationType", 'name': u"has_profile_pic"})
    if has_profile_pic:
        op = triple_collection.collection.aggregate([
            {'$match': {
            '_type': "GRelation",
            'relation_type': has_profile_pic._id
            }},
            {'$group': {
            '_id': {'auth_id': "$subject"},
            'pp_data': {'$addToSet': {'gr_id': "$_id", 'status': "$status"}}
            }}
        ])

        res = 0
        for each in op["result"]:
            auth_id = each["_id"]["auth_id"]
            pub_id = None
            pub_res = 0
            del_id = []
            del_res = 0

            for l in each["pp_data"]:
                if l["status"] == u"PUBLISHED":
                    pub_id = l["gr_id"]

                else:
                    del_id.append(l["gr_id"])

            if not pub_id:
                pub_id = each["pp_data"][len(each["pp_data"])-1]["gr_id"]
                pub_res = node_collection.collection.update({'_id': pub_id}, {'$set': {'status': u"PUBLISHED"}}, upsert=False, multi=False)
                pub_res = pub_res['n']
                del_id.pop()

            del_res = node_collection.collection.update({'_id': {'$in': del_id}}, {'$set': {'status': u"DELETED"}}, upsert=False, multi=True)

            if pub_res or del_res['n']:
                res += 1

        if res:
            print "\n Updated following no. of has_profile_pic GRelation document(s): ", res

    # Updates the value of object_cardinality to 100. So that teaches will behave as 1:M (one-to-many) relation.
    teaches = node_collection.one({'_type': "RelationType", 'name': "teaches"})
    if teaches:
        res = node_collection.collection.update({'_id': teaches._id, 'object_cardinality': {'$ne': 100}},
                {'$set': {'object_cardinality': 100}},
                upsert=False, multi=False
            )
        if res["updatedExisting"]:
            print "\n 'teaches' RelationType updated with object_cardinality: 100. Changed document: ", res['n']
        else:
            print "\n 'teaches' RelationType: no need to update."

    # Replacing object_type of "has_course" relationship from "NUSSD Course" to "Announced Course"
    ann_course = node_collection.one({'_type': "GSystemType", 'name': "AnnouncedCourse"})
    if ann_course:
        res = node_collection.collection.update({'_type': "RelationType", 'name': "has_course"},
                {'$set': {'object_type': [ann_course._id]}},
                upsert=False, multi=False
              )
        if res['updatedExisting']: # and res['nModified']:
            print "\n Replaced object_type of 'has_course' relationship from 'NUSSD Course' to 'Announced Course'."

    # Adds "relation_set" field (with default value as []) to all documents belonging to GSystems.
    res = node_collection.collection.update({'_type': {'$nin': ["MetaType", "GSystemType", "RelationType", "AttributeType", "GRelation", "GAttribute", "ReducedDocs", "ToReduceDocs", "IndexedWordList", "node_holder"]}, 'relation_set': {'$exists': False}},
                            {'$set': {'relation_set': []}},
                            upsert=False, multi=True
    )
    if res['updatedExisting']: # and res['nModified']:
        print "\n 'relation_set' field added to following no. of documents: ", res['n']

    # Adds "attribute_set" field (with default value as []) to all documents belonging to GSystems.
    res = node_collection.collection.update({'_type': {'$nin': ["MetaType", "GSystemType", "RelationType", "AttributeType", "GRelation", "GAttribute", "ReducedDocs", "ToReduceDocs", "IndexedWordList", "node_holder"]}, 'attribute_set': {'$exists': False}},
                            {'$set': {'attribute_set': []}},
                            upsert=False, multi=True
    )
    if res['updatedExisting']: # and res['nModified']:
        print "\n 'attribute_set' field added to following no. of documents: ", res['n']

    '''
    Replace foll. with legal field update code - katkamrachana
    # Adds "license" field (with default value as "") to all documents belonging to GSystems.
    res = node_collection.collection.update({'_type': {'$nin': ["MetaType", "GSystemType", "RelationType", "AttributeType", "GRelation", "GAttribute", "ReducedDocs", "ToReduceDocs", "IndexedWordList", "node_holder"]}, 'license': {'$exists': False}},
                            {'$set': {'license': None}},
                            upsert=False, multi=True
    )
    if res['updatedExisting']: # and res['nModified']:
        print "\n 'license' field added to following no. of documents: ", res['n']
    '''

    # Adding "Agency_type" field adding to group documents with default values
    res = node_collection.collection.update({'_type': {'$in': ['Group']}, 'agency_type': {'$exists': False}},
                            {'$set': {'agency_type': "Project" }},
                            upsert=False, multi=True
    )
    if res['updatedExisting']: # and res['nModified']:
       print "\n 'agency_type' field added to 'Group' documents totalling to : ", res['n']

    # Adding "Agency_type" field adding to author documents with default values
    res = node_collection.collection.update({'_type': {'$in': ['Author']}, 'agency_type': {'$exists': False}},
                            {'$set': {'agency_type': "Others" }},
                            upsert=False, multi=True
    )
    if res['updatedExisting']: # and res['nModified']:
       print "\n 'agency_type' field added to 'Author' documents totalling to : ", res['n']


    # Modify language field with unicode value if any document has language with dict datatype
    res = node_collection.collection.update({'language': {}},
                            {'$set': {'language': u""}},
                            upsert=False, multi=True
    )

    # Removing existing "cr_or_xcr" field with no default value
    res = node_collection.collection.update({'_type': {'$in': ['Group']}, 'cr_or_xcr': {'$exists': True}},
                            {'$unset': {'cr_or_xcr': False }},
                            upsert=False, multi=True
    )
    if res['updatedExisting']: # and res['nModified']:
       print "\n Already existing 'cr_or_xcr' field removed from documents totalling to : ", res['n']

    # Adding "curricular" field with no default value
    res = node_collection.collection.update({'_type': {'$in': ['Group']}, 'curricular': {'$exists': False}},
                            {'$set': {'curricular': False }},
                            upsert=False, multi=True
    )
    if res['updatedExisting']: # and res['nModified']:
        print "\n 'curricular' field added to all Group documents totalling to : ", res['n']

    # Removing existing "partners" field with no default value
    res = node_collection.collection.update({'_type': {'$in': ['Group']}, 'partners': {'$exists': True}},
                            {'$unset': {'partners': False }},
                            upsert=False, multi=True
    )
    if res['updatedExisting']: # and res['nModified']:
       print "\n Already existing 'partners' field removed from documents totalling to : ", res['n']

    # # Adding "partner" field with no default value
    # res = node_collection.collection.update({'_type': {'$in': ['Group']}, 'partner': {'$exists': False}},
    #                         {'$set': {'partner': False }},
    #                         upsert=False, multi=True
    # )
    # if res['updatedExisting']: # and res['nModified']:
    #     print "\n 'partner' field added to all Group documents totalling to : ", res['n']

    # Adding "preferred_languages" field with no default value
    res = node_collection.collection.update({'_type': {'$in': ['Author']}, 'preferred_languages': {'$exists': False}},
                            {'$set': {'preferred_languages': {}}},
                            upsert=False, multi=True
    )
    if res['updatedExisting']: # and res['nModified']:
        print "\n 'preferred_languages' field added to all author documents totalling to : ", res['n']


    # Adding "rating" field with no default value
    res = node_collection.collection.update({'_type': {'$nin': ['GAttribute', 'GRelation', "ReducedDocs", "ToReduceDocs", "IndexedWordList", "node_holder"]}, 'rating': {'$exists': False}},
                            {'$set': {'rating': []}},
                            upsert=False, multi=True
    )
    if res['updatedExisting']: # and res['nModified']:
        print "\n 'rating' field added to following no. of documents: ", res['n']

    # Adds 'subject_scope', 'attribute_type_scope', 'object_value_scope' field (with default value as "") to all documents which belongs to GAttribute
    res = node_collection.collection.update({'_type': {'$in': ["Group", "Author"]}, 'group_admin': {'$exists': False}},
                            {'$set': {'group_admin': []}},
                            upsert=False, multi=True
    )
    if res['updatedExisting']: # and res['nModified']:
        print "\n 'group_admin' field added to following no. of documents: ", res['n']

    # Adds 'subject_scope', 'attribute_type_scope', 'object_value_scope' field (with default value as "") to all documents which belongs to GAttribute
    res = triple_collection.collection.update({'_type': "GAttribute", 'subject_scope': {'$exists': False}, 'attribute_type_scope': {'$exists': False}, 'object_value_scope': {'$exists': False}},
                            {'$set': {'subject_scope':"", 'attribute_type_scope':"", 'object_value_scope': ""}},
                            upsert=False, multi=True
    )
    if res['updatedExisting']: # and res['nModified']:
        print "\n 'subject_scope', 'attribute_type_scope', 'object_value_scope' fields added to following no. of documents: ", res['n']

    # Adds 'subject_scope', 'relation_type_scope', 'right_subject_scope' field (with default value as "") to all documents which belongs to GRelation
    res = triple_collection.collection.update({'_type': "GRelation", 'subject_scope': {'$exists': False}, 'relation_type_scope': {'$exists': False}, 'right_subject_scope': {'$exists': False}},
                            {'$set': {'subject_scope':"", 'relation_type_scope':"", 'right_subject_scope': ""}},
                            upsert=False, multi=True
    )
    if res['updatedExisting']: # and res['nModified']:
        print "\n 'subject_scope', 'relation_type_scope', 'right_subject_scope' fields added to following no. of documents: ", res['n']

    # Adds "annotations" field (with default value as []) to all documents belonging to GSystems
    res = node_collection.collection.update({'_type': {'$nin': ["MetaType", "GSystemType", "RelationType", "AttributeType", "GRelation", "GAttribute", "ReducedDocs", "ToReduceDocs", "IndexedWordList", "node_holder"]}, 'annotations': {'$exists': False}},
                            {'$set': {'annotations': []}},
                            upsert=False, multi=True
    )
    if res['updatedExisting']: # and res['nModified']:
        print "\n annotations field added to following no. of documents: ", res['n']

    # Adds "group_set" field (with default value as []) to all documents except those which belongs to either GAttribute or GRelation
    res = node_collection.collection.update({'_type': {'$nin': ["GAttribute", "GRelation", "ReducedDocs", "ToReduceDocs", "IndexedWordList", "node_holder"]}, 'group_set': {'$exists': False}},
                            {'$set': {'group_set': []}},
                            upsert=False, multi=True
    )
    if res['updatedExisting']: # and res['nModified']:
        print "\n group_set field added to following no. of documents: ", res['n']

    # Adds "property_order" field (with default value as []) to all documents except those which belongs to either GAttribute or GRelation
    res = node_collection.collection.update({'_type': {'$nin': ["GAttribute", "GRelation", "ReducedDocs", "ToReduceDocs", "IndexedWordList", "node_holder"]}, 'property_order': {'$exists': False}},
                            {'$set': {'property_order': []}},
                            upsert=False, multi=True
    )
    if res['updatedExisting']: # and res['nModified']:
        print "\n property_order field added to following no. of documents: ", res['n']

    # Adding "modified_by" field with None as it's default value
    res = node_collection.collection.update({'_type': {'$nin': ['GAttribute', 'GRelation', "ReducedDocs", "ToReduceDocs", "IndexedWordList", "node_holder"]}, 'modified_by': {'$exists': False}},
                            {'$set': {'modified_by': None}},
                            upsert=False, multi=True
    )
    if res['updatedExisting']: # and res['nModified']:
        print "\n modified_by field added to following no. of documents: ", res['n']

    # Adding "complex_data_type" field with empty list as it's default value
    res = node_collection.collection.update({'_type': 'AttributeType', 'complex_data_type': {'$exists': False}},
                            {'$set': {'complex_data_type': []}},
                            upsert=False, multi=True
    )
    if res['updatedExisting']: # and res['nModified']:
        print "\n complex_data_type field added to following no. of documents: ", res['n']

    # Adding "post_node" field with empty list as it's default value
    res = node_collection.collection.update({'_type': {'$nin': ['GAttribute', 'GRelation', "ReducedDocs", "ToReduceDocs", "IndexedWordList", "node_holder"]}, 'post_node': {'$exists': False}},
                            {'$set': {'post_node': []}},
                            upsert=False, multi=True
    )
    if res['updatedExisting']: # and res['nModified']:
        print "\n post_node field added to following no. of documents: ", res['n']

    # Adding "collection_set" field with empty list as it's default value
    res = node_collection.collection.update({'_type': {'$nin': ['GAttribute', 'GRelation', "ReducedDocs", "ToReduceDocs", "IndexedWordList", "node_holder"]}, 'collection_set': {'$exists': False}},
                            {'$set': {'collection_set': []}},
                            upsert=False, multi=True
    )
    if res['updatedExisting']: # and res['nModified']:
        print "\n collection_set field added to following no. of documents: ", res['n']

    # Adding "location" field with no default value
    res = node_collection.collection.update({'_type': {'$nin': ['GAttribute', 'GRelation', "ReducedDocs", "ToReduceDocs", "IndexedWordList", "node_holder"]}, 'location': {'$exists': False}},
                            {'$set': {'location': []}},
                            upsert=False, multi=True
    )
    if res['updatedExisting']: # and res['nModified']:
        print "\n location field added to following no. of documents: ", res['n'],"\n"

    # Adding "language" field with no default value
    res = node_collection.collection.update({'_type': {'$nin': ['GAttribute', 'GRelation', "ReducedDocs", "ToReduceDocs", "IndexedWordList", "node_holder"]}, 'language': {'$exists': False}},
                            {'$set': {'language': unicode('')}},
                            upsert=False, multi=True
    )

    # Adding "access_policy" field
    # For Group documents, access_policy value is set depending upon their
    # group_type values, i.e. either PRIVATE/PUBLIC whichever is there
    node_collection.collection.update({'_type': 'Group', 'group_type': 'PRIVATE'}, {'$set': {'access_policy': u"PRIVATE"}}, upsert=False, multi=True)
    node_collection.collection.update({'_type': 'Group', 'group_type': 'PUBLIC'}, {'$set': {'access_policy': u"PUBLIC"}}, upsert=False, multi=True)

    # For Non-Group documents which doesn't consits of access_policy field, add it with PUBLIC as it's default value
    node_collection.collection.update({'_type': {'$nin': ['Group', 'GAttribute', 'GRelation', "ReducedDocs", "ToReduceDocs", "IndexedWordList", "node_holder"]}, 'access_policy': {'$exists': False}}, {'$set': {'access_policy': u"PUBLIC"}}, upsert=False, multi=True)

    node_collection.collection.update({'_type': {'$nin': ['Group', 'GAttribute', 'GRelation', "ReducedDocs", "ToReduceDocs", "IndexedWordList", "node_holder"]}, 'access_policy': {'$in': [None, "PUBLIC"]}}, {'$set': {'access_policy': u"PUBLIC"}}, upsert=False, multi=True)
    node_collection.collection.update({'_type': {'$nin': ['Group', 'GAttribute', 'GRelation', "ReducedDocs", "ToReduceDocs", "IndexedWordList", "node_holder"]}, 'access_policy': "PRIVATE"}, {'$set': {'access_policy': u"PRIVATE"}}, upsert=False, multi=True)

    gstpage_node = node_collection.find_one({"name":"Page"})
    gstwiki = node_collection.find_one({"name":"Wiki page"})

    # page_nodes = node_collection.find({"member_of":gstpage_node._id})
    # for i in page_nodes:
    #     if gstwiki._id not in i.type_of:
    #         i.type_of.append(gstwiki._id)
    #         i.save()
    #     else:
    #         print i.name,"Page already Updated"

    nodes = node_collection.find({"_type":"Author",
            '$or':[{'language_proficiency':{'$exists':False}},{'subject_proficiency':{'$exists':False}}]})
    for i in nodes:
            node_collection.collection.update({'_id':ObjectId(i._id)}, {'$set':{'language_proficiency': '','subject_proficiency':'' }},upsert=False, multi=False)
            print i.name, "Updated !!"



    # Add attributes to discussion thread for every page node.
    # If thread does not exist, create it.
    # pages_files_not_updated = []
    '''
    Commented on Dec 5 2015 katkam.rachana@gmail.com to avoid unnecessary processing. This is a one-time script

    pages_files_not_updated = {}
    page_gst = node_collection.one( { '_type': "GSystemType", 'name': "Page" })
    file_gst = node_collection.one( { '_type': "GSystemType", 'name': "File" })
    page_file_cur = node_collection.find( { 'member_of': {'$in':[page_gst._id, file_gst._id]} , 'status': { '$in': [u'DRAFT', u'PUBLISHED']}} ).sort('last_update', -1)
    has_thread_rt = node_collection.one({"_type": "RelationType", "name": u"has_thread"})
    twist_gst = node_collection.one({'_type': 'GSystemType', 'name': 'Twist'})
    reply_gst = node_collection.one({'_type': 'GSystemType', 'name': 'Reply'})
    rel_resp_at = node_collection.one({'_type': 'AttributeType', 'name': 'release_response'})
    thr_inter_type_at = node_collection.one({'_type': 'AttributeType', 'name': 'thread_interaction_type'})
    discussion_enable_at = node_collection.one({"_type": "AttributeType", "name": "discussion_enable"})
    all_count =  page_file_cur.count()
    print "\n Total pages and files found : ", all_count
    print "\n Processing " + str(all_count) + " will take time. Plase hold on ...\n"
    for idx, each_node in enumerate(page_file_cur):
        try:
            # print "Processing #",idx, " of ",all_count
            print ".",
            # print "\nPage# ",idx, "\t - ", each_node._id, '\t - ' , each_node.name, each_node.attribute_set
            release_response_val = True
            interaction_type_val = unicode('Comment')
            userid = each_node.created_by
            thread_obj = node_collection.one({"_type": "GSystem", "member_of": ObjectId(twist_gst._id), "prior_node": ObjectId(each_node._id)})
            release_response_status = False
            thread_interaction_type_status = False
            discussion_enable_status = False
            has_thread_status = False
            # if get_attribute_value(each_node._id,"discussion_enable") != "":
            #     discussion_enable_status = True
            if get_relation_value(each_node._id,"has_thread") != ("",""):
                has_thread_status = True

            if thread_obj:
                reply_cur = node_collection.find({'prior_node': each_node._id, 'member_of': reply_gst._id})
                if reply_cur:
                    for each_rep in reply_cur:
                        node_collection.collection.update({'_id': each_rep._id},{'$set':{'prior_node':[thread_obj._id]}}, upsert = False, multi = False)
                        each_rep.reload()

                # creating GRelation
                if not has_thread_status:
                    gr = create_grelation(each_node._id, has_thread_rt, thread_obj._id)
                    each_node.reload()
                if get_attribute_value(thread_obj._id,"release_response") != "":
                    release_response_status = True
                if get_attribute_value(thread_obj._id,"thread_interaction_type") != "":
                    thread_interaction_type_status = True
                if not release_response_status:
                    if release_response_val:
                        create_gattribute(thread_obj._id, rel_resp_at, release_response_val)
                        thread_obj.reload()

                if not thread_interaction_type_status:
                    if interaction_type_val:
                        create_gattribute(thread_obj._id, thr_inter_type_at, interaction_type_val)
                        thread_obj.reload()
                # print "\nThread_obj updated with new attr", thread_obj.attribute_set, '\n\n'
            else:
                thread_obj = node_collection.one({"_type": "GSystem", "member_of": ObjectId(twist_gst._id),"relation_set.thread_of": ObjectId(each_node._id)})

            if thread_obj:
                if get_attribute_value(each_node._id,"discussion_enable") != True:
                    create_gattribute(each_node._id, discussion_enable_at, True)
            else:
                if get_attribute_value(each_node._id,"discussion_enable") != False:
                    create_gattribute(each_node._id, discussion_enable_at, False)
                # print "\n\n discussion_enable False"
        except Exception as e:

            pages_files_not_updated[str(each_node._id)] = str(e)
            print "\n\nError occurred for page ", each_node._id, "--", each_node.name,"--",e
            # print e, each_node._id
            pass
    print "\n------- Discussion thread for Page and File GST successfully completed-------\n"
    print "\n\n Pages/Files that were not able to updated\t", pages_files_not_updated
    '''
    # Correct Eventype and CollegeEventtype Node  by setting their modified by field
    glist = node_collection.one({'_type': "GSystemType", 'name': "GList"})
    if glist:
        event_type_node_cur = node_collection.find({'member_of':ObjectId(glist._id),"name":{'$in':['Eventtype','CollegeEvents']}})
        for i in event_type_node_cur:
            i.modified_by = 1
            i.save()
            print "Updated",i.name,"'s modified by feild from null to 1"

    

    # Adding default st. -katkamrachana

    default_st_cur = node_collection.find({'_type': 'GSystemType',
                    'name': {'$in': GSTUDIO_DEFAULT_SYSTEM_TYPES_LIST}})
    default_st_ids = [st._id for st in default_st_cur]


    print "\n RelationTypes and AttributeTypes to add GSTUDIO_DEFAULT_SYSTEM_TYPES_LIST."
    rt_res_default_st = node_collection.collection.update({'_type': 'RelationType',
        '$or': [{'subject_type': {'$nin': default_st_ids}}, {'object_type': {'$nin': default_st_ids}}]}, \
        {'$addToSet': {'subject_type': {'$each': default_st_ids}, 'object_type': {'$each': default_st_ids},\
        }}, upsert=False, multi=True)

    if rt_res_default_st['updatedExisting']: # and res['nModified']:
        print "\n Added 'GSTUDIO_DEFAULT_SYSTEM_TYPES_LIST' ids to " + rt_res_default_st['n'].__str__() + " RelationType instances."

    at_res_default_st = node_collection.collection.update({'_type': 'AttributeType',
        'subject_type': {'$nin': default_st_ids}}, \
     {'$addToSet': {'subject_type': {'$each': default_st_ids}}}, upsert=False, multi=True)

    if at_res_default_st['updatedExisting']: # and res['nModified']:
        print "\n Added 'GSTUDIO_DEFAULT_SYSTEM_TYPES_LIST' ids to " + at_res_default_st['n'].__str__() + " AttributeType instances."

    # For all right_subject nodes of 'translation_of' GRelations,
    # add member_of of 'trans_node' GST
    trans_node_gst_name, trans_node_gst_id = GSystemType.get_gst_name_id("trans_node")

    rt_translation_of = Node.get_name_id_from_type('translation_of', 'RelationType', get_obj=True)

    all_translations_grels = triple_collection.find({
                            '_type': u'GRelation',
                            'relation_type': rt_translation_of._id
                        },{'right_subject': 1})
    right_subj_ids = [each_rs.right_subject for each_rs in all_translations_grels]
    right_subj_update_res = node_collection.collection.update(
                                {'_id': {'$in': right_subj_ids}, 'member_of': {'$nin': [trans_node_gst_id]}},
                                {'$set': {'member_of': [trans_node_gst_id]}},
                                upsert=False, multi=True)
    if right_subj_update_res['updatedExisting']: # and res['nModified']:
        print "\n Added 'trans_node' _id in " + right_subj_update_res['n'].__str__() + " 'translation_of' right_subject instances."


    # changing member_of from `activity` to `Page`
    print "\nReplacing member_of field from 'activity' to'Page'"

    activity_gst = node_collection.one({'_type': 'GSystemType', 'name': 'activity'})
    if activity_gst:
      activity_cur = node_collection.find({'member_of': activity_gst._id})
      print "\n Activities found: ", activity_cur.count()
      page_gst = node_collection.one({'_type': 'GSystemType', 'name': 'Page'})
      wiki_page_gst = node_collection.one({'_type': 'GSystemType', 'name': 'Wiki page'})
      activity_gs_mem_update_res = node_collection.collection.update({'member_of': activity_gst._id},
        {'$set': {'member_of': [page_gst._id], 'type_of': [wiki_page_gst._id]}} ,upsert=False, multi=True)
      if activity_gs_mem_update_res['updatedExisting']: # and res['nModified']:
          print "\n Replaced member_of field from 'activity' to'Page' in " + activity_gs_mem_update_res['n'].__str__() + " instances."
