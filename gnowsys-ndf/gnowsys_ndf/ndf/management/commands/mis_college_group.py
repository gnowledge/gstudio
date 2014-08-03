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

########################################################################################################################

class Command(BaseCommand):
  """This script handles works related to MIS app.
  """

  help = "\tThis script handles works related to MIS app."

  def handle(self, *args, **options):
    print "\n options: ", options, "\n"

    # Creating private groups ------------------------------------------------------------------------------------------
    if False:
      try:
        create_college_group()

      except Exception as e:
        error_message = "\n CollegeGroupCreateError: " + str(e) + " !!!\n"
        log_list.append(error_message)
        raise Exception(error_message)

      finally:
        if log_list:
            log_list.append("\n ============================================================ End of Iteration ============================================================\n")

            log_file_name = os.path.splitext(os.path.basename(__file__))[0] + ".log"
            log_file_path = os.path.join(SCHEMA_ROOT, log_file_name)

            with open(log_file_path, 'a') as log_file:
              log_file.writelines(log_list)

    # Assigning Student & Voluntary Teacher Nodes' to respective college groups ----------------------------------------
    if True:
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


    # Creating enrollement code for Students ---------------------------------------------------------------------------
    if False:
      stud_cur = None
      college_cur = None

      try:
        collegeid = collection.Node.one({'_type': "GSystemType", 'name': "College"})._id
        studentid = collection.Node.one({'_type': "GSystemType", 'name': "Student"})._id
        rt_sc = collection.Node.one({'_type': "RelationType", 'name': "student_belongs_to_college"})
        at_ec = collection.Node.one({'_type': "AttributeType", 'name': "enrollment_code"})

        college_cur = collection.Node.find({'member_of': collegeid}, timeout=False).sort('name')

        for c in college_cur:
          c.get_neighbourhood(c.member_of)
          info_message = "\n\n College: " + c.name
          log_list.append(info_message)

          # Retrieve all students belonging to given college (c._id) -- RelationType (rt_sc -- student_belongs_to_college)
          stud_cur = collection.Triple.find({'_type': "GRelation", 'relation_type': rt_sc.get_dbref(), 'right_subject': c._id}, timeout=False)

          if stud_cur.count():
            for s in stud_cur:
              # Checking whether enrollment code is created for given student or not
              stud_en_node = collection.Triple.one({'_type': "GAttribute", 'subject': s.subject, 'attribute_type': at_ec.get_dbref()})
              
              if stud_en_node is None:
                # If not created, create it...
                info_message = "\n\n Creating enrollment code for " + s.name + "..."
                log_list.append(info_message)

                # last_enroll_code = get_count_of_enroll_students(c._id, rt_sc, at_ec)
                # new_enroll_code =  c.enrollment_code + ("%05d" % (last_enroll_num + 1))

                new_enroll_code =  get_new_enroll_code(rt_sc, at_ec, _id=c._id, enrollment_code=c.enrollment_code)

                create_enrollment_code(s.subject, at_ec, new_enroll_code)

                info_message = "\n Enrollment code for " + s.name + " created successfully."
                log_list.append(info_message)

              else:
                info_message = "\n Enrollment code for " + s.name + " already created !"
                log_list.append(info_message)

          else:
            info_message = "\n No students registered for this college !"
            log_list.append(info_message)

          if stud_cur.alive:
            info_message = "\n stud-Cursor state (before): " + str(stud_cur.alive)
            log_list.append(info_message)
            stud_cur.close()
            info_message = "\n stud-Cursor state (after): " + str(stud_cur.alive)
            log_list.append(info_message)

        if college_cur.alive:
          info_message = "\n college-Cursor state (before): " + str(college_cur.alive)
          log_list.append(info_message)
          college_cur.close()
          info_message = "\n college-Cursor state (after): " + str(college_cur.alive)
          log_list.append(info_message)

      except Exception as e:
        error_message = "\n StudentEnrollmentCodeCreateError: " + str(e) + "\n"
        log_list.append(error_message)
        raise Exception(error_message)

      finally:
        if stud_cur:
          if stud_cur.alive:
            info_message = "\n stud-Cursor state (f_before): " + str(stud_cur.alive)
            log_list.append(info_message)
            stud_cur.close()
            info_message = "\n stud-Cursor state (f_after): " + str(stud_cur.alive)
            log_list.append(info_message)

        if college_cur:
          if college_cur.alive:
            info_message = "\n college-Cursor state (f_before): " + str(college_cur.alive)
            log_list.append(info_message)
            college_cur.close()
            info_message = "\n college-Cursor state (f_after): " + str(college_cur.alive)
            log_list.append(info_message)

        if log_list:
          log_list.append("\n ============================================================ End of Iteration ============================================================\n")

          log_file_name = os.path.splitext(os.path.basename(__file__))[0] + ".log"
          log_file_path = os.path.join(SCHEMA_ROOT, log_file_name)

          with open(log_file_path, 'a') as log_file:
            log_file.writelines(log_list)

	# ------------------------ End of handle() --------------------------------    


def create_college_group():
  """
  Creates private group for each college; and appends glab's (superuser) user-id as a creator for each of them.

  Arguments: Empty

  Returns: Nothing
  """

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


def assign_groupid(system_type):
  """
  Assigns college-group's id to group_set field of respective Student & Voluntary Teacher nodes.

  Arguments:
  system_type -- Determines type of node i.e. either Student or Voluntary Teacher

  Returns: Nothing
  """
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


def get_new_enroll_code(relation_type_node, attribute_type_node, **college):
  """
  Returns new enrollment code
  - Finds list of all students belonging to given college (college["_id"])
  - Counts those students for whom enrollment code is created among the above list
  - Creates new enrollment code using the combination of given college's enrollment code and incementing above count

  Arguments:
  relation_type_node -- RelationType node (student_belongs_to_college)
  attribute_type_node -- AttributeType node (enrollment_code)
  **college -- Dict consisting of two keys - _id, enrollment_code

  Returns:
  Enrollment code as a basestring value
  """
  enroll_count = 0
  new_enroll_code = ""
  
  try:
    stud_cur = collection.Triple.find({'_type': "GRelation", 'relation_type': relation_type_node.get_dbref(), 'right_subject': college["_id"]}, timeout=False)

    for s in stud_cur:
      s_en = collection.Triple.one({'_type': "GAttribute", 'subject': s.subject, 'attribute_type': attribute_type_node.get_dbref()})
      if s_en:
        enroll_count = enroll_count + 1

    new_enroll_code = college["enrollment_code"] + ("%05d" % (enroll_count + 1))

  except Exception as e:
    error_message = " EnrollCodeCreateError - " + str(e) + "!!!"
    raise Exception(error_message)

  finally:
    if stud_cur.alive:
      info_message = "\n stud-Cursor state in get_count_of_enroll_students() (before): " + str(stud_cur.alive)
      log_list.append(info_message)
      stud_cur.close()
      info_message = "\n stud-Cursor state in get_count_of_enroll_students() (after): " + str(stud_cur.alive)
      log_list.append(info_message)    

  return new_enroll_code


def create_enrollment_code(stud_id, attribute_type_node, new_enroll_code):
  """
  Creates an attribute (enrollment_code) for given student (stud_id)

  Arguments:
  stud_id -- ObjectId of the student node
  new_enroll_code -- Enrollment code for given student (stud_id)

  Returns:
  Nothing
  """
  stud_en_node = None

  try:
    stud_en_node = collection.GAttribute()

    stud_en_node.subject = stud_id
    stud_en_node.attribute_type = attribute_type_node
    stud_en_node.object_value = new_enroll_code
    
    stud_en_node.status = u"PUBLISHED"
    stud_en_node.save()
    info_message = "\n GAttribute ("+stud_en_node.name+") created successfully."
    log_list.append(info_message)

  except Exception as e:
    error_message = " GAttributeCreateError ("+str(stud_id)+") - "+str(e)+" !!!"
    raise Exception(error_message)






