from django.contrib.auth.admin import User
from gnowsys_ndf.ndf.models import node_collection
from gnowsys_ndf.settings import GSTUDIO_INSTITUTE_ID

author_user_map = {
    "fields":{
        "_id": "id",
        "password": "password",
        "name": "username",
        "email": "email",
        "created_at": "date_joined",
        },
    "attributes":{
        "first_name": "first_name",
        "last_name": "last_name"
    }
}

username_existing_expected_map = {
    "piegon": "pigeon",
    "garpes": "grapes",
    "beatle": "beetle"
}


def update_username(username_existing_expected_map={}):

    user_tokens_map_seperator = "-"

    for existing, expected in username_existing_expected_map.iteritems():

        check_in_username = user_tokens_map_seperator + existing + user_tokens_map_seperator + GSTUDIO_INSTITUTE_ID
        auth_cur = node_collection.find({'_type': u'Author', 'name': {'$regex': unicode(check_in_username), '$options': 'i'} })
        print "\nUpdating Author instances for: '%s' \n" % existing
        for each_auth in auth_cur:
            print "\nOLD: ", each_auth.name
            each_auth.name = each_auth.name.replace(existing, expected)
            each_auth.save()
            print "NEW: ", each_auth.name

        print "-------------------------------------------"
        print "\nUpdating User instances for: '%s' \n" % existing
        user_cur = User.objects.filter(username__endswith=unicode(check_in_username))
        for each_user in user_cur:
            print "\nOLD: ", each_user.username
            each_user.username = each_user.username.replace(existing, expected)
            print "NEW: ", each_user.username
            each_user.save()

        print "\n=========================================== \n"


# calling method
update_username(username_existing_expected_map)
