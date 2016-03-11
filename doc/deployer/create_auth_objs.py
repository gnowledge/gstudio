from gnowsys_ndf.ndf.models import *
from django.contrib.auth.models import User
all_users = User.objects.all()
auth_gst = node_collection.one({'_type': u'GSystemType', 'name': u'Author'})
new_auth_instances = 0
for each_user in all_users:
	try:
		auth = node_collection.find_one({'_type': u"Author", 'created_by': int(each_user.id)})
	except:
		pass
	# This will create user document in Author collection to behave user as a group.
	if auth is None and each_user.is_active:
		print "\n Creating new Author obj for ",each_user.username
		auth = node_collection.collection.Author()
		auth.name = unicode(each_user.username)
		auth.email = unicode(each_user.email)
		auth.password = u""
		auth.member_of.append(auth_gst._id)
		auth.group_type = u"PUBLIC"
		auth.edit_policy = u"NON_EDITABLE"
		auth.subscription_policy = u"OPEN"
		auth.created_by = each_user.id
		auth.modified_by = each_user.id
		auth.contributors.append(each_user.id)
		auth.group_admin.append(each_user.id)
		auth.preferred_languages = {'primary': ('en', 'English')}

		auth.agency_type = "Student"
		auth_id = ObjectId()
		auth['_id'] = auth_id
		auth.save(groupid=auth._id) 
		home_group_obj = node_collection.one({'_type': u"Group", 'name': unicode("home")})
		if each_user.id not in home_group_obj.author_set:
			node_collection.collection.update({'_id': home_group_obj._id}, {'$push': {'author_set': each_user.id }}, upsert=False, multi=False)
			home_group_obj.reload()
		desk_group_obj = node_collection.one({'_type': u"Group", 'name': unicode("desk")})
		if desk_group_obj and each_user.id not in desk_group_obj.author_set:
			node_collection.collection.update({'_id': desk_group_obj._id}, {'$push': {'author_set': each_user.id }}, upsert=False, multi=False)
			desk_group_obj.reload()
		new_auth_instances = new_auth_instances + 1

print "\n Total Author objects created: ", new_auth_instances

