from gnowsys_ndf.ndf.models import *

def main():
    # all users
    all_users = User.objects.all()
    # list of all users ids
    all_users_ids_list = User.objects.all().values_list('id', flat=True)
    # all authors
    all_authors = node_collection.find({'_type': 'Author'})
    all_authors_created_by_list = [a.created_by for a in all_authors] 
    all_authors.rewind()

    all_users_ids_list = User.objects.all().values_list('id', flat=True)

    ids_diff_authors_minus_users = list(set(all_authors_created_by_list) - set(all_users_ids_list))
    ids_diff_users_minus_authors = list(set(all_users_ids_list) - set(all_authors_created_by_list))

    ids_diff_authors_minus_users_gs_creations = node_collection.find({'_type': 'GSystem', 'created_by': {'$in': ids_diff_authors_minus_users } })
    ids_diff_users_minus_authors_gs_creations = node_collection.find({'_type': 'GSystem', 'created_by': {'$in': ids_diff_users_minus_authors } })


    # TO PRINT:
    print "all_users.count(): ", all_users.count()
    print "all_authors.count(): ", all_authors.count()
    print "\n"
    print "ids_diff_authors_minus_users: ", list(ids_diff_authors_minus_users)
    print "len(ids_diff_authors_minus_users): ", len(ids_diff_authors_minus_users)
    print "\n"
    print "ids_diff_users_minus_authors: ", list(ids_diff_users_minus_authors)
    print "len(ids_diff_users_minus_authors): ", len(ids_diff_users_minus_authors)
    print "\n"
    print "ids_diff_authors_minus_users_gs_creations.count(): ", ids_diff_authors_minus_users_gs_creations.count()
    print "ids_diff_users_minus_authors_gs_creations.count(): ", ids_diff_users_minus_authors_gs_creations.count()

    print "\n"
    print "="*50

    print "ids_diff_authors_minus_users: ", ids_diff_authors_minus_users

    print "\n\n"
    print "="*50

    print "ids_diff_users_minus_authors: ", ids_diff_users_minus_authors

    print "\n\n"
    print "="*50
    print "\n"

    print "ids_diff_authors_minus_users_gs_creations.count(): ", ids_diff_authors_minus_users_gs_creations.count(), "\n"

    for i in ids_diff_authors_minus_users_gs_creations:
        print "Name      : ", i.name
        print "member_of : ", i.member_of_names_list
        print "created_at: ", i.created_at
        print "created_by: ", i.created_by
        print "group_set : ", Node.get_names_list_from_obj_id_list(i.group_set, 'Group')
        print "\n-----------------------------------\n"

    print "\n"
    print "="*50
    print "\n"

    print "ids_diff_users_minus_authors_gs_creations.count(): ", ids_diff_users_minus_authors_gs_creations.count(), "\n"

    for i in ids_diff_users_minus_authors_gs_creations:
        print "Name      : ", i.name
        print "member_of : ", i.member_of_names_list
        print "created_at: ", i.created_at
        print "created_by: ", i.created_by
        print "group_set : ", Node.get_names_list_from_obj_id_list(i.group_set, 'Group')
        print "\n-----------------------------------\n"

    print "\n"
    print "="*50
    print "\n"

    all_creators = node_collection.find({'_type': {'$in': ['GSystem']}}).distinct('created_by')
    print "all_creators: ", all_creators
    all_creators_nodes = node_collection.find({'_type': {'$in': ['GSystem']} })
    print "all_creators_nodes.count(): ", all_creators_nodes.count()

    all_creators_nodes_userid_1 = node_collection.find({'_type': {'$in': ['GSystem']}, 'created_by': 1 })
    print "all_creators_nodes_userid_1.count(): ", all_creators_nodes_userid_1.count()

    # # django ORM based user query
    # User.objects.filter(id__in=all_creators)
    # all_creators_users = User.objects.filter(id__in=all_creators)
    # all_creators_users.count()
    # [u.username for u in all_creators_users]
    # for each_auth_obj in all_authors:


    #     u = User.objects.get(id=each_auth_obj.created_by)

    #     print "\n\ndjango User: "
    #     print "\tid: ", u.id
    #     print "\tname: ", u.username
    #     print "\temail: ", u.email

    #     print "\nmongo Author: "
    #     print "\tcreated_by: ", each_auth_obj.created_by
    #     print "\tname: ", each_auth_obj.name
    #     print "\temail: ", each_auth_obj.email

    #     print "Resources Created: ", node_collection.find({'_type': {'$ne': 'Author'}, '$or': [{'created_by': each_auth_obj.created_by}, {'modified_by': each_auth_obj.created_by}, {'contributos': each_auth_obj.created_by}] }).count()
    #     print "=============================================================="


if __name__ == '__main__':
    main()