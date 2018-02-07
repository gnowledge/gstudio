import json

from django.contrib.auth.admin import User
from gnowsys_ndf.ndf.models import Node, Author, node_collection
from gnowsys_ndf.settings import GSTUDIO_INSTITUTE_ID
try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

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
	# try:
	# 	with open('../doc/release-scripts/user-tokens.json') as tokens:
	# 		user_tokens_map = json.load(tokens)
	# 		user_tokens_map_seperator = user_tokens_map['seperator']
	# except Exception as e:
	# 	print e

	for existing, expected in username_existing_expected_map.iteritems():

		check_in_username = user_tokens_map_seperator + existing + user_tokens_map_seperator + GSTUDIO_INSTITUTE_ID
		auth_cur = node_collection.find({'_type': u'Author', 'name': {'$regex': unicode(check_in_username), '$options': 'i'} })
		print "\nUpdating Author instances for: '%s' \n"%existing
		for each_auth in auth_cur:
			print "\nOLD: ", each_auth.name
			each_auth.name = each_auth.name.replace(existing, expected)
			each_auth.save()
			print "NEW: ", each_auth.name

		print "-------------------------------------------"
		print "\nUpdating User instances for: '%s' \n"%existing
		user_cur = User.objects.filter(username__endswith=unicode(check_in_username))
		for each_user in user_cur:
			print "\nOLD: ", each_user.username
			each_user.username = each_user.username.replace(existing, expected)
			print "NEW: ", each_user.username
			each_user.save()

		print "\n=========================================== \n"

if __name__ == '__main__':
	update_username(username_existing_expected_map)
