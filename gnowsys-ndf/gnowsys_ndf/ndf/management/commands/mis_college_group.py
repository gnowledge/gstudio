''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import Node, Group

collection = get_database()[Node.collection_name]

####################################################################################################################

class Command(BaseCommand):
  """This script creates private group for each college.
  """

  help = "\tThis script creates private group for each college."

  def handle(self, *args, **options):
    try:
      collegeid = collection.Node.one({'_type': "GSystemType", 'name': "College"})._id
      college_cur = collection.Node.find({'_type': "GSystem", 'member_of': collegeid})
      groupid = collection.Node.one({'_type': "GSystemType", 'name': "Group"})._id
      glab_created_by = collection.Node.one({'_type': "Author", 'name': "glab"}).created_by

      for n in college_cur:
        college_exists = collection.Node.one({'_type': "Group", 'name': n.name}, {'_id': 1, 'name': 1, 'group_type': 1})

        if college_exists:
          # If given college is found, don't create it again and pass the iteration
          info_message = "\n CollegeGroupAlreadyExists: Group ("+college_exists.group_type+") for this college ("+college_exists.name+") already exists with this ObjectId ("+str(college_exists._id)+") ! \n"
          print info_message
          continue

        gfc = collection.Group()
        gfc._type = u"Group"
        gfc.name = n.name
        gfc.member_of = [groupid]
        gfc.group_type = u"PRIVATE"
        gfc.created_by = glab_created_by
        gfc.modified_by = glab_created_by
        gfc.contributors = [glab_created_by]
        gfc.status = u"PUBLISHED"
        gfc.save()

        info_message = "\n CollegeGroupCreation: Group ("+gfc.group_type+") for this college ("+gfc.name+") with this ObjectId ("+str(gfc._id)+") created successfully. \n"
        print info_message
      
    except Exception as e:
      error_message = "\n CollegeGroupCreateError: " + str(e) + " !!!\n"
      print error_message
      raise Exception(error_message)

    # Assigning college's group id to group_set field of respective Student nodes
    assign_groupid("Student")

    # Assigning college's group id to group_set field of respective Voluntary Teacher nodes
    assign_groupid("Teacher")
    
def assign_groupid(system_type):
  try:
    system_type_id = collection.Node.one({'_type': "GSystemType", 'name': system_type})._id
    system_type_cur = collection.Node.find({'_type': "GSystem", 'member_of': system_type_id})

    for n in system_type_cur:
      n.get_neighbourhood(n.member_of)
      
      if system_type == "Student":
        colg_list = n.student_belongs_to_college
      else:
        colg_list = n.trainer_of_college
      
      for colg in colg_list:
        colg_group_id = collection.Node.one({'_type': "Group", 'group_type': "PRIVATE", 'name': colg.name})._id
        if colg_group_id not in n.group_set:
          n.group_set.append(colg_group_id)
          n.save()

  except Exception as e:
    error_message = "\n AssigCollegeGroupIDError: "+str(e)+" !!!\n"
    print error_message
    raise Exception(error_message)

