from datetime import datetime
from gnowsys_ndf.ndf.models import *
from django.contrib.auth.models import User
from django.core.management import execute_from_command_line

usernames_list = Author.get_author_usernames_list_from_user_id_list((counter_collection.find().distinct("user_id")))
for each in usernames_list:
	execute_from_command_line(["manage.py", "activity_timestamp",each])
