import subprocess
#from gnowsys-ndf.gnowsys_ndf.ndf.models import *
import os
import csv
from django.core.management.base import BaseCommand, CommandError
#before moving to restore all the users check if users exist on that system
'''
file_path = '/home/mukesh/virtualenviroment/gstudio/gnowsys-ndf/gnowsys_ndf/Author.csv'

with open(file_path, 'rb') as csv_file:
	csv_file_content = csv.DictReader(csv_file, delimiter=",")
	json_file_content = []	
	for row in csv_file_content:
		json_file_content.append(row)

for i in json_file_content:
	author_node = node_collection.find_one({"_type":"Author","name":i['name']})
	if author_node:
		pass
	else:
		print "Author named" + i['name'] + "does not exist in this database" + "Replication Not possible.  !!!"
		print "Sorry  :-("
		break
'''
class Command(BaseCommand):

    
        def handle(self, *args, **options):

		print "Enter database name to restore data"
		db = raw_input()
		#settings_dir = os.path.dirname(__file__)
		path = os.path.abspath(os.path.dirname(os.pardir))
		backup_path = os.path.join(path,'backup/')
		path_val = os.path.exists(backup_path)
		if path_val == True:
	
			cmd = 'mongoimport --db '+ db +' --collection Nodes --file '+ backup_path + '/Groupandallcontent.json --upsert'
			subprocess.Popen(cmd,stderr=subprocess.STDOUT,shell=True)
	
			cmd = 'mongoimport --db '+ db +' --collection fs.chunks --file '+ backup_path + '/chunks.json --upsert' 
			subprocess.Popen(cmd,stderr=subprocess.STDOUT,shell=True)
	
			cmd = 'mongoimport --db '+ db +' --collection fs.files --file '+ backup_path + '/files.json --upsert'
			subprocess.Popen(cmd,stderr=subprocess.STDOUT,shell=True)
	
			cmd = 'mongoimport --db '+ db +' --collection Triples --file '+ backup_path + '/at_triples.json --upsert'
			subprocess.Popen(cmd,stderr=subprocess.STDOUT,shell=True)
	
			cmd = 'mongoimport --db '+ db +' --collection Triples --file '+ backup_path + '/rt_triples.json --upsert'
			subprocess.Popen(cmd,stderr=subprocess.STDOUT,shell=True)

			cmd = 'mongoimport --db '+ db +' --collection Nodes --file '+ backup_path + '/at_files.json --upsert'
			subprocess.Popen(cmd,stderr=subprocess.STDOUT,shell=True)

			cmd = 'mongoimport --db '+ db +' --collection Nodes --file '+ backup_path + '/rt_files.json --upsert'
			subprocess.Popen(cmd,stderr=subprocess.STDOUT,shell=True)
	
			cmd = 'mongoimport --db '+ db +' --collection Nodes --file '+ backup_path + '/collection_dump.json --upsert'
			subprocess.Popen(cmd,stderr=subprocess.STDOUT,shell=True)

		else:
			print "backup folder doesnt exists."	
				

