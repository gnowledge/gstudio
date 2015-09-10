import subprocess
from gnowsys_ndf.ndf.models import *
from django.core.management.base import BaseCommand, CommandError
import os

nodelist=[]
user_list = []
group_set = []
member_of = []
prior_node_list = []
post_node_list = []
fs_file_ids = []
Gattribute_ids = []
Grelations_ids = []
collection_set_ids = []
Gattribute_value = []
Grelations_value = []
class Command(BaseCommand):

    
        def handle(self, *args, **options):
		print "Enter Group Name whose data backup is to be taken"
                Group_name = raw_input()
                #db = get_database()
                #files = db['fs.files']
                #chunks = db['fs.chunks']
                #follow the recursive stretagy go till the depth of the snode take their induvidual dumps and then finally of the main groups
                Group_node = node_collection.find_one({"_type":"Group","name":unicode(Group_name)}) 
		if Group_node:
				#all the nodes having Group id
				print "Enter name of the database"
				db_name=raw_input() 
				nodes = node_collection.find({"group_set":ObjectId(Group_node._id)})
				
				user_list.extend(Group_node.author_set)
				user_list.extend(Group_node.group_admin)

				for i in nodes:
					nodelist.append(i._id)	
					if i._type == 'Page':
						get_page_node_details(i)
					if i._type == 'File':
						get_file_node_details(i)
					if i.collection_set:
						get_collection_node_ids(i)
					if i.prior_node:
						get_prior_node(i)
					if i.post_node:
						get_post_node(i)
					if i.attribute_set:
						#fetch attribute_type
						for j in i.attribute_set:
							at_type = node_collection.find_one({"_type":"AttributeType","name":unicode(j.keys()[0])})
							attr = triple_collection.find_one({"_type": "GAttribute", "subject": i._id, "attribute_type.$id": at_type._id})
							if attr:            		
								Gattribute_ids.append(attr._id)
								if type(attr.object_value) not in  [datetime.datetime,unicode,int] :
									try:
										Gattribute_value.extend(attr.object_value)
									except:
										Gattribute_value.append(attr.object_value)

					if i.relation_set:
						for j in i.relation_set:				
							if unicode(j.keys()[0]):				
								rel_node = node_collection.find_one({"$or":
												      [ {"name":unicode(j.keys()[0])},	{"inverse_name":unicode(j.keys()[0])}],"_type":"RelationType"})
				
								value_node = triple_collection.find_one({"_type": "GRelation", "subject": i._id, "relation_type.$id": rel_node._id})
								if value_node:	 
									Grelations_ids.append(value_node._id) 
									if type(attr.object_value) not in  [datetime.datetime,unicode,int] :
										try:
											Grelations_value.extend(value_node.right_subject)
										except:
											Grelations_value.append(value_node.right_subject)		
				query_list = []
				commandlist=[]
				query ={}
				

				all_node='{"group_set":ObjectId("%s")}' % ObjectId(Group_node._id)
				f_list = [ObjectId(i) for i in fs_file_ids ]
				at_files = '{"_id":{"$in":%s}}' % Gattribute_value
				at_files = at_files.replace("'",'"')
				cmd = "mongoexport --db "+ db_name + " --	collection Nodes -q '" + '%s'  % at_files + "' --out backup/at_files.json"
				commandlist.append(cmd)
				

				rt_files = '{"_id":{"$in":%s}}' % Grelations_value
				rt_files = rt_files.replace("'",'"')
				cmd = "mongoexport --db "+ db_name +" --collection Nodes -q '" + '%s'  % rt_files + "' --out backup/rt_files.json"
				commandlist.append(cmd)

				#things to be taken from triples
				at_triples = '{"_id":{"$in":%s}}' % Gattribute_ids
				at_triples = at_triples.replace("'",'"')

				cmd = "mongoexport --db "+ db_name +" --collection Triples -q '" + '%s'  % at_triples + "' --out backup/at_triples.json"
				commandlist.append(cmd)

				rt_triples = '{"_id":{"$in":%s}}' % Grelations_ids
				rt_triples = rt_triples.replace("'",'"')

				cmd = "mongoexport --db "+ db_name +" --collection Triples -q '" + '%s'  % rt_triples + "' --out backup/rt_triples.json"
				commandlist.append(cmd)

				ab = '{"_id":{"$in":%s}}' % fs_file_ids
				a = ab.replace("'",'"')


				cmd = "mongoexport --db "+ db_name + " --collection fs.files -q '" + '%s'  % a + "' --out backup/files.json"
				commandlist.append(cmd)

				ab = '{"files_id":{"$in":%s}}' % fs_file_ids
				a = ab.replace("'",'"')
				cmd = "mongoexport --db " + db_name + " --collection fs.chunks -q '" + '%s'  % a + "' --out backup/chunks.json"
				commandlist.append(cmd)

				ab = '{"_type":"Author","created_by":{"$in":%s}}' % user_list 
				cmd  = "mongoexport --db "+ db_name +" --collection Nodes --type=csv --fields name -q '" + '%s'  % ab + "' --out backup/Author.csv"
				commandlist.append(cmd)

				ab = '{"_type":"Author","created_by":{"$in":%s}}' % user_list 
				cmd  = "mongoexport --db "+ db_name +" --collection Nodes -q '" + '%s'  % ab + "' --out backup/Author.json"
				commandlist.append(cmd)

				
				collection_dump = '{"_id":{"$in":%s}}' % collection_set_ids
				collection_dump = collection_dump.replace("'",'"')
				cmd = "mongoexport --db " + db_name + " --collection Nodes -q '" + '%s'  % collection_dump + "' --out backup/collection_dump.json"
				commandlist.append(cmd)

				ac   = '{"$or":[{"name":"' + unicode(Group_name) +'"}' + ',' + ab + ',' + all_node + ']}'
				cmd  = "mongoexport --db " + db_name + " --collection Nodes -q '" + '%s'  % ac + "' --out backup/Groupandallcontent.json"	
				commandlist.append(cmd)

				for i in commandlist:
					subprocess.Popen(i,stderr=subprocess.STDOUT,shell=True)
	


				#the final list
				# take rcs of every thing
				final_list = []
				final_list.extend(Gattribute_value)
				final_list.extend(Grelations_value)
				final_list.extend(collection_set_ids)
				final_list.extend(fs_file_ids)
				final_list.extend(Grelations_ids)
				final_list.extend(nodelist)
				final_list.extend(Gattribute_ids)
				#check if rcs dir exists if not create it
				PROJECT_ROOT = os.path.abspath(os.path.dirname(os.pardir))
				rcs_path = os.path.join(PROJECT_ROOT, 'gnowsys_ndf/ndf/rcs/')
				path_val = os.path.exists(rcs_path)
				if path_val == False:
					os.makedirs(rcs_path)
				for i in final_list:	
					#get rcs files path and copy them to the current dir:
					hr = HistoryManager()
					if type(i)!= int:
						try:
							a = node_collection.find_one({"_id":ObjectId(i)})
							if a:
								path = hr.get_file_path(a)
								path = path + ",v"
								cp = "cp  -u " + path + " " +" --parents " + rcs_path + "/" 
								subprocess.Popen(cp,stderr=subprocess.STDOUT,shell=True)
						except:		
							pass
		else:
			print "No Group of this Name Exist !!!"	

def get_file_node_details(node):
	for i in node:
		if 'fs_file_ids' == i:
			fs_file_ids.extend(node['fs_file_ids'])
		if 'group_set' == i:
			for j in node.group_set:
				group_node = node_collection.find_one({"_id":ObjectId(j)})
				if group_node:
					if group_node._type != unicode('Author'):
						group_set.extend(group_node.group_set)
		if 'author_set' == i:
		        user_list.extend(node.author_set)			
	return node

def get_page_node_details(node):
	for i in node:
		if 'group_set' == i:
			for j in node.group_set:
				group_node = node_collection.find_one({"_id":ObjectId(j)})
				if group_node:
					if group_node._type != unicode('Author'):
						group_set.extend(group_node.group_set)
		if 'author_set' == i:
		        user_list.extend(node.author_set)			
	return node

def get_collection_node_ids(node):	
	for i in node.collection_set:
		collection_set_ids.append(i)
		new_node = node_collection.find_one({"_id":ObjectId(i)})
		if new_node:
		        if new_node.collection_set:
			        get_collection_node_ids(new_node)

def get_prior_node(node):
	for i in node.prior_node:
		prior_node_list.append(i)
		new_node = node_collection.find_one({"_id":ObjectId(i)})
		if new_node:
			if new_node.prior_node:
				get_prior_node(new_node)
def get_post_node(node):	
	for i in node.post_node:
		post_node_list.append(i)
		new_node = node_collection.find_one({"_id":ObjectId(i)})
		if new_node:
			if new_node.post_node:
				get_post_node(new_node)
	

