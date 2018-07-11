import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen as uReq
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

print(datetime.now())

url=""                                                                                                                 #put the landing page here, usually localhost
stack=["/explore/courses"]
visited=[]
initial_time=[]
second_time=[]
while(len(stack)>0):
    str=stack.pop()
    visited.append(str)
    print(str)
    print(url+str)
    print(len(visited))
    try:
        init = datetime.now()
        content=requests.get(url+str, verify=False)
        initial_time.append(datetime.now()-init)
        temp = datetime.now()
        content=requests.get(url+str, verify=False)
        second_time.append(datetime.now()-temp)
        soup=BeautifulSoup(content.text,"html.parser")
        for link in soup.find_all('a'):
            target = link.get('href')
            # print(target)
            try:
                if ((target not in visited) and (target not in stack) and type(target) == type("bat") and target[0] == '/'):
                    #print(target)
                    if (".gif" in target or ".jpg" in target or ".png" in target or "/accounts/login" in target):
                        continue
                    stack.append(target)
            except:
                pass
        #the if will fire if there are hidden links
        if(str[-16:len(str)]=="/course/content/"):
            text=soup.prettify()                                                                                    #converts the response object into a string
            startpoint=text.find("course_data")                                                                     #finds the first(and only) occurance of the string "course_data")
            text=text[startpoint:]                                                                                  #trim till the beginning of the line
            endpoint=text.find(";")                                                                                 #the first occurance of the semicolon gives the end of line
            required=text[14:endpoint]                                                                              #get the list string
            json=[]                                                                                                 #name the list something relevant
            required='json = '+required                                                                             #append command to the start
            exec(required)                                                                                          #execute the command
            #print(json)
            modifiedstr = str[:str.find("content")]
            modifiedstr = modifiedstr + "activity_player/"                                                          #that's how the URLs are designed
            #print(modifiedstr)
            for chapter in json:
                hidden = chapter["id"]
                children = chapter["children"]
                for j in children:
                    hidden_child = j["id"]
                    #print(url + modifiedstr + hidden + '/' + hidden_child)
                    req = requests.get(url + modifiedstr + hidden + '/' + hidden_child, verify="False")             #leaf nodes, just requested, not parsed.
                    print("Requested Successfully")
    except Exception as e:                                       
        print(e)
        print("Sorry couldn't parse")
        pass
print(datetime.now())
print(len(visited))


'''
url="http://doer.metastudio.org"
str="/59425be44975ac013cccb909/course/content/"
res = requests.get(url+str)
print(type(res))
content= uReq(url+str)
req=requests.get("http://doer.metastudio.org/59425fc64975ac013d976b32/course/content/")
soup = BeautifulSoup(content,'lxml')
text=soup.prettify()
startpoint=text.find("course_data")
text=text[startpoint:]
endpoint=text.find(";")
req=text[14:endpoint]
json=[]
req='json = '+req
print(req)
exec(req)
#print(json)
modifiedstr=str[:str.find("content")]
modifiedstr=modifiedstr+"activity_player/"
print(modifiedstr)
for i in json:
    st=i["id"]
    children=i["children"]
    for j in children:
        stc=j["id"]
        print(url+modifiedstr+st+'/'+stc)
        req=uReq(url+modifiedstr+st+'/'+stc)
        print("Requested Successfully")

test="print('Hello World')"
exec(test)
#print(req)
#print(text)
#print(type(text))
for link in soup.find_all('a'):
    pass
    #print(link.get('href'))
'''
