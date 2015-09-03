import subprocess
from django.core.management.base import BaseCommand, CommandError
from gnowsys_ndf.factory_type import *
from gnowsys_ndf.ndf.models import *
from bson.json_util import dumps,loads
from bson import json_util
from gnowsys_ndf.ndf.models import NodeJSONEncoder
from gnowsys_ndf.ndf.rcslib import RCS
import json
rcs = RCS()
hr = HistoryManager()
		
class Command(BaseCommand):

	def handle(self,*args,**options):
		
		#print factory_attribute_types
		final_list = []
		
		GSystemTypeList = [i['name'] for i in factory_gsystem_types]
		RelationTypeList = [ i.keys()[0] for i in  factory_relation_types ]
		AttributeTypeList = [ i.keys()[0] for i in  factory_attribute_types ]
		metatypes = get_metatypes()	
		GSystemTypeList = get_gsystems(GSystemTypeList)
		RelationTypeList = get_relationtypes(RelationTypeList)
		AttributeTypeList = get_attributetypes(AttributeTypeList)
		datalist = get_factory_data(factory_data)
		final_list  = datalist + AttributeTypeList +  RelationTypeList  + GSystemTypeList + metatypes
		#send it for making the rcs of all the nodes
		make_rcs_dir(final_list)
		'''
		make_catalog()		 
		'''
def  get_metatypes():
	node = node_collection.find({"_type":"MetaType"})
	print node.count()
	metatypeslist = [i._id for i in node]
	print "the metatype",metatypeslist
	return metatypeslist		

def  get_gsystems(GSystemTypeList):
	var = {"_type": "GSystemType","name":{"$in":GSystemTypeList}}  
	Systemtypes = node_collection.find(var,{"_id":1})
	Systemtypelist = [i._id for i in Systemtypes]
	'''
	cmd = "mongoexport --db studio-dev --collection Nodes -q '" + '%s'  % var + "' --out Schema/GSystemType.json"
	subprocess.Popen(cmd,stderr=subprocess.STDOUT,shell=True)
	'''
	return Systemtypelist	
def get_relationtypes(RelationTypeList):
	var = {"_type": "RelationType","name":{"$in":RelationTypeList}} 
	'''var = var.replace("'",'"')'''
	'''
	cmd = "mongoexport --db studio-dev --collection Nodes -q '" + '%s'  % var + "' --out Schema/RelationType.json"
	subprocess.Popen(cmd,stderr=subprocess.STDOUT,shell=True)
	'''
	relationtype = node_collection.find(var,{"_id":1})
	relationtypelist = [i._id for i in relationtype ]
	return relationtypelist
def get_attributetypes(AttributeTypeList):
	var = {"_type": "AttributeType","name":{"$in":AttributeTypeList}} 
	'''
	var = var.replace("'",'"')	
	cmd = "mongoexport --db studio-dev --collection Nodes -q '" + '%s'  % var + "' --out Schema/AttributeType.json"
	subprocess.Popen(cmd,stderr=subprocess.STDOUT,shell=True)
	'''
	attributetype = node_collection.find(var,{"_id":1})
	attributetypelist = [i._id for i in attributetype]
	return attributetypelist
def  get_factory_data(Factory_data):
	data_list = []
	for i in factory_data:
		var = str(i)
		var = var.replace("'",'"')
		node = node_collection.find(i)
		data_list.append(node[0]._id)
	'''
		cmd = "mongoexport --db studio-dev --collection Nodes -q '" + '%s'  % var + "' --out Schema/" + str(i["name"]) + "." +"json" + ""
		subprocess.Popen(cmd,stderr=subprocess.STDOUT,shell=True)
	'''
	return data_list
		# take the rcs of the data
		
def make_rcs_dir(final_list):
	PROJECT_ROOT = os.path.abspath(os.path.dirname(os.pardir))
	rcs_path = os.path.join(PROJECT_ROOT)
	path_val = os.path.exists(rcs_path)
	GSystemtypenodes = []
	Relationtypenodes = []
	Attributetypenodes = []
	factorydatanode = []
	metatype = []
	if path_val == False:
		os.makedirs(rcs_path)
	for i in final_list:	
		#get rcs files path and copy them to the current dir:
		if type(i)!= int:
			
				a = node_collection.find_one({"_id":ObjectId(i)})
				if a:
					rel_path = hr.get_file_path(a)
					path = rel_path + ",v"
					#cp = "cp  -u " + path + " " +" --parents " + rcs_path + "/" 
					#subprocess.Popen(cp,stderr=subprocess.STDOUT,shell=True)
				if a:
					filter_list = ['GSystemType','RelationType','AttributeType','MetaType']
					if a._type  in filter_list:
						file_node = get_version_document(a,rel_path)
						if a._type == 'GSystemType':
							GSystemtypenodes.append(file_node)
						elif a._type == 'RelationType':
							Relationtypenodes.append(file_node)
						elif a._type == 'AttributeType':
							Attributetypenodes.append(file_node)
						elif a._type == 'MetaType': 
							print "asdf",a 
							metatype.append(file_node)
					elif a._type not in filter_list:
						file_node = get_version_document(a,rel_path,'1.1')
						factorydatanode.append(file_node)					
			
	#start making catalog 	
	make_catalog(GSystemtypenodes,'GSystemType')
	make_catalog(Relationtypenodes,'RelationType')
	make_catalog(Attributetypenodes,'AttributeType')	
	make_catalog(factorydatanode,'factorydata')
	print metatype
	make_catalog(metatype,'metatype')	
	
def make_catalog(file_node,data_type):
	''' make folder called catalog '''
	PROJECT_ROOT = os.path.abspath(os.path.dirname(os.pardir))
	refcatpath = os.path.join(PROJECT_ROOT + '/GRef.cat.')
	path_val = os.path.exists(refcatpath)
	if path_val == False:		
		os.makedirs(refcatpath)
	with open('GRef.cat./' + data_type+ ".json", 'w') as outfile:
		json.dump(file_node, outfile,ensure_ascii=True,indent=4,
                                          sort_keys=False)
	file_node = []
def get_version_document(document,rel_path,version=""):
	if version == "":
		versionno = hr.get_current_version(document)
	rcs.checkout((rel_path,version))
	with open(rel_path, 'r') as version_file:
		json_data = version_file.read()
	rcs.checkin(rel_path)
	return json.loads(json_data)
