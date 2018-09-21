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
all_culprit_iframes = node_collection.find({'_type':'GSystem', 'content':regx })
print "Total Objects containing Faulty Iframe Tags: ", all_culprit_iframes.count()
htmlparser = HTMLParser.HTMLParser()

for index, each in enumerate(all_culprit_iframes, start=1):                                                                                            
      content = each.content                      # display the content in encoded format with faulty iframe tags.
      # print content.encode("utf-8"), "\n"
      # print "*"*30
      each.content = content.replace('amp;', '')   # Removal of irrelevant characters.
      print index, ". ", each._id                               # print the Assesment object ids
      each.content = htmlparser.unescape(each.content)  # Replacement of &lt; &gt; with < > symbols.Converting special characters into websafe codec.
      rectifiedcontent = re.sub('><iframe','/><iframe', each.content)    
      content = tostring(html.fromstring(rectifiedcontent), encoding='unicode')
      # print content.encode("utf-8"), "\n" 
      # print "="*30
      each.content = content
      #each.save()
      
  

