'''
Issue :The drawing link is not allowing one to draw

Fix	: URL mentioned under href is not proper and has modified to the correct one

'''


import re
from gnowsys_ndf.ndf.models import node_collection
from bs4 import BeautifulSoup  

'''To identify the href without "/"'''
regx1 = '^/sugar/activities/Paint.activity/'

'''Extracting the activities having the issue

GR:II --> Property Based Reasoning --> Representing Relationships 2
GR:I  --> Analysing and Describing shapes -->Analysing Shapes -->Sorting Shapes'''

GRGSystmnds = node_collection.find({'_type':'GSystem',
				    '$or':[{'_id':ObjectId('59425d1c4975ac013cccbba3')},{'_id':ObjectId('59425e4d4975ac013cccbcb4')}]})

   
'''To fetch the faulty hrefs and update them accordingly.'''
for index,each_nd in enumerate(GRGSystmnds,start =1):
       #print index,each_nd._id,str(each_nd.content)
       soup = BeautifulSoup(each_nd.content)
       findflg = soup.find_all('a') 
       if findflg:
           for link in findflg:
	       flag = False
               linkaddr = link.get("href")
               if re.match(regx1,linkaddr):
                   #print "Before:",linkaddr
                   if linkaddr.endswith('n='):
                       flag = True
                       linkaddr +='Paint'
                       link["href"] = linkaddr 
                       #print "After:",linkaddr
                       each_nd.content = soup
                   if flag: 
                       each_nd.save()
                       #print each_nd.content.encode("utf-8")
       print "="*30
 

