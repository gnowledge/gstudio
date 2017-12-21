from gnowsys_ndf.ndf.models import *

all_authors = node_collection.find({'_type': 'Author'})

for each_auth_obj in all_authors:

    u = User.objects.get(id=each_auth_obj.created_by)

    print "\n\ndjango User: "
    print "\tid: ", u.id
    print "\tname: ", u.username
    print "\temail: ", u.email

    print "\nmongo Author: "
    print "\tcreated_by: ", each_auth_obj.created_by
    print "\tname: ", each_auth_obj.name
    print "\temail: ", each_auth_obj.email

    print "Resources Created: ", node_collection.find({'_type': {'$ne': 'Author'}, '$or': [{'created_by': each_auth_obj.created_by}, {'modified_by': each_auth_obj.created_by}, {'contributos': each_auth_obj.created_by}] }).count()
    print "=============================================================="