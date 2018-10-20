'''
Issue :The images in the activity pages are not showing up. The src of the image is given as absolute URL not that of relative

Fix :  Finding the activities having the image src as the absolute URL and then changing the same to the relative one.

'''


import re
from gnowsys_ndf.ndf.models import node_collection
from bs4 import BeautifulSoup  

#To identify the image src having the absolute URL 
regx = re.compile('"https:\/\/clixplatform.tiss.edu\/media',re.IGNORECASE) 

#Extracting all activity pages containing the above regx pattern in the content
page_gst_id = node_collection.one({'_type': 'GSystemType', 'name': 'Page'})._id
activitynds = node_collection.find({'_type': 'GSystem','member_of':page_gst_id,'content': regx,'collection_set': []})   

#To fetch the faulty src of images and correct them
 for index,eachnd in enumerate(activitynds,start =1):
     soup = BeautifulSoup(eachnd.content)
     fndflg = soup.find_all('img')
     if fndflg:
         print index ,"\t",":", eachnd_id
         for eachimg in fndflg:
             imgsrc = eachimg["src"]
             print imgsrc,"\n"
             nodesave = False
             innerflg = imgsrc.startswith("https://clixplatform")
             if innerflg:
                 nodesave = True
                 print index, "\t", eachnd._id,":\n"
                 imgsrc = imgsrc[imgsrc.index('/media') : len(imgsrc)]
         if nodesave:
             print "Changing :",eachnd._id
             eachnd.save()


