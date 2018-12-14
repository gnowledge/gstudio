#The following python script converts mp4 to webm files whose mid attribute is None.
from gnowsys_ndf.ndf.models import *                                                                              
from gnowsys_ndf.settings import GSTUDIO_EPUBS_LOC_PATH                                                           
from bs4 import BeautifulSoup                                                                                     
import re                                                                                                         
import shutil                                                                                                     
from os import path                                                                                               
from gnowsys_ndf.ndf.views.tasks import convertVideo
ann_unit_gst_name, ann_unit_gst_id = GSystemType.get_gst_name_id(u"announced_unit")                                                          
announced_nodes=node_collection.find({'member_of':ann_unit_gst_id})                          
#announced units (total 28)
print("Total announced units:",announced_nodes.count())
#calculated file nodes                                                           
GST_FILE = node_collection.one({'_type':'GSystemType', 'name': "File"})
temp = False                                           
print("----------------------------------")                                                                       
for index,each in enumerate(announced_nodes,start=1):                                                             
	print("index:",index)                                                                                         
        print(each.name)
        #count of announced_unit files                                                                                               
	announcedunit_files=node_collection.find({'member_of':{'$in':[GST_FILE._id]},'group_set':{'$all':[each._id]}})
	file_count=announcedunit_files.count()                  
	print("file_count:",file_count)                         
	print("XXXXXXXXXXXX")                                   
	for indexx,au in enumerate(announcedunit_files,start=1):
		print("indexobject:",indexx)                                            
		iffile=au.if_file                                                             
		midd=iffile.mid                               
		filename=au.name
		file_id=au._id
		userid=au.created_by                       
		mimetype=iffile.mime_type                                      
		if mimetype=="video/mp4":                     
			print("mp4 filename:",filename)               
			print("iffile attr",iffile)               
			print("-------------")                    
			print("mid attr:",midd)                   
			if midd.id == None:
				print("previous_mid_attr:",midd)                       
				convertVideo(userid,file_id,filename)
				print("webm file created")
				print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
				print("modified_mid_attr",midd)
				#temp = True
				break;
                #au.save()
			else:                    
				print(midd.id)                        
	print("00000000000")*5 
	#if temp:
	#	break;
