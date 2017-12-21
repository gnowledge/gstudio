# Script to parse course content and create corresponding pages and modules
# Task: edX Exchange
# Author: Stuti R. Rastogi
# Date: 14th July, 2014

##############################################################################################################

''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError
from django_mongokit import get_database

try:
  from bson import ObjectId
except ImportError:  # old pymongo
  from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import *

''' import ElementTree to parse xml files '''
import xml.etree.ElementTree as et

import time

#############################################################################################################

 # global variables
db = get_database()
collection = db[Node.collection_name]

page_fetch = collection.Node.one({'_type':'GSystemType', 'name': 'Page'})
page_id = page_fetch._id            # id of GSystemType page

module_fetch = collection.Node.one({'_type':'GSystemType', 'name': 'Module'})
module_id = module_fetch._id         # id of GSystemType module

class Command(BaseCommand):

    help = "This script will parse the course xml and create pages and modules accordingly."
    
    def handle(self, *args, **options):

        # user input for manually downloaded course location
        path = raw_input("Enter the path of downloaded course (eg: /home/username/Downloads/edx_demo_course/): ")

        # user input for the group where the pages will be created
        group_name = raw_input("Enter group name to create pages in: ")

        group = collection.Node.find({'_type' : 'Group', 'name' : unicode(group_name)})
        if group.count() == 0:
            print "No such group exists, using default home group..."
            time.sleep(2)
            group = collection.Node.one({'_type' : 'Group', 'name' : 'home'})
        else:
            print "Group exists. Creating pages..."
            time.sleep(2)
            group = collection.Node.one({'_type' : 'Group', 'name' : unicode(group_name)})

        group_id = group._id

        course_xml_path = path + "/course.xml"
        course_xml = et.parse(course_xml_path)
        course_url_name = course_xml.getroot().get("url_name")

        # The url_name gives the name of xml file having course structure (chapters)

        course_url_name_xml_path = path + "/course/" + course_url_name + ".xml"
        course_url_name_xml = et.parse(course_url_name_xml_path)

        for chapter in course_url_name_xml.getroot().iter("chapter"):
            chapter_url_name = chapter.get("url_name")                  # name of each chapter
            chapter_xml_path = path + "/chapter/" + chapter_url_name + ".xml"
            chapter_xml = et.parse(chapter_xml_path)
            chapter_display_name = chapter_xml.getroot().get("display_name")

            # chapters are made of one or more sequentials
            for seq in chapter_xml.getroot().iter("sequential"):
                seq_url_name = seq.get("url_name")
                seq_xml_path = path + "/sequential/" + seq_url_name + ".xml"
                seq_xml = et.parse(seq_xml_path)
                seq_display_name = seq_xml.getroot().get("display_name")

                # Each sequential is a module in metastudio - made up of many pages (verticals)
                module = collection.GSystem()
                module.name = unicode(seq_display_name)
                module.content = unicode(seq_display_name)
                module.member_of.append(ObjectId(module_id))
                module.group_set.append(ObjectId(group_id))
                module.created_by = 1
                module.modified_by = 1
                module.collection_set = []


                # sequentials are made of one or more verticals
                for ver in seq_xml.getroot().iter("vertical"):
                    ver_url_name = ver.get("url_name")
                    ver_xml_path = path + "/vertical/" + ver_url_name + ".xml"
                    ver_xml = et.parse(ver_xml_path)
                    ver_display_name = ver_xml.getroot().get("display_name")
                    content = ""
                    content_org_start = "\r\n#+BEGIN_HTML \r\n"
                    content_org_end = "\r\n#+END_HTML\r\n"
                    
                    # A vertical can consist of html, problems, videos, discussions, etc.
                    # Each of these is a different element.

                    # We create one page for each vertical and append content to it
                    page = collection.GSystem()
                    page.name = unicode(ver_display_name)
                    page.member_of.append(ObjectId(page_id))        # page is member of Page GSystemType
                    page.created_by = 1
                    page.modified_by = 1
                    page.contributors.append(1)
                    page.content = unicode(content)
                    page.content_org = unicode(content_org_start + content + content_org_end)
                    page.group_set.append(ObjectId(group_id))
                    page.author_set.append(1)
                    page.access_policy = u"PUBLIC"
                    page.status = u"PUBLISHED"

                   
                    for element in ver_xml.getroot().getchildren():
                        tag = element.tag                   # the name of the element
                        url = element.get("url_name")
                        
                        element_path = path + "/" + tag + "/" + url + ".xml"
                        element_xml = et.parse(element_path)
                        element_name = element_xml.getroot().get("display_name")

                        if tag == "html":
                            html_filename = element_xml.getroot().get("filename")
                            html_path = path + "/html/" + html_filename + ".html"

                            # Get content of the HTML file with tags in a variable
                            with open(html_path, 'r') as f:
                                html_content = f.read()
                            f.close()

                            # Append the HTML content to the page created for the vertical
                            content = content + html_content

                        else:
                            with open(element_path, 'r') as f:
                                element_content = f.read()
                            f.close()

                            # Append the XML content to the page created for the vertical
                            content = content + element_content


                    page.content = unicode(content)
                    page.content_org = unicode(content_org_start + content + content_org_end)

                    page.save()                 # The page is saved in the database

                    module.collection_set.append(ObjectId(page._id))

                module.save()