'''
Issue :The drawing link is not allowing one to draw

Fix	: URL mentioned under href is not proper and has modified to the correct one

This script modifies two particular activities under Geometrical Reasoning

GR:I  --> Analysing and Describing shapes -->Analysing Shapes -->Sorting Shapes
GR:II --> Property Based Reasoning --> Representing Relationships 2

Hence this may not work for every server
'''


import re
from gnowsys_ndf.ndf.models import node_collection
from bs4 import BeautifulSoup  

'''To identify the href without "/"'''
regx1 = '^/sugar/activities/Paint.activity/'

grgsystmnds = node_collection.find({'_type':'GSystem',
				    '$or':[{'_id':ObjectId('59425d1c4975ac013cccbba3')},{'_id':ObjectId('59425e4d4975ac013cccbcb4')}]})

   
'''To fetch the faulty hrefs and update them accordingly.'''
for index,each_nd in enumerate(grgsystmnds,start =1):
       #print index,each_nd._id,str(each_nd.content)
       soup = BeautifulSoup(each_nd.content)
       findflg = soup.find_all('a')
       flag = False 
       if findflg:
           for link in findflg:
               linkaddr = link.get("href")
               if re.match(regx1,linkaddr):
                   #print "Before:",linkaddr
                   if linkaddr.endswith('n='):
                       flag = True
                       linkaddr +='Paint'
                       link["href"] = linkaddr 
                       #print "After:",linkaddr
           if flag: 
                  print "Saving :", each_nd._id     # Printing the node which is changed and about to be saved
                  each_nd.content = soup
                  each_nd.save()
 

