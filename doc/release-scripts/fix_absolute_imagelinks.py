'''
***Rectified_Issues***
Issue1 :The images in the activity pages are not showing up. The src of the image is given as absolute URL not that of relative
Fix :  Finding the activities having the image src as the absolute URL and then changing the same to the relative one.

-----------
Issue2: Activity Turtle Blocks icon redirecting to clixplatform.tiss.edu/turtle/ instead of clixserver.tiss.edu/turtle/
Fix: Finding the activities whose href source is absolute url: clixplatform.tiss.edu/turtle/ and then changing the same to the relative url: /turtle/.

'''


import re
from gnowsys_ndf.ndf.models import node_collection, Node
from bs4 import BeautifulSoup  

#Issue 1
#To identify the image src having the absolute URL 
regx = re.compile('"https:\/\/clixplatform.tiss.edu\/media',re.IGNORECASE)
regx1 = re.compile('"http:\/\/clixplatform.tiss.edu\/media',re.IGNORECASE) 

#Extracting all activity pages containing the above regx pattern in the content
page_gst_id = Node.get_name_id_from_type('Page','GSystemType')[1]
trnsnd_gst_id = Node.get_name_id_from_type('trans_node','GSystemType')[1]
activitynds = node_collection.find({'_type': 'GSystem','member_of':{'$in':[page_gst_id,trnsnd_gst_id]},'content': {'$in':[regx,regx1]},'collection_set': []})   

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
                    eachimg['src'] = imgsrc[imgsrc.index('/media') : ]
        if nodesave:
            eachnd.content = soup
            eachnd.content = eachnd.content.decode("utf-8")
            print "Changing :",eachnd._id       # Printing node which is changed
            eachnd.save()
            nodesave = False
    print "*"*30

#Issue 2
#Extracting all the activity pages containing href src as "clixplatform.tiss.edu/turtle"
turtle_regx = re.compile('"https:\/\/clixplatform.tiss.edu\/turtle',re.IGNORECASE)
turtle_nds = node_collection.find({'_type': 'GSystem','member_of':{'$in':[page_gst_id,trnsnd_gst_id]},'content': {'$in':[turtle_regx]},'collection_set': []})

for indx,eachnode in enumerate(turtle_nds,start =1):
    soup = BeautifulSoup(eachnode.content)
    fndanchor = soup.find_all('a')
    #print("previous content:",fndanchor)
    if fndanchor:
        #print indx ,"\t",":", eachnode._id,"\n"
        for each in fndanchor:
            if each.has_attr('href'):
                hrefsrc=each["href"]
                #print(hrefsrc)
                innerflag = hrefsrc.startswith("https://clixplatform") or hrefsrc.startswith("http://clixplatform")
                if innerflag:
                    nodesave = True
                    each["href"]="/turtle/"
                    #print("modified href",each["href"])
        if nodesave:
            eachnode.content=soup
            eachnode.content = eachnode.content.decode("utf-8")
            print "Changing :",eachnode._id
            eachnode.save()
            nodesave = False


