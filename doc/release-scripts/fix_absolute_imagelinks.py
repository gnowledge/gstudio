'''
Issue :The images in the activity pages are not showing up. The src of the image is given as absolute URL not that of relative

Fix :  Finding the activities having the image src as the absolute URL and then changing the same to the relative one.

'''


import re
from gnowsys_ndf.ndf.models import node_collection
from bs4 import BeautifulSoup  

#To identify the image src having the absolute URL 
regx = re.compile('"https:\/\/clixplatform.tiss.edu\/media',re.IGNORECASE)
regx1 = re.compile('"http:\/\/clixplatform.tiss.edu\/media',re.IGNORECASE) 

#Extracting all activity pages containing the above regx pattern in the content
page_gst_id = node_collection.one({'_type': 'GSystemType', 'name': 'Page'})._id
activitynds = node_collection.find({'_type': 'GSystem','member_of':page_gst_id,'content': {'$in':[regx,regx1]},'collection_set': []})   

nodesave = False

#To fetch the faulty src of images and correct them
for index,eachnd in enumerate(activitynds,start =1):
    soup = BeautifulSoup(eachnd.content)
    fndflg = soup.find_all('img')
    if fndflg:
        print index ,"\t",":", eachnd._id,"\n"
        for eachimg in fndflg:
            if eachimg.has_attr('src'):
                imgsrc = eachimg["src"]
                innerflg = imgsrc.startswith("https://clixplatform") or imgsrc.startswith("http://clixplatform")
                if innerflg:
                    nodesave = True
                    #print index, "\t", eachnd._id,
                    eachimg['src'] = imgsrc[imgsrc.index('/media') : len(imgsrc)]
        if nodesave:
            eachnd.content = soup
            eachnd.content = eachnd.content.decode("utf-8")
            print "Changing :",eachnd._id       # Printing node which is changed
            eachnd.save()
    print "*"*30

