#imports from python package#############################################################################################################

from email.message import Message
from email.parser import Parser
import datetime
import re
import os
import subprocess

#########################################################################################################################################


inputfile = open('','r+')
line = inputfile.readline()
mailparser = Parser()
messages = []
i = 0


def process(message):
        "This function processes the body of every mail and decides what action is to be performed"
        os.chdir("/var/lib/mailman/bin")

        body = message.get_payload()
        b = body.split('\n')
        subject = b[0]
        #print body
        if re.search(r"^create list",subject):
                listname = b[2].split(':',1)[1]
                adminname = b[1].split(':',1)[1]
                subprocess.call(["sudo","newlist","-q",listname,adminname,"gnowledge"])
                #print("created the list: "+listname+"\n"+" admin: "+adminname+"\n")
        if re.search(r"^join a group",subject):
                listname = b[2].split(':',1)[1]
                useraddress = b[1].split(':',1)[1]
                fp = open('/home/glab/file1','w')
                fp.write(useraddress)
                fp.close()
                subprocess.call(["sudo","add_members","-r","/home/glab/file1",listname])
                #print("user: "+useraddress+" subscribed to the list: "+listname)

        if re.search(r"^unsubscribe from a group",subject):
                listname = b[2].split(':',1)[1]
                useraddress = b[1].split(':',1)[1]
                fp = open('/home/glab/file1','w')
                fp.write(useraddress)
                fp.close()
                subprocess.call(["sudo","remove_members","-f","/home/glab/file1",listname])
                #print("user: "+useraddress+" unsubscribed from the list: "+listname)

        if re.search(r"^post to list",subject):
                b=body.split('\n',6)
                useraddress = b[1].split(':',1)[1]
                listname = b[2].split(':',1)[1]
                forumname = b[3].split(':',1)[1]
                threadname = b[4].split(':',1)[1]
                object_id = b[5]
                thread_content = b[6]
                fp = open("/home/glab/file1","w")
                fp.write("From: "+useraddress+"\n")
                fp.write("To: "+listname+"@gnowledge.org"+"\n")
                fp.write("Date: "+str(datetime.datetime.now())+"\n")
                fp.write("ObjectId: "+object_id+"\n")
                fp.write("Subject: "+forumname+": "+threadname+"\n\n")
                fp.write(thread_content+"\n")
                fp.close()
                os.chdir("/usr/sbin")
                a=subprocess.Popen(["cat","/home/glab/file1"],stdout=subprocess.PIPE)
                b=subprocess.Popen(["sudo","sendmail","-i","-t"],stdin=a.stdout,stdout=subprocess.PIPE)
                output = b.communicate()[0]
                #print("user: "+useraddress+" posted to the list: "+listname)

        if re.search(r"reply to post",subject):
                b=body.split('\n',7)
                useraddress = b[1].split(':',1)[1]
                listname = b[2].split(':',1)[1]
                forumname = b[3].split(':',1)[1]
                threadname = b[4].split(':',1)[1]
                object_id = b[5]
                reply_id = b[6]
                reply = b[7]
                fp = open("/home/glab/file1","w")
                fp.write("From: "+useraddress+"\n")
                fp.write("To: "+listname+"@gnowledge.org"+"\n")
                fp.write("Date: "+str(datetime.datetime.now())+"\n")
                fp.write("ObjectId: "+object_id+"\n")
                fp.write("In-Reply-To: "+reply_id+"\n")
                fp.write("Subject: "+forumname+": "+threadname+"\n\n")
                fp.write(reply+"\n")
                fp.close()
                os.chdir("/usr/sbin")
                a=subprocess.Popen(["cat","/home/glab/file1"],stdout=subprocess.PIPE)
                b=subprocess.Popen(["sudo","sendmail","-i","-t"],stdin=a.stdout,stdout=subprocess.PIPE)
                output = b.communicate()[0]
                #print("user: "+useraddress+" posted to the list: "+listname)

        return


for next in inputfile:
        end = re.search(r"^From\s[A-Za-z0-9_.]+@[A-Za-z.]+.[A-Za-z]{1,4}\s\s[A-Za-z]{3}\s[A-Za-z]{3}\s\s[0-9]{1,2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}$
        if end:
                messages.append(mailparser.parsestr(line))
                process(messages[i])
                i += 1
                line = next
        else:
                line += next

messages.append(mailparser.parsestr(line))
process(messages[i])
inputfile.close()
subprocess.call(["sudo","rm",""])

