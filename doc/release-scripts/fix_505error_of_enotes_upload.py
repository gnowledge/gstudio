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
from gnowsys_ndf.ndf.models import node_collection, Node
from bs4 import BeautifulSoup  

#To identify the href starting with digit but not with "/"
regx = re.compile('<a href="[\d\w]*\/course\/notebook\/\?create=True"',re.IGNORECASE)
regx1 = '^\d' 

le_module_name = "Linear Equations"
le_modules = node_collection.find({'_type':'GSystem','name':le_module_name},{'collection_set':1})

page_gst_id = Node.get_name_id_from_type('Page','GSystemType')[1]
trnsnd_gst_id =Node.get_name_id_from_type('trans_node','GSystemType')[1]
#Extracting all activities under the Linear Equations module
legsystmnds = node_collection.find({
        '_type':'GSystem', 
        'member_of':{'$in':[page_gst_id,trnsnd_gst_id]},
        'group_set':{'$in':[eachid for each in le_modules for eachid in each.collection_set]},
        'collection_set':[],
        'content':regx})
   

#To fetch the faulty hrefs and update them accordingly. This covers the e-Notes as well as Upload
for index, each_nd in enumerate(legsystmnds,start =1):
     soup = BeautifulSoup(each_nd.content)         
     findflg = soup.find_all('a')
     flag = False
     if findflg:
         for link in findflg:
             linkaddr = link.get("href")
             if re.match(regx1,linkaddr):
                 flag = True
                 linkaddr = "/"+linkaddr
                 link['href'] = linkaddr
         if flag:
              each_nd.content = soup
              each_nd.content = each_nd.content.decode("utf-8")
              print "Changing:", each_nd._id       # Printing the node which got changed
              each_nd.save()
     

