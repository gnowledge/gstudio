'''
Issue :Write a note icon is not working in any of the three languages 
       Unit1: Making and Solving Puzzles
                Lesson 1:Making and Solving Puzzles
                        Activity 4 : Creating, Asking and Answering Puzzles
        Unit 3 : Measuring the seeds
                Lesson 3: Measuring the seeds
                        Activity 1 : Measuring the Diameter
                        Activity 2 : Measuring the size of the Seeds
                        Activity 3 : Analysis
                        Activity 5 : Combining the data

Issue : Upload icon not working
        Unit 3 : Measuring the seeds
                Lesson 3 : Measuring the seeds
                        Activity 3 : Analysis

Fix :  Authoring Issue, where in the url mentioned under href is not proper which has to strt with '/'

'''


import re
from gnowsys_ndf.ndf.models import node_collection
from bs4 import BeautifulSoup  

#To identify the href starting with digit but not with "/"
regx1 = '^\d' 

le_module_name = "Linear Equations"
le_modules = node_collection.find({'_type':'GSystem','name':{'$in':le_module_name}},{'_id':1,'collection_set':1})

page_gst_id = node_collection.one({'_type': 'GSystemType', 'name': 'Page'})._id

#Extracting all activities under the Linear Equations module
legsystmnds = node_collection.find({
        '_type':'GSystem', 
        'member_of':page_gst_id,
        'group_set':{'$in':[eachid for each in le_modules for eachid in each.collection_set]},
        'collection_set':[]})
   

#To fetch the faulty hrefs and update them accordingly. This covers the e-Notes as well as Upload
for index, each_nd in enumerate(legsystmnds,start =1):
     soup = BeautifulSoup(each_nd.content)
     findflg = soup.find_all('a')
     if findflg:
         for link in findflg:
             linkaddr = link.get("href")
             flag = False
             if re.match(regx1,linkaddr):
                 flag = True
                 linkaddr = "/"+linkaddr
                 link['href'] = linkaddr
                 each_nd.content = soup
             if flag:
                 print "Changing:", each_nd._id
    		 each_nd.save()
     

