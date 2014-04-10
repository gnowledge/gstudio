''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import Node
db =get_database()
collection = db['Nodes']
import os
import subprocess
####################################################################################################################

class Command(BaseCommand):
    """This update-script updates fields' data-types or their values.
    """

    help = "\tThis update-script updates fields' data-types or their values."

    def handle(self, *args, **options):
        
        #fetch all nodes whoes mime_type contain pdf or svg
        try:
            nodes = collection.Node.find({'$or':[{ 'mime_type': { '$regex': 'pdf', '$options': 'i' }},{ 'mime_type': { '$regex': 'svg', '$options': 'i' }}]})
            for each in nodes:
                node = collection.Node.one({'_id':ObjectId(each['_id'])})
                if node is not None:
                    if node.fs_file_ids:
                        if (node.fs.files.exists(node.fs_file_ids[0])):
                            if len(node.fs_file_ids) == 1:
                                grid_fs_obj = node.fs.files.get(ObjectId(node.fs_file_ids[0]))
                                thumbnail_pdf = convert_pdf_thumbnail(grid_fs_obj,node._id)
                                tobjectid = node.fs.files.put(thumbnail_pdf.read(), filename=thumbnail_pdf.name)
                                collection.File.find_and_modify({'_id':node._id},{'$push':{'fs_file_ids':tobjectid}})
                                print "this file",str(node._id),"succesfully updated"
                            else:
                                print "This file's:",str(node._id),"thumbnail already created"
                        else:
                            print "1.this file dont have fs_file_ids[0]"
                    else:
                        print "2.this file dont have fs_file_ids[0]"
                else:
                    print "incorrect node"
        except Exception as e:
            print "Error Occured",e
        # --- End of handle() ---

def convert_pdf_thumbnail(files,_id):
    '''                                                                                                                                       
    convert pdf file's thumnail                                                                                                               
    '''
    filename = str(_id)
    os.system("mkdir -p "+ "/tmp"+"/"+filename+"/")
    fd = open('%s/%s/%s' % (str("/tmp"),str(filename),str(filename)), 'wb')
    files.seek(0)
    fd.write(files.read())
    fd.close()
    subprocess.check_call(['convert', '-thumbnail', '128x128',str("/tmp/"+filename+"/"+filename+"[0]"),str("/tmp/"+filename+"/"+filename+"-thumbnail.png")])
    thumb_pdf = open("/tmp/"+filename+"/"+filename+"-thumbnail.png", 'r')
    return thumb_pdf


