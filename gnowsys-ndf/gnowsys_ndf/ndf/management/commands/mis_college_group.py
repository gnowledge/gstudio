''' -- imports from python libraries -- '''
import os

''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError

from django_mongokit import get_database

try:
    from bson import ObjectId
except ImportError:  # old pymongo
    from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.ndf.models import Node, Group

####################################################################################################################

collection = get_database()[Node.collection_name]

SCHEMA_ROOT = os.path.join( os.path.dirname(__file__), "schema_files" )

log_list = [] # To hold intermediate error and information messages

####################################################################################################################

class Command(BaseCommand):
  """This script creates private group for each college; and assigns college-group's id to group_set field of respective Student & Voluntary Teacher nodes.
  """

  help = "\tThis script creates private group for each college; and assigns college-group's id to group_set field of respective Student & Voluntary Teacher nodes."

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
          log_list.append(info_message)
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
        log_list.append(info_message)
      
    except Exception as e:
      error_message = "\n CollegeGroupCreateError: " + str(e) + " !!!\n"
      log_list.append(error_message)
      raise Exception(error_message)

    system_type = ""
    try:
      # Assigning college's group id to group_set field of respective Student nodes
      system_type = "Student"
      info_message = "\n\n *** Assigning college's group id to group_set field of respective "+system_type+" nodes \n"
      log_list.append(info_message)
      assign_groupid(system_type)

      # Assigning college's group id to group_set field of respective Voluntary Teacher nodes
      system_type = "Voluntary Teacher"
      info_message = "\n\n *** Assigning college's group id to group_set field of respective "+system_type+" nodes \n"
      log_list.append(info_message)
      assign_groupid(system_type)

    except Exception as e:
      error_message = "\n CollegeGroupUpdateError ("+system_type+"): " + str(e) + " !!!\n"
      log_list.append(error_message)
      raise Exception(error_message)

    finally:
      if log_list:

        log_list.append("\n ============================================================ End of Iteration ============================================================\n")

        log_file_name = os.path.splitext(os.path.basename(__file__))[0] + ".log"
        log_file_path = os.path.join(SCHEMA_ROOT, log_file_name)

        with open(log_file_path, 'a') as log_file:
          log_file.writelines(log_list)

	# ------------------------ End of handle() --------------------------------    


def assign_groupid(system_type):
  try:
    system_type_id = collection.Node.one({'_type': "GSystemType", 'name': system_type})._id
    system_type_cur = collection.Node.find({'_type': "GSystem", 'member_of': system_type_id})

    for n in system_type_cur:
      possible_relations = n.get_possible_relations(n.member_of)
      
      if system_type == "Student":
        colg_list = possible_relations["student_belongs_to_college"]["subject_or_right_subject_list"]
      else:
        colg_list = possible_relations["trainer_of_college"]["subject_or_right_subject_list"]
      
      group_set_updated = False

      for colg in colg_list:
        colg_group_id = collection.Node.one({'_type': "Group", 'group_type': "PRIVATE", 'name': colg.name})._id
        if colg_group_id not in n.group_set:
          n.group_set.append(colg_group_id)
          group_set_updated = True
          info_message = "\n CollegeGroupUpdation: This "+system_type+" ("+n.name+" - "+str(n._id)+") is added to college group ("+colg.name+" - "+str(colg_group_id)+") successfully. \n"
          log_list.append(info_message)

      if group_set_updated:
        n.save()

  except Exception as e:
    error_message = " For "+n.name+" ("+str(n._id)+") - "+str(e)+" !!!"
    raise Exception(error_message)

