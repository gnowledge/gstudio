'''
Issue :Transcript for model comversations stunted

Fix	: The CSS used for the transcript part is not same as that of the others (which used the toggler CSS). Have made the required changes for the transcripts
      related to the audio and model conversations which come up on click of answer this in Unit 0 :English Beginner Lesson 8 : Let's Talk 

This script addresses a particular activity node, hence hardcoded the node id may not work for every server

'''


import re
from gnowsys_ndf.ndf.models import node_collection
from bs4 import BeautifulSoup  

'''Extracting the let's talk activity having the issue'''

changedflg = False

actnd = node_collection.one({'_type':'GSystem','_id':ObjectId('59b653d42c47960149a1287f')})

soup = BeautifulSoup(actnd.content)

mrkup2 = '<form class="trans-form"><input align="right" id="toggler09" type="checkbox" /> <label class="toggle-me" for="toggler09">Transcript</label><div class="transcript"><object data="/media/b/0/b/3537c6b9800766bde84555191d5b510c5d760afc72a8fea888b765258369f.txt" style="width:99%!important; height:auto!important;word-wrap: break-word;" type="text/html"></object></div></form>'
mrkup3 = '<form class="trans-form"><input align="right" id="toggler08" type="checkbox" /> <label class="toggle-me" for="toggler08">Transcript</label><div class="transcript"><object data="/media/d/0/c/94657554e663a44dc3dfa309454108a4ba5bbc620131bb7a1a1e1d089cb88.txt" style="width:99%!important; height:auto!important;word-wrap: break-word;" type="text/html"></object></div></form>'
mrkup4 = '<form class="trans-form"><input align="right" id="toggler07" type="checkbox" /> <label class="toggle-me" for="toggler07">Transcript</label><div class="transcript"><object data="/media/2/a/3/7868f3d837d326586fe59f6b1f1abdde16b3bfcbcb1e239511877d6963583.txt" style="width:99%!important; height:auto!important;word-wrap: break-word;" type="text/html"></object></div></form>'


'''Replace the transcript related tags with the required'''
for each in soup.find_all('input',{"class":"small radius transcript-toggler"}):
     #print each['class'],each.attrs,each.attrs.keys()
     stylflg = each.has_attr('style')
     if stylflg:
         #for child in each.parent.children:
         #    print each.parent.children
         prnt_div = each.parent
         inner_divtag = prnt_div.find('div',{"class":"transcript-data hide"})
         #print inner_divtag
         trnscrpt_file = inner_divtag.find('object')['data']
         #print trnscrpt_file
         if trnscrpt_file.split('/')[-1] == '3537c6b9800766bde84555191d5b510c5d760afc72a8fea888b765258369f.txt':
             inner_divtag.decompose()
             each.replaceWith(BeautifulSoup(mrkup2,'html.parser'))
             changedflg = True
         if trnscrpt_file.split('/')[-1] == '94657554e663a44dc3dfa309454108a4ba5bbc620131bb7a1a1e1d089cb88.txt':
             inner_divtag.decompose()
             each.replaceWith(BeautifulSoup(mrkup3,'html.parser'))
             if not changedflg:
                  changedflg = True
         if trnscrpt_file.split('/')[-1] == '7868f3d837d326586fe59f6b1f1abdde16b3bfcbcb1e239511877d6963583.txt': 
             inner_divtag.decompose()
             each.replaceWith(BeautifulSoup(mrkup4,'html.parser'))
             if not changedflg:
                  changedflg = True

if actnd and changedflg:
     print "Saving :", actnd._id    #Printing the id of the changed node before saving it
     actnd.content = soup
     actnd.content = actnd.content.decode("utf-8")
     actnd.save()
     changedflg = False

