import xlrd
import csv
from collections import defaultdict

''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from mongokit import IS

try:
  from bson import ObjectId
except ImportError:  # old pymongo
  from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import *

####################################################################################################################
gapp = node_collection.one({'_type': u'MetaType', 'name': u'GAPP'})
schema_file_xls = os.path.join( os.path.dirname(__file__), "schema_files/app_names.xls")
schema_file_csv = os.path.join( os.path.dirname(__file__), "schema_files/app_translations.csv")
wb = xlrd.open_workbook(schema_file_xls)
sheet = wb.sheet_by_index(0)
csv_file = open(schema_file_csv, 'wb')
wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
for rownum in xrange(sheet.nrows):
    wr.writerow([unicode(val).encode('utf8') for val in sheet.row_values(rownum)])
csv_file.close()


class Command(BaseCommand):
    help = "Creating translations of app names"

    def handle(self, *args, **options):
      print "---------------------------------------------------\n"
      main()

def main():
  columns = defaultdict(list)
  translation_dict={}

  get_translation_rt = node_collection.one({'_type': 'RelationType', 'name': u"translation_of"})
  with open(schema_file_csv, 'rb') as f:
    reader = csv.reader(f)
    i = 1
    reader.next()
    for row in reader:
      for (i,v) in enumerate(row):
        columns[i].append(v)
    translation_dict=dict(zip(columns[0],columns[1]))
    print translation_dict,"dict"
    for k, v in translation_dict.items():
        app_items = node_collection.find({'name':k})
        for each in list(app_items):
            get_node = node_collection.one({'_id': ObjectId(each._id), 'member_of': gapp._id})
            if get_node:
                name=v.decode('utf-8')
                print get_node.name
                node_rt = triple_collection.find({'_type': "GRelation", 'subject': get_node._id, 'relation_type': get_translation_rt._id})
                if node_rt.count() > 0:
                    node = node_collection.one({'_id': ObjectId(node_rt[0].right_subject) })
                else:
                    node = None
                    node_rt = None

                if node is None:
                    node = node_collection.collection.GSystem()
                    node.name = unicode(name)
                    node.access_policy = u"PUBLIC"
                    node.contributors.append(1)
                    node.created_by = 1
                    #node.group_set.append(get_group._id)
                    node.language = u"hi"
                    node.member_of.append(gapp._id)
                    node.modified_by = 1
                    node.status = u"DRAFT"
                    node.save()
                    print "\nTranslated Node ",node.name," created successfully\n"
                else:
                    print "\nTranslated node ",node.name," already exists\n"

                if node_rt is None:
                    relation_type = node_collection.one({'_type': 'RelationType', 'name':'translation_of'})
                    gr_node = create_grelation(each._id, relation_type, node._id)
                    # grelation = triple_collection.collection.GRelation()
                    # grelation.relation_type=relation_type
                    # grelation.subject=each._id
                    # grelation.right_subject=node._id
                    # grelation.name=u""
                    # grelation.save()
                    print "\nGRelation for node ",node.name," created sucessfully!!"
                else:
                    print "\nGRelation for node ",node.name," already exists\n"


