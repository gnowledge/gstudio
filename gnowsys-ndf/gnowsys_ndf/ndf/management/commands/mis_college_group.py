''' -- imports from python libraries -- '''
import os
import time
import datetime

''' imports from installed packages '''
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from optparse import make_option

try:
  from bson import ObjectId
except ImportError:  # old pymongo
  from pymongo.objectid import ObjectId

''' imports from application folders/files '''
from gnowsys_ndf.settings import META_TYPE
from gnowsys_ndf.ndf.models import node_collection, triple_collection
from gnowsys_ndf.ndf.views.methods import create_gattribute, create_grelation

####################################################################################################################

SCHEMA_ROOT = os.path.join( os.path.dirname(__file__), "schema_files")

log_list = [] # To hold intermediate error and information messages
log_list.append("\n######### Script run on : " + time.strftime("%c") + " #########\n############################################################\n")

########################################################################################################################


class Command(BaseCommand):
  """This script handles works related to MIS GAPP.
  """
  option_list = BaseCommand.option_list

  user_defined_option_list = (
    make_option('-d', '--setup-data', action='store_true', dest='setup_mis_data', default=False, help='This sets up group(s) with MIS-data.'),
    make_option('-g', '--setup-gapps', action='store_true', dest='setup_gapps', default=False, help='This sets up default GAPPS for group(s).'),
    make_option('-r', '--ren-regYear', action='store_true', dest='ren_regYear', default=False, help='This renames registration_year to registration_date and updates existing value(s), if exists.'),
    make_option('-l', '--link-login-ac', action='store_true', dest='link_login_ac', default=False, help='This renames registration_year to registration_date and updates existing value(s), if exists.'),
  )

  option_list = option_list + user_defined_option_list

  help = "This script handles works related to MIS GAPP."

  def handle(self, *args, **options):
    # Links Author GSystem and Respecive Person's Sub-type GSystem. ------------------------------------
    if options['link_login_ac']:
      try:
        info_message = "\n Links Author GSystem and Respecive Person's Sub-type GSystem.\n"
        log_list.append(info_message)
        info_message = ""
        link_login_ac()

      except Exception as e:
        error_message = "\n LoginLinkError: " + str(e) + " !!!\n"
        log_list.append(error_message)
        pass

      finally:
        if log_list:
          log_list.append("\n ============================================================ End of Iteration ============================================================\n")

          log_file_name = os.path.splitext(os.path.basename(__file__))[0] + ".log"
          log_file_path = os.path.join(SCHEMA_ROOT, log_file_name)

          with open(log_file_path, 'a') as log_file:
            log_file.writelines(log_list)

    # Renames registration_year to registration_date & updates existing value(s) ------------------------------------
    if options['ren_regYear']:
      try:
        info_message = "\n Renames registration_year to registration_date & updates existing value(s).\n"
        log_list.append(info_message)
        info_message = ""
        update_registration_year()

      except Exception as e:
        error_message = "\n RegistrationDateError: " + str(e) + " !!!\n"
        log_list.append(error_message)
        pass

      finally:
        if log_list:
          log_list.append("\n ============================================================ End of Iteration ============================================================\n")

          log_file_name = os.path.splitext(os.path.basename(__file__))[0] + ".log"
          log_file_path = os.path.join(SCHEMA_ROOT, log_file_name)

          with open(log_file_path, 'a') as log_file:
            log_file.writelines(log_list)

    # Setting up default GAPPS for group(s) ----------------------------------------------------------------------------
    if options['setup_gapps']:
      try:
        info_message = "\n Setting up default GAPPS for group(s).\n"
        log_list.append(info_message)
        info_message = ""
        setup_default_gapps()
      except Exception as e:
        print "\n GAPPSSetupError: " + str(e)
        pass
      finally:
        if log_list:
          log_list.append("\n ============================================================ End of Iteration ============================================================\n")

          log_file_name = os.path.splitext(os.path.basename(__file__))[0] + ".log"
          log_file_path = os.path.join(SCHEMA_ROOT, log_file_name)

          with open(log_file_path, 'a') as log_file:
            log_file.writelines(log_list)

    # Setting up group(s) with MIS data --------------------------------------------------------------------------------
    if options['setup_mis_data']:
      try:
        info_message = "\n Setting up group(s) with MIS-data.\n"
        log_list.append(info_message)
        info_message = ""
        setup_mis_data()
      except Exception as e:
        print "\n MISDataError: " + str(e)
        pass
      finally:
        if log_list:
          log_list.append("\n ============================================================ End of Iteration ============================================================\n")

          log_file_name = os.path.splitext(os.path.basename(__file__))[0] + ".log"
          log_file_path = os.path.join(SCHEMA_ROOT, log_file_name)

          with open(log_file_path, 'a') as log_file:
            log_file.writelines(log_list)

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
    if False:
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


def link_login_ac():
  """This function links Author GSystem and Respecive Person's Sub-type GSystem.
  """
  users = User.objects.all()
  has_login_rt = node_collection.one({'_type': "RelationType", 'name': "has_login"})

  for each in users:
    person_node = node_collection.find({'attribute_set.email_id': each.email})
    auth_node = node_collection.one({'_type': "Author", 'email': each.email})
    if person_node.count() <= 0 or auth_node is None:
      error_message = "\n Either person_node or auth_node doesn't exists for given email (" + each.email + ") !!!"
      log_list.append(error_message)
      continue

    for pn in person_node:
      gr_node = create_grelation(pn._id, has_login_rt, auth_node._id)
      info_message = "\n This GRelation created for " + str(gr_node.name) + "."
      log_list.append(info_message)


def update_registration_year():
  '''
  This renames registration_year to registration_date and updates existing value(s), if exists.
  '''

  # Fetch the AttributeType (registration_year) & rename it using update command
  ryat = node_collection.one({'_type': "AttributeType", 'name': "registration_year"})

  if not ryat:
    # It means already updated don't do anything
    ryat = node_collection.one({'_type': "AttributeType", 'name': "registration_date"})
    info_message = "\n Already updated -- " + ryat.name + " (" + str(ryat._id) + ") !\n"
    log_list.append(info_message)
    return

  info_message = "\n Before update: " + str(ryat._id) + " -- " + ryat.name + " -- " + str(ryat["validators"])
  log_list.append(info_message)

  res = node_collection.collection.update({'_id': ryat._id},
                          {'$set': {'name': u"registration_date",
                                    'altnames': u"Date of Registration",
                                    'validators': [u"m/d/Y", u"date_month_day_year", u"MM/DD/YYYY"]
                          }},
                          upsert=False, multi=False
                        )

  if res['n']:
    ryat.reload()
    info_message = "\n After update: " + str(ryat._id) + " -- " + ryat.name + " -- " + str(ryat["validators"]) + "\n"
    log_list.append(info_message)

    # If AttributeType is updated successfully, then look out for any existing value(s)
    # With value as datetime.datetime(2014, 1, 1, 0, 0)
    # If found, replace it with datetime.datetime(2014, 1, 1, 0, 0)

    ry_cur = triple_collection.find({'_type': "GAttribute", 'attribute_type': ryat._id})

    c = ry_cur.count()
    if c:
      info_message = "\n No. of existing value(s) found: " + str(c)
      log_list.append(info_message)

      for each in ry_cur:
        if each.object_value == datetime.datetime(2014, 1, 1, 0, 0):
          d = datetime.datetime(2014, 9, 2, 0, 0)
          res = triple_collection.collection.update({'_id': each._id},
                                  {'$set': {'object_value': d,
                                            'name': each.name.replace("2014-01-01 00:00:00", str(d))
                                  }},
                                  upsert=False, multi=False
                                )
          if res['n']:
            # n = triple_collection.one({'_id': each._id})
            each.reload()
            info_message = "\n Updated: " + each.name#n.name

          else:
            info_message = "\n Not updated: " + each.name + " !!"

          log_list.append(info_message)

    else:
      info_message = "\n No documents exist for update !!\n"
      log_list.append(info_message)

  else:
    error_message = "Something went wrong while updating AttributeType - " + ryat.name + " (" + str(ryat._id) + ")"
    log_list.append(error_message)
    raise Exception(error_message)


def setup_default_gapps():
  '''
  This sets up default GAPPS for group(s).
  '''

  default_gapps_names_list = ["Page", "File", "Forum", "MIS", "Task", "Batch", "Event"]# "Meeting"]
  info_message = "\n Default GAPPS names: " + str(default_gapps_names_list)

  # Fetch GAPPS and populate their document-node in a different list
  default_gapps_list = [] # Will hold document of each corresponding GAPP name from above given list
  meta_type_gapp = node_collection.one({'_type': "MetaType", 'name': META_TYPE[0]})
  info_message += "\n Default GAPPS list: \n"
  for each in default_gapps_names_list:
    gapp_node = node_collection.one({'_type': "GSystemType", 'member_of': meta_type_gapp._id, 'name': each})

    if gapp_node:
      default_gapps_list.append(gapp_node)
      info_message += " " + gapp_node.name + "("+str(gapp_node._id)+")\n"

  log_list.append(info_message)

  # If length of list-of-names & list-of-documents doesn't match throw Exception
  if len(default_gapps_names_list) != len(default_gapps_list):
    error_message = "\n GAPPSSetupError: Few GAPPS not found!!!\n"
    log_list.append(error_message)
    raise Exception(error_message)

  # Fetch AttributeType node - apps_list
  at_apps_list = node_collection.one({'_type': "AttributeType", 'name': "apps_list"})
  if not at_apps_list:
    error_message = "\n GAPPSSetupError: AttributeType (apps_list) doesn't exists.. please create explicitly!!!\n"
    log_list.append(error_message)
    raise Exception(error_message)
  info_message = "\n AttributeType: " + at_apps_list.name + "("+str(at_apps_list._id)+")\n"
  log_list.append(info_message)

  # Fetch MIS_admin group - required for fetching GSystems of College GSystemType
  mis_admin = node_collection.one({'_type': "Group",
                                   '$or': [{'name': {'$regex': u"MIS_admin", '$options': 'i'}},
                                           {'altnames': {'$regex': u"MIS_admin", '$options': 'i'}}],
                                   'group_type': "PRIVATE"
                                  },
                                  {'name': 1}
                                  )
  if not mis_admin:
    error_message = "\n GAPPSSetupError: Group (MIS_admin) doesn't exists.. please check!!!\n"
    log_list.append(error_message)
    raise Exception(error_message)
  info_message = "\n Group: " + mis_admin.name + "("+str(mis_admin._id)+")\n"
  log_list.append(info_message)

  # Fetch GSystems of College GSystemType belonging to MIS_admin group
  college = node_collection.one({'_type': "GSystemType", 'name': u"College"}, {'name': 1})
  if not college:
    error_message = "\n GAPPSSetupError: GSystemType (College) doesn't exists.. please check!!!\n"
    log_list.append(error_message)
    raise Exception(error_message)
  info_message = "\n GSystemType: " + college.name + "("+str(college._id)+")\n"
  log_list.append(info_message)

  college_cur = list(node_collection.find({'_type': "GSystem", 'member_of': college._id, 'group_set': mis_admin._id}))

  for i, each in enumerate(college_cur):
    g = node_collection.one({'_type': "Group", 'name': each.name, 'group_type': "PRIVATE"}, {'name': 1})
    if g:
      info_message = "\n "+str(i+1)+") Setting GAPPS for this college group ("+g.name+" -- "+str(g._id)+")\n"
      log_list.append(info_message)

      is_apps_list = triple_collection.one({'_type': "GAttribute", 'subject': g._id, 'attribute_type': at_apps_list._id})
      if is_apps_list:
        info_message = " Default GAPPs list already exists for Group ("+g.name+" -- "+str(g._id)+"), so overriding it..."
        log_list.append(info_message)
        res = triple_collection.collection.update({'_id': is_apps_list._id}, {'$set': {'object_value': default_gapps_list}}, upsert=False, multi=False)
        if res["n"]:
          is_apps_list.reload()
          info_message = "\n Successfully overridden: " + str(is_apps_list._id) + "\n"
          log_list.append(info_message)
        else:
          info_message = "\n Not overridden: " + str(is_apps_list._id) + "\n"
          log_list.append(info_message)

      else:
        info_message = " Default GAPPs list doesn't exists for Group ("+g.name+" -- "+str(g._id)+"), so creating..."
        log_list.append(info_message)
        ga = create_gattribute(g._id, at_apps_list, default_gapps_list)
        info_message = "\n Successfully created: " + str(ga._id) + "\n"
        log_list.append(info_message)

    else:
      error_message = "\n GAPPSSetupError: This college group ("+each.name+") doesn't exists.. please create explicitly!!!\n"
      log_list.append(error_message)


def setup_mis_data():
  '''
  This sets up group(s) with MIS-data.
  '''
  # Fetch MIS_admin group details
  mis_admin = node_collection.one({'_type': "Group",
                                 '$or': [{'name': {'$regex': u"MIS_admin", '$options': 'i'}},
                                         {'altnames': {'$regex': u"MIS_admin", '$options': 'i'}}],
                                 'group_type': "PRIVATE"
                                },
                                {'name': 1}
                                )
  info_message = "\n mis_admin --"
  info_message += "\n id: " + str(mis_admin._id)
  info_message += "\n name: " + mis_admin.name
  log_list.append(info_message)
  info_message = ""

  # Set groups_name_list with values
  groups_name_list = []
  # groups_name_list = ["Platform Development"]
  # or -----
  college = node_collection.one({'_type': "GSystemType", 'name': u"College"}, {'name': 1})
  college_cur = node_collection.find({'_type': "GSystem", 'member_of': college._id, 'group_set': mis_admin._id}, {'name': 1})

  for each in college_cur:
    groups_name_list.append(each.name)

  def setup_groups(groups_name_list, cur):
    info_message = "\n groups_name_list: " + str(groups_name_list)
    log_list.append(info_message)

    # Creating list of ObjectId(s) of group(s)
    groups_list = [] # Holds ObjectId of groups listed in groups_name_list
    for each in groups_name_list:
      gr = node_collection.one({'_type': "Group", 'name': each, 'group_type': "PRIVATE"}, {'name': 1})
      if gr:
        groups_list.append(gr._id)

    info_message = "\n groups_list: " + str(groups_list)
    log_list.append(info_message)

    # Creating list of ObjectId(s) of GSystem(s) passed in as cur (cursor-object)
    gs_oid_list = []
    info_message = "\n Appending:"
    for each in cur:
      info_message += " " + each.name + ","
      gs_oid_list.append(each._id)

    log_list.append(info_message)

    res = node_collection.collection.update({'_id': {'$in': gs_oid_list}}, {'$addToSet': {'group_set': {'$each': groups_list}}}, upsert=False, multi=True)
    info_message = "\n No. of GSystems updated: " + str(res['n'])
    log_list.append(info_message)

  # Setup Country
  country = node_collection.one({'_type': "GSystemType", 'name': u"Country"}, {'name': 1})
  info_message = "\n\n country: " + str(country._id) + " -- " + country.name
  log_list.append(info_message)
  country_cur = node_collection.find({'_type': "GSystem", 'member_of': country._id, 'group_set': mis_admin._id}, {'name': 1})
  info_message = "\n Countrys found: " + str(country_cur.count())
  log_list.append(info_message)
  setup_groups(groups_name_list, country_cur)
  info_message = "\n Updated Country data sucessfully !\n"
  log_list.append(info_message)

  # Setup State
  state = node_collection.one({'_type': "GSystemType", 'name': u"State"}, {'name': 1})
  info_message = "\n state: " + str(state._id) + " -- " + state.name
  log_list.append(info_message)
  state_cur = node_collection.find({'_type': "GSystem", 'member_of': state._id, 'group_set': mis_admin._id}, {'name': 1})
  info_message = "\n States found: " + str(state_cur.count())
  log_list.append(info_message)
  setup_groups(groups_name_list, state_cur)
  info_message = "\n Updated State data sucessfully !\n"
  log_list.append(info_message)

  # Setup District
  district = node_collection.one({'_type': "GSystemType", 'name': u"District"}, {'name': 1})
  info_message = "\n district: " + str(district._id) + " -- " + district.name
  log_list.append(info_message)
  district_cur = node_collection.find({'_type': "GSystem", 'member_of': district._id, 'group_set': mis_admin._id}, {'name': 1})
  info_message = "\n Districts found: " + str(district_cur.count())
  log_list.append(info_message)
  setup_groups(groups_name_list, district_cur)
  info_message = "\n Updated District data sucessfully !\n"
  log_list.append(info_message)

  # Setup University
  university = node_collection.one({'_type': "GSystemType", 'name': u"University"}, {'name': 1})
  info_message = "\n university: " + str(university._id) + " -- " + university.name
  log_list.append(info_message)
  university_cur = node_collection.find({'_type': "GSystem", 'member_of': university._id, 'group_set': mis_admin._id}, {'name': 1})
  info_message = "\n Universitys found: " + str(university_cur.count())
  log_list.append(info_message)
  setup_groups(groups_name_list, university_cur)
  info_message = "\n Updated University data sucessfully !\n"
  log_list.append(info_message)

  # Setup College
  college = node_collection.one({'_type': "GSystemType", 'name': u"College"}, {'name': 1})
  info_message = "\n college: " + str(college._id) + " -- " + college.name
  log_list.append(info_message)
  college_cur = node_collection.find({'_type': "GSystem", 'member_of': college._id, 'group_set': mis_admin._id}, {'name': 1})
  info_message = "\n Colleges found: " + str(college_cur.count())
  log_list.append(info_message)
  setup_groups(groups_name_list, college_cur)
  info_message = "\n Updated College data sucessfully !\n"
  log_list.append(info_message)

  # Setup Caste
  caste = node_collection.one({'_type': "GSystemType", 'name': u"Caste"}, {'name': 1})
  info_message = "\n caste: " + str(caste._id) + " -- " + caste.name
  log_list.append(info_message)
  caste_cur = node_collection.find({'_type': "GSystem", 'member_of': caste._id, 'group_set': mis_admin._id}, {'name': 1})
  info_message = "\n Castes found: " + str(caste_cur.count())
  log_list.append(info_message)
  setup_groups(groups_name_list, caste_cur)
  info_message = "\n Updated Caste data sucessfully !\n"
  log_list.append(info_message)

  # Setup NUSSD Course
  nussd_course = node_collection.one({'_type': "GSystemType", 'name': u"NUSSD Course"}, {'name': 1})
  info_message = "\n nussd_course: " + str(nussd_course._id) + " -- " + nussd_course.name
  log_list.append(info_message)
  nussd_course_cur = node_collection.find({'_type': "GSystem", 'member_of': nussd_course._id, 'group_set': mis_admin._id}, {'name': 1})
  info_message = "\n Nussd_courses found: " + str(nussd_course_cur.count())
  log_list.append(info_message)
  setup_groups(groups_name_list, nussd_course_cur)
  info_message = "\n Updated NUSSD Course data sucessfully !\n"
  log_list.append(info_message)


def create_college_group():
  """
  Creates private group for each college; and appends glab's (superuser) user-id as a creator for each of them.

  Arguments: Empty

  Returns: Nothing
  """

  collegeid = node_collection.one({'_type': "GSystemType", 'name': "College"})._id
  college_cur = node_collection.find({'_type': "GSystem", 'member_of': collegeid})
  groupid = node_collection.one({'_type': "GSystemType", 'name': "Group"})._id
  glab_created_by = node_collection.one({'_type': "Author", 'name': "glab"}).created_by

  for n in college_cur:
    college_exists = node_collection.one({'_type': "Group", 'name': n.name}, {'_id': 1, 'name': 1, 'group_type': 1})

    if college_exists:
      # If given college is found, don't create it again and pass the iteration
      info_message = "\n CollegeGroupAlreadyExists: Group ("+college_exists.group_type+") for this college ("+college_exists.name+") already exists with this ObjectId ("+str(college_exists._id)+") ! \n"
      log_list.append(info_message)
      continue

    gfc = node_collection.collection.Group()
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
    system_type_id = node_collection.one({'_type': "GSystemType", 'name': system_type})._id
    system_type_cur = node_collection.find({'_type': "GSystem", 'member_of': system_type_id})

    for n in system_type_cur:
      possible_relations = n.get_possible_relations(n.member_of)

      if system_type == "Student":
        colg_list = possible_relations["student_belongs_to_college"]["subject_or_right_subject_list"]
      else:
        colg_list = possible_relations["trainer_of_college"]["subject_or_right_subject_list"]

      group_set_updated = False

      for colg in colg_list:
        colg_group_id = node_collection.one({'_type': "Group", 'group_type': "PRIVATE", 'name': colg.name})._id
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
