"""

This script is used to migrate django users from one server to another.
Before running this script, we must take dump of users from source server

Step 1 : Take backup of 'example-sqlite3' on destination server

Step 2 : Execute foll. script on source server, to take dump of user objects
			from django.contrib.auth.models import User
			import pickle
			u = User.objects.all()
			output = open("/tmp/users_dump.pkl","wb")
			pickle.dump(u,output)
			output.close()

Step 3 : Move this file 'users_dump.pkl' to destination server and place it at manage.py level

"""

from django.core.management.base import BaseCommand, CommandError
import pickle
import datetime
from django.contrib.auth.models import User
from gnowsys_ndf.ndf.models import *
auth_obj = node_collection.one({'_type': u'GSystemType', 'name': u'Author'})
success_log_csv = open("success_log.csv", "a")
fail_log_csv = open("fail_log.csv", "a")
success_log_txt = open("success_log.txt", "a")
fail_log_txt = open("fail_log.txt", "a")

global success_log_var
global success_log_txt_var
global fail_log_txt_var
global fail_log_var
global new_users_created
global failed_users
global total_active_users
# reg_active_users
# reg_inactive_users
global already_existing_users
global success_log_var
global fail_log_var
global success_log_txt_var
global fail_log_txt_var
global usernames
global useremails
global userids

class Command(BaseCommand):

    help = "\n\tMigrating users\n"
    def handle(self, *args, **options):
		global success_log_var
		global success_log_txt_var
		global fail_log_txt_var
		global fail_log_var
		global new_users_created
		global failed_users
		global total_active_users
		# reg_active_users
		# reg_inactive_users
		global already_existing_users
		global success_log_var
		global fail_log_var
		global success_log_txt_var
		global fail_log_txt_var
		global usernames
		global useremails
		global userids

		auth_node = None
		success_log_var = ""
		success_log_txt_var = ""
		fail_log_txt_var = ""
		fail_log_var = ""
		new_users_created = 0
		failed_users = 0
		total_active_users = 0
		# reg_active_users = 0
		# reg_inactive_users = 0
		already_existing_users = 0
		csv_lbl = "\n\n\n\nEmail,ID,Username,First Name,Last Name,Active,Remark"
		success_log_var = csv_lbl
		fail_log_var = csv_lbl
		success_log_txt_var = "\n"
		fail_log_txt_var = "\n"
		usernames = []
		useremails = []
		userids = []

		for each in User.objects.all():
			usernames.append(each.username)
			userids.append(each.id)
			useremails.append(each.email)

		print "\n Existing Users: ", len(usernames)
		# 'cube_users_sep_1.pkl' is pickle dump file
		#  of user objects from source, in this case: cube.metastudio.org
		fp = open("allusers.pkl","rb")
		line = pickle.loads(fp.read())
		print "\n New Users: ", len(line)
		d = datetime.datetime.now()
		# logging.info('Script executed at : %s ', str(d))
		info_msg = "\nScript Executed at : " + str(d) + '\nNo. of Existing users found : '+ str(len(usernames)) + '\nNo. of New users to be processed: ' + str(len(line))
		# success_log_var += csv_lbl
		# fail_log_var += csv_lbl

		home_group_obj = node_collection.one({'_type': u"Group", 'name': unicode("home")})

		def create_user(user_obj):
			global useremails
			global usernames
			global userids
			new_user = User()
			new_user.__dict__ = user_obj.__dict__
			new_user.is_superuser = False
			new_user.is_staff = False
			userids.append(new_user.id)
			useremails.append(new_user.email)
			usernames.append(new_user.username)
			# logging.info('id Updated : new_id- %s ',str(new_user.id))
			new_user.save()
			return new_user
			# print "\n\n creating new Author group"



		def create_author_node(user_obj):
			auth = node_collection.collection.Author()
			auth.name = unicode(user_obj.username)
			# print auth.name
			auth.email = unicode(user_obj.email)
			auth.password = u""
			auth.member_of.append(auth_obj._id)
			auth.group_type = u"PUBLIC"
			auth.edit_policy = u"NON_EDITABLE"
			auth.subscription_policy = u"OPEN"
			auth.created_by = user_obj.id
			auth.modified_by = user_obj.id
			auth.contributors.append(user_obj.id)
			# auth_id = ObjectId()
			# print "\n\n ObjectId-- ", auth_id
			# auth._id = auth_id
			# auth.save(groupid=auth._id)
			auth.save()
			return auth


		# print "\nBefore user migration home group author_set -- ",home_group_obj.author_set
		# logging.info('Before user migration home group author_set - %s ',str(home_group_obj.author_set))
		for index,each in enumerate(line):
			try:
				# print ".",
				# logging.info('Processing user : User name- %s , id- %s , email - %s',str(each.username),str(each.id),str(each.email))

				# b = each
				# a = User()
				# if not each.username in usernames and each.username != "glab" and each.email not in useremails:
				if each.email and each.username:
					if each.username not in usernames:
						if each.email not in useremails:
							if each.is_active:
								print "\n Processing user_obj ",index + 1, " of ", len(line)
								total_active_users = total_active_users + 1
								old_id = each.id
								if len(userids) == 0:
									each.id = 1
								else:
									each.id = max(userids) + 1
								auth_node = node_collection.one({'_type': "Author",'created_by': int(each.id)})
								if auth_node is None:
									print "New auth_node"
									new_user = create_user(each)
									auth = create_author_node(new_user)
									log_msg = "ID updated (" + str(old_id) + " to "+ str(new_user.id) + ")"
									log_msg += " Successfully created User object and Author group : " + str(auth._id)
									print "\n\n log_msg",log_msg
									# print "\n\n new author grp creation completed--", auth._id
									# adding user's id into author_set of "home" group.
									if new_user.id not in home_group_obj.author_set:
										node_collection.collection.update({'_id': home_group_obj._id}, {'$push': {'author_set': new_user.id }}, upsert=False, multi=False)
										home_group_obj.reload()
									new_users_created =  new_users_created + 1

									success_log_var += '\n"'+str(new_user.email) +'",'+str(new_user.id)+',"'+str(new_user.username)+'","'+str(new_user.first_name)+'","'+str(new_user.last_name)+'",'+str(new_user.is_active)+','+log_msg
									success_log_txt_var += "\n\nEmail - " + str(new_user.email) + "\n\t ID : "+ str(new_user.id)+ "\n\t Username : "+ str(new_user.username) + \
									"\n\t First Name : "+ str(new_user.first_name)+"\n\t Last Name : "+str(new_user.last_name) + \
									"\n\t Active : " + str(new_user.is_active) + "\n\t Remark : " + log_msg
									# logging.info('New author group created : name- %s and _id- %s ',str(auth.name),str(auth._id))

								else:
									print "Author exists for -- ", new_user.id, "------", auth_node._id, "--", auth_node.name
									failed_users = failed_users + 1
									fail_log_var += '\n"'+str(each.email) +'",'+str(each.id)+',"'+str(each.username)+'","'+str(each.first_name)+'","'+str(each.last_name)+'",'+str(each.is_active)+',Author group exists'
									fail_log_txt_var += "\n\nEmail - " + str(each.email) + "\n\t ID : "+ str(each.id)+ "\n\t Username : "+ str(each.username) + \
									"\n\t First Name : "+ str(each.first_name)+"\n\t Last Name : "+str(each.last_name) + \
									"\n\t Active : " + str(each.is_active) + "\n\t Remark : Author group exists"
									# logging.info('Author group exists : User name- %s and id- %s ',str(auth.name),str(auth_node.id))
							else:
								# reg_inactive_users = reg_inactive_users + 1
								print "\n Inactive User"
								failed_users = failed_users + 1
								fail_log_var += '\n"'+str(each.email) +'",'+str(each.id)+',"'+str(each.username)+'","'+str(each.first_name)+'","'+str(each.last_name)+'",'+str(each.is_active)+',Inactive User'
								fail_log_txt_var += "\n\nEmail - " + str(each.email) + "\n\t ID : "+ str(each.id)+ "\n\t Username : "+ str(each.username) + \
								"\n\t First Name : "+ str(each.first_name)+"\n\t Last Name : "+str(each.last_name) + \
								"\n\t Active : " + str(each.is_active) + "\n\t Remark : Inactive User"
								# logging.info('New user created : User name- %s and id- %s ',str(a.username),str(a.id))
						else:
							print " Email already exists"
							failed_users = failed_users + 1
							already_existing_users = already_existing_users + 1
							fail_log_var +=  '\n"'+str(each.email) +'",'+str(each.id)+',"'+str(each.username)+'","'+str(each.first_name)+'","'+str(each.last_name)+'",'+str(each.is_active)+',Email already exists'
							fail_log_txt_var += "\n\nEmail - " + str(each.email) + "\n\t ID : "+ str(each.id)+ "\n\t Username : "+ str(each.username) + \
							"\n\t First Name : "+ str(each.first_name)+"\n\t Last Name : "+str(each.last_name) + \
							"\n\t Active : " + str(each.is_active) + "\n\t Remark : Email already exists"
							# logging.info('Email Already exists. Email- %s, username- %s, id- %s',str(each.email),str(each.username),str(each.id))
					else:
						print "\n Username already exists"
						failed_users = failed_users + 1
						already_existing_users = already_existing_users + 1
						fail_log_var += '\n"'+str(each.email) +'",'+str(each.id)+',"'+str(each.username)+'","'+str(each.first_name)+'","'+str(each.last_name)+'",'+str(each.is_active)+',Username already exists'
						fail_log_txt_var += "\n\nEmail - " + str(each.email) + "\n\t ID : "+ str(each.id)+ "\n\t Username : "+ str(each.username) + \
						"\n\t First Name : "+ str(each.first_name)+"\n\t Last Name : "+str(each.last_name) + \
						"\n\t Active : " + str(each.is_active) + "\n\t Remark : Username already exists"
						# logging.info('Username exists. Email- %s, username- %s, id- %s',str(each.email),str(each.username),str(each.id))
				else:
					print "Email/Username not found"
					failed_users = failed_users + 1
					fail_log_var += '\n"'+str(each.email) +'",'+str(each.id)+',"'+str(each.username)+'","'+str(each.first_name)+'","'+str(each.last_name)+'",'+str(each.is_active)+',Email/Username not found'
					fail_log_txt_var += "\n\nEmail - " + str(each.email) + "\n\t ID : "+ str(each.id)+ "\n\t Username : "+ str(each.username) + \
					"\n\t First Name : "+ str(each.first_name)+"\n\t Last Name : "+str(each.last_name) + \
					"\n\t Active : " + str(each.is_active) + "\n\t Remark : Email/Username not found"
					# logging.info('User object Error. Email or username is empty. Email- %s, username- %s',str(each.email),str(each.username))
			except Exception as e:
				print "Exception--",e
				failed_users = failed_users + 1
				fail_log_var += '\n"'+str(each.email) +'",'+str(each.id)+',"'+str(each.username)+'","'+str(each.first_name)+'","'+str(each.last_name)+'",'+str(each.is_active)+',Error: "'+str(e) + '"'
				fail_log_txt_var += "\n\nEmail - " + str(each.email) + "\n\t ID : "+ str(each.id)+ "\n\t Username : "+ str(each.username) + \
				 "\n\t First Name : "+ str(each.first_name)+"\n\t Last Name : "+str(each.last_name) + \
				 "\n\t Active : " + str(each.is_active) + "\n\t Remark : Error: "+str(e)
				# logging.info('Error - %s %s %s . %s ',str(each.email), str(each.username), str(each.id),str(e))
				pass
		# logging.info('After user migration home group author_set - %s ',str(home_group_obj.author_set))
		# print "FINAL home_group_obj.author_set--",home_group_obj.author_set
		fp.close()
		total_users_msg = "\nSuccessfully created "+str(new_users_created)+" New Users "
		# success_report_msg = "\nActive/Inactive Users : \n\tTotal active users processed : "+ str(total_active_users) + \
		# "\n\t\tActive Users Registered :\t" + str(reg_active_users)+ \
		# "\n\t\tInactive Users Registered : \t" + str(reg_inactive_users)
		
		failed_report_msg = "\nFailed to create " + str(len(line)-new_users_created)
		duplicate_msg = "\nDuplicate entries found : " + str(already_existing_users)
		
		success_log_csv.write(info_msg)
		success_log_csv.write(total_users_msg)
		# success_log_csv.write(success_report_msg)
		success_log_csv.write(duplicate_msg)
		success_log_csv.write(success_log_var)

		fail_log_csv.write(info_msg)
		fail_log_csv.write(failed_report_msg)
		fail_log_csv.write(duplicate_msg)
		fail_log_csv.write(fail_log_var)

		success_log_txt.write(info_msg)
		success_log_txt.write(total_users_msg)
		# success_log_txt.write(success_report_msg)
		success_log_txt.write(duplicate_msg)
		success_log_txt.write(success_log_txt_var)

		fail_log_txt.write(info_msg)
		fail_log_txt.write(failed_report_msg)
		fail_log_txt.write(duplicate_msg)
		fail_log_txt.write(fail_log_txt_var)


