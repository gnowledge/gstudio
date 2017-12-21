''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from django_mongokit import get_database
from mongokit import IS

try:
  from bson import ObjectId
except ImportError:  # old pymongo
  from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import *
import xlrd,csv
from collections import defaultdict

####################################################################################################################
''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import Node
db=get_database()
collection =db['Nodes']
theme_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Theme' })
theme_item_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'theme_item' })
topic_GST = collection.Node.one({'_type': 'GSystemType', 'name': 'Topic'})
get_group=collection.Node.one({'_type':'Group', 'name':u'home'})
theme_list=collection.Node.find({'$and':[{'member_of':theme_GST._id},{'group_set':get_group._id}]})
schema_file_xls = os.path.join( os.path.dirname(__file__), "schema_files/ncf_hindi_themes.xls")
schema_file_csv = os.path.join( os.path.dirname(__file__), "schema_files/theme_translations.csv")
wb=xlrd.open_workbook(schema_file_xls)
sheet = wb.sheet_by_index(0)
csv_file = open(schema_file_csv, 'wb')
wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
for rownum in xrange(sheet.nrows):
    wr.writerow([unicode(val).encode('utf8') for val in sheet.row_values(rownum)])
csv_file.close()

# print "file createddddd"

class Command(BaseCommand):
    help = "Creating translations of themes"

    def handle(self, *args, **options):
      print "---------------------------------------------------\n"
      main()

def main():
  #print "main"
  columns = defaultdict(list)
  translation_dict={}

  get_translation_rt=collection.Node.one({'$and':[{'_type':'RelationType'},{'name':u"translation_of"}]})
  with open(schema_file_csv, 'rb') as f:
    reader = csv.reader(f)
    i = 1
    reader.next()
    for row in reader:
      for (i,v) in enumerate(row):
        columns[i].append(v)
    translation_dict=dict(zip(columns[0],columns[1]))
    #print translation_dict,"dict"
    for k, v in translation_dict.items():
      theme_elements=collection.Node.find({'name':k})
      for each in list(theme_elements):
        get_node=collection.Node.one({'_id':ObjectId(each._id)})
        if get_node:
          member_of=get_node.member_of_names_list
          if "Theme" in member_of:
            app_obj = theme_GST
          else:
            if "theme_item" in member_of:
              app_obj = theme_item_GST
            else:
              app_obj = topic_GST

          name=v.decode('utf-8')
          #print name,"name"
          theme_node_rt = collection.Node.find({'$and':[{'_type':"GRelation"},{'relation_type':get_translation_rt._id},{'subject':get_node._id}]})
          if theme_node_rt.count() > 0:
            theme_node = collection.Node.one({'_id': ObjectId(theme_node_rt[0].right_subject) })
          else:
            theme_node = None
            theme_node_rt = None

          if theme_node is None:
            theme_node = collection.GSystem()
            theme_node.name = unicode(name)
            theme_node.access_policy = u"PUBLIC"
            theme_node.contributors.append(1)
            theme_node.created_by = 1
            theme_node.group_set.append(get_group._id)
            theme_node.language = u"hi"
            theme_node.member_of.append(app_obj._id)
            theme_node.modified_by = 1
            theme_node.status = u"DRAFT"
            theme_node.save()
            print "\nTranslated Node ",theme_node.name," created successfully\n"
          else:
            print "\nTranslated node ",theme_node.name," already exists\n"

          if theme_node_rt is None:

            relation_type=collection.Node.one({'$and':[{'name':'translation_of'},{'_type':'RelationType'}]})
            grelation=collection.GRelation()
            grelation.relation_type=relation_type
            grelation.subject=each._id
            grelation.right_subject=theme_node._id
            grelation.name=u""
            grelation.save()
            print "\nGRelation for node ",theme_node.name," created sucessfully!!"
          else:
            print "\nGRelation for node ",theme_node.name," already exists\n"

    for k, v in translation_dict.items():
      theme_elements=collection.Node.find({'name':k})
      for each in list(theme_elements):
        theme_node_rt=collection.Node.find({'$and':[{'_type':"GRelation"},{'relation_type':get_translation_rt._id},{'subject':each._id}]})
        t_node=collection.Node.one({'_id':ObjectId(each._id)})
        if theme_node_rt:
          for node in list(theme_node_rt):
            theme_node=collection.Node.one({'_id':node.right_subject})
            if t_node.collection_set:
              trans_list=[]
              for rt in t_node.collection_set:
                get_rt=collection.Node.find({'$and':[{'_type':"GRelation"},{'relation_type':get_translation_rt._id},{'subject':rt}]})
                if get_rt:
                  for each in list(get_rt):
                    trans_list.append(each.right_subject)

              print "\nProcessing the translated collection_set for node ",theme_node.name," ...\n"
              if trans_list != theme_node.collection_set:
                theme_node.collection_set=trans_list
                theme_node.save()
                print "Translated collection_set for node ",theme_node.name," updated successfully\n"
              else:
                print "Translated collection_set for node ",theme_node.name," already exists"
