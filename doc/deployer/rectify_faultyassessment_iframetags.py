# The Assessment script covers the following usecases : 


#Usecase 1: Usecase which covers the correction of faulty iframe tags like the one with no proper ending iframe tags, no proper starting iframe tags, in the assessments.
#Usecase 2: Usecase also covers the correction of multiple faulty iframe tags in the same content.
#Usecase 3: Usecase which covers the conversion of special characters into websafe codec.  



import re
from gnowsys_ndf.ndf.models import *
from lxml import html
from lxml.html import tostring
import HTMLParser


# regular expression to cover the starting iframe tag with no proper ending iframe tags.
regx = re.compile("(<iframe[^>]*>(?!<\/iframe>))",re.IGNORECASE)                    

#based on above regular expression, In ct10,total 46 culprit iframe tags were found
all_culprit_iframes = node_collection.find({'_type':'GSystem','content':regx })
print(all_culprit_iframes.count())



#text_activity_node = node_collection.one({ '_type' : 'GSystem', '_id' : ObjectId( '5b8908c74ee17501aad05110' )  })      #5b88f0f54ee17501a9d1f76a
h = HTMLParser.HTMLParser()


for each in all_culprit_iframes:                                                                                            
      #index = index +1                     #display index numbers to count the total faulty iframe tags
      #print str(index) +" :\n"
      c = each.content                      #display the content in encoded format with faulty iframe tags.
    #  print c.encode("utf-8") ,"\n"
    #  print "*"*10
      each.content = c.replace('amp;','')                  #Removal of irrelevant characters.
      print each._id, "\n" #each.content.encode("utf-8"), "\n"                     #print the object ids
    #  print "?"*10
      each.content = h.unescape(each.content)              #replacement of &lt; &gt; with < > symbols.Converting special characters into websafe codec.
      txt1 = re.sub('><iframe','/><iframe',each.content)    
      c = tostring(html.fromstring(txt1 ), encoding='unicode')
      print c.encode("utf-8"), "\n" 
      print "="*30
      each.content = c
      each.save()
      #text_activity_node.content =  text_activity_node.content.encode("utf-8")+"<hr>"+str(each._id)+"</hr>"+c.encode("utf-8")
  
#print text_activity_node.content
