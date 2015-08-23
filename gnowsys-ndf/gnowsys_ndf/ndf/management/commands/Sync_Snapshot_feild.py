from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.models import HistoryManager 

import subprocess
import string
from django.core.management.base import BaseCommand, CommandError
history_manager = HistoryManager()
#AttributeType,RelationType


def get_last_published_version(node):
	published_node_version = ""	
	rcs = RCS()
        fp = history_manager.get_file_path(node)
        cmd= 'rlog  %s' % \
	      (fp)
        rev_no =""
        proc1=subprocess.Popen(cmd,shell=True,
				stdout=subprocess.PIPE)
        for line in iter(proc1.stdout.readline,b''):
            if line.find('revision')!=-1 and line.find('selected') == -1:
                  rev_no=string.split(line,'revision')
                  rev_no=rev_no[1].strip( '\t\n\r')
                  rev_no=rev_no.strip(' ')
            if line.find('PUBLISHED')!=-1:
                   published_node_version = rev_no
		   break;	      
        return published_node_version

class Command(BaseCommand):
  help = "Based on "

  def handle(self, *args, **options):
	# all_nodes = node_collection.find({ "_type":{"$nin":["ToReduceDocs","IndexedWordList","node_holder", "AttributeType", "RelationType", "MetaType", "ProcessType", "GSystemType", "Group", "Author"]},"snapshot":{"$exists":False}})	
	all_nodes = node_collection.find({ "_type":{"$in":["GSystem","File"]},"snapshot":{"$exists":False}})	
	nodes = node_collection.find({ "_type":{"$in":["GSystem","File"]},"snapshot":{}})
	print "No.of Nodes not having Snapshot feilds: ", all_nodes.count()
	for i in all_nodes:
	     	
		node_collection.collection.update({'_id':ObjectId(i._id)}, {'$set':{'snapshot': {} }},upsert=False, multi=False)

	print "No. of Nodes not having values in snapshot feild: ", nodes.count()
        if nodes.count() > 0:
		for i in nodes:
			try:	
				print i.name
				get_node = node_collection.find_one({"_id":ObjectId(i._id)})
				if (not get_node['group_set']) == False :
						print "providing resource version to resource name: ", i.name
						for j in get_node['group_set']:
							id_type = node_collection.find_one({"_id":ObjectId(j)})
							if id_type and id_type._type == 'Group':
								rcsno = get_last_published_version(i)
								if not rcsno:
									rcsno = history_manager.get_current_version(i) 	
						
								node_collection.collection.update({"_id":ObjectId(i._id)},{'$set':{'snapshot'+"."+str(j):rcsno }},upsert=False,multi=False)
							elif id_type and id_type._type == 'Author':
								rcsno = history_manager.get_current_version(i)
								node_collection.collection.update({"_id":ObjectId(i._id)},{'$set':{'snapshot'+"."+str(j):rcsno }},upsert=False,multi=False)
											
				else:
					pass

			except:
				print "Nodes getting Error"
				print "==================="
				print "Node name",i.name
				print "==================="
				pass



	else:
		print "No Node to update. !!"

