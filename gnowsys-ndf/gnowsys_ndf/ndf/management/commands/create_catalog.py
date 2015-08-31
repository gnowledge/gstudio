import subprocess
from django.core.management.base import BaseCommand, CommandError
from gnowsys_ndf.factory_type import *
from gnowsys_ndf.ndf.models import *

class Command(BaseCommand):

	def handle(self,*args,**options):
		
		#print factory_attribute_types
		GSystemTypeList = [i['name'] for i in factory_gsystem_types]
		RelationTypeList = [ i.keys()[0] for i in  factory_relation_types ]
		AttributeTypeList = [ i.keys()[0] for i in  factory_attribute_types ]
		get_factory_data(factory_data) 
		get_gsystems(GSystemTypeList)
		get_relationtypes(RelationTypeList)
		get_attributetypes(AttributeTypeList)


def  get_gsystems(GSystemTypeList):
	var = '{"_type": "GSystemType","name":{"$in":%s}}' % GSystemTypeList
	var = var.replace("'",'"')
	cmd = "mongoexport --db studio-dev --collection Nodes -q '" + '%s'  % var + "' --out Schema/GSystemType.json"
	subprocess.Popen(cmd,stderr=subprocess.STDOUT,shell=True)

def get_relationtypes(RelationTypeList):
	var = '{"_type": "RelationType","name":{"$in":%s}}' % RelationTypeList
	var = var.replace("'",'"')
	cmd = "mongoexport --db studio-dev --collection Nodes -q '" + '%s'  % var + "' --out Schema/RelationType.json"
	subprocess.Popen(cmd,stderr=subprocess.STDOUT,shell=True)


def get_attributetypes(AttributeTypeList):
	var = '{"_type": "AttributeType","name":{"$in":%s}}' % AttributeTypeList
	var = var.replace("'",'"')	
	cmd = "mongoexport --db studio-dev --collection Nodes -q '" + '%s'  % var + "' --out Schema/AttributeType.json"
	subprocess.Popen(cmd,stderr=subprocess.STDOUT,shell=True)

def  get_factory_data(Factory_data):
	final_list = []
	for i in factory_data:
		var = str(i)
		var = var.replace("'",'"')
		node = node_collection.find(i)
		final_list.append(node[0]._id)
		# take the rcs of the data
		cmd = "mongoexport --db studio-dev --collection Nodes -q '" + '%s'  % var + "' --out Schema/" + str(i["name"]) + "." +"json" + ""
		subprocess.Popen(cmd,stderr=subprocess.STDOUT,shell=True)
	PROJECT_ROOT = os.path.abspath(os.path.dirname(os.pardir))
	rcs_path = os.path.join(PROJECT_ROOT)
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
					print path,rcs_path
					cp = "cp  -u " + path + " " +" --parents " + rcs_path + "/" 
					subprocess.Popen(cp,stderr=subprocess.STDOUT,shell=True)
			except:		
				pass
