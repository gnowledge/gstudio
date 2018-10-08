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

'''To identify the href starting with digit but not with "/"''';
regx1 = '^\d' 

'''Extracting all activities under the Linear Equations module'''
LEGSystmnds = node_collection.find({
        '_type':'GSystem', 
        'member_of':[ObjectId('5752ad552e01310a05dca4a1')],
        'group_set':{'$in':[
            ObjectId('59b665592c47962c1d002711'),ObjectId('59b666132c47962c1d002874'),
            ObjectId('59b662f42c47962c1d002147'),ObjectId('59b663de2c47962c1d002620')]},
        'collection_set':[]})
   

'''To fetch the faulty hrefs and update them accordingly. This covers the e-Notes as well as Upload'''
for index, each_nd in enumerate(LEGSystmnds,start =1):
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
                 #print each_nd.content.encode("utf-8")
     #print "="*30
     

