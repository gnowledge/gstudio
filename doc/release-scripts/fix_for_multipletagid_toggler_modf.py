
'''Issue: In a particular activity page, there are multiple transcripts and on click of the later has effect on the former but not on the corresponding
   Reson: Both the transcripts are having the same ID 
  Unit : English Beginner Lesson Name : Places Around Us Acitity page :Warm Up

 Fix : Have modified the first encountered ID as Toggler09

'''

from gnowsys_ndf.ndf.models import node_collection, Node
import re

#To find the below string occuring more than once <input align="right" id="toggler" type="checkbox"><label class="toggle-me" for="toggler">Transcript</label> '''
regx = re.compile("(id=\"toggler\"(?!for=\"toggler\").*?for=\"toggler\")",re.IGNORECASE)
 
# To collect all the activities under the English module
english_module_names = ['English Elementary','English Beginner'] 
english_modules = node_collection.find({'_type':'GSystem','name':{'$in':english_module_names}},{'_id':1,'collection_set':1})

page_gst_id = Node.get_name_id_from_type('Page','GSystemType')[1]
gsystemnds = node_collection.find({
            '_type':'GSystem',
            'member_of':page_gst_id,
            'group_set':{'$in':[eachid for each in english_modules for eachid in each.collection_set]},
            'collection_set':[],
            'content':regx})

#For each node if the pattern matched more than twice then we change the first 2 occurances of the string "toggler" with "toggler09"
for each in gsystemnds:
    matches = re.findall(regx,str(each.content))
    flag = False
    if len(matches) > 1:
        flag = True
        each.content = each.content.replace('"toggler"','"toggler09"',2)
    if flag:
        print "Saving :",each._id     # Printing the node id which got changed and is being saved
        each.save()
        flag = False
    
