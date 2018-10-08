
'''Issue: In a particular activity page, there are multiple transcripts and on click of the later has effect on the former but not on the corresponding
   Reson: Both the transcripts are having the same ID 
  Unit : English Beginner Lesson Name : Places Around Us Acitity page :Warm Up

 Fix : Have modified the first encountered ID as Toggler09

'''

from gnowsys_ndf.ndf.models import node_collection
import re

''' To collect all the activities under the English module'''
GSystemnds = node_collection.find({
            '_type':'GSystem',
            'member_of':[ObjectId('5752ad552e01310a05dca4a1')],
            'group_set':{'$in':[
                    ObjectId('5943ff594975ac013d3701fc'),ObjectId('5943fd564975ac013d36fdae'),
                    ObjectId('59425be44975ac013cccb909'),ObjectId('59b6565c2c47960148218050')]},
            'collection_set':[]})

'''Pattern to identity the Multiple ID = toggler 
To find the below string occuring more than once
<input align="right" id="toggler" type="checkbox"><label class="toggle-me" for="toggler">Transcript</label> '''
regx = "(id=\"toggler\"(?!for=\"toggler\").*?for=\"toggler\")"
 
'''Found only one id :59425bed4975ac013cccb981------59425be44975ac013cccb909'''
 
'''For each node if the pattern matched more than twice then we change the first 2 occurances of the string "toggler" with "toggler09" '''
for each in GSystemnds:
    matches = re.findall(regx,str(each.content))
    flag = False
    if len(matches) > 1:
        flag = True
        trns_faulty_nd = node_collection.one({'_id':ObjectId(each._id)})
        trns_faulty_nd.content.replace('"toggler"','"toggler09"',2)
    if flag:    
    trns_faulty_nd.save()
