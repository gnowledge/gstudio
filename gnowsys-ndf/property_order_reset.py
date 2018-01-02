from gnowsys_ndf.ndf.models import *

# ================================================================== Tabs for Event

el_name = ["name", "start_time", "end_time", "is_bigbluebutton" , "event_coordinator", "open_event", "has_attendees", "location", "content_org", "event_status", "tags"]
el = []
for i, n in enumerate(el_name):
  old_n = n
  n = node_collection.one({'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': n})
  if n:
    print "\n ", (i+1), " ", n._id, " -- ", n.name, " -- ", n.property_order
    el.append(n._id)
  else:
    print "\n ", (i+1), " ", old_n
    el.append(old_n)

epo = [["Basic", el]]
event = node_collection.one({'_type': "GSystemType", 'name': "Event"})
node_collection.collection.update({'_id': event._id}, {'$set': {'property_order': epo}}, upsert=False, multi=False)
event.reload()

from gnowsys_ndf.ndf.views.methods import get_property_order_with_value
event_cur = node_collection.find({'type_of': event._id})
for n in event_cur:
  node_collection.collection.update({'_id': n._id}, {'$set': {'property_order': []}}, upsert=False, multi=False)
  print "\n ", n._id, " -- ", n.name, " -- ", n.property_order
  print "\n ", n._id, " -- ", n.name, " -- ", get_property_order_with_value(n)
  n.reload()
  print "\n ", n._id, " -- ", n.name, " -- ", n.property_order


"""
# ================================================================== Tabs for StudentCourseEnrollment

sce_name = ["nussd_course_type", "start_enroll", "end_enroll"]
sce = []
for i, n in enumerate(sce_name):
  old_n = n
  n = node_collection.one({'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': n})
  if n:
    print "\n ", (i+1), " ", n._id, " -- ", n.name, " -- ", n.property_order
    sce.append(n._id)
  else:
    print "\n ", (i+1), " ", old_n
    sce.append(old_n)

scepo = [["Enroll", sce]]
sce_gst = node_collection.one({'_type': "GSystemType", 'name': "StudentCourseEnrollment"})
node_collection.collection.update({'_id': sce_gst._id}, {'$set': {'property_order': scepo}}, upsert=False, multi=False)
sce_gst.reload()


# ================================================================== Tabs for Classroom Session & Exam

cel_name = ["name", "start_time", "end_time", "event_organised_by", "event_coordinator", "has_attendees", "location", "content_org", "tags", "nussd_course_type", "session_of", "event_has_batch", "event_status"]
cel = []
for i, n in enumerate(cel_name):
  old_n = n
  n = node_collection.one({'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': n})
  if n:
    print "\n ", (i+1), " ", n._id, " -- ", n.name, " -- ", n.property_order
    cel.append(n._id)
  else:
    print "\n ", (i+1), " ", old_n
    cel.append(old_n)

sepo = [["Basic", cel]]
subevents = node_collection.find({'_type': "GSystemType", 'name': {'$in': ["Classroom Session", "Exam"]}})
sel = []
for each in subevents:
  if each._id not in sel:
    sel.append(each._id)
node_collection.collection.update({'_id': {'$in': sel}}, {'$set': {'property_order': sepo}}, upsert=False, multi=True)

from gnowsys_ndf.ndf.views.methods import get_property_order_with_value
subevents.rewind()
for n in subevents:
  print "\n ", n._id, " -- ", n.name, " -- ", get_property_order_with_value(n)

# ======================================================================== Tabs for NUSSD Course

ncl_name = ["nussd_course_type", "name", "course_code", "tags", "theory_credit", "field_work_credit", "qualifying_attendence", "evaluation_type", "min_marks", "max_marks", "content_org"]
ncl = []
for i, n in enumerate(ncl_name):
  old_n = n
  n = node_collection.one({'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': n})
  if n:
    print "\n ", (i+1), " ", n._id, " -- ", n.name, " -- ", n.property_order
    ncl.append(n._id)
  else:
    print "\n ", (i+1), " ", old_n
    ncl.append(old_n)

nrl_name = ["mast_tr_qualifications", "voln_tr_qualifications"]
nrl = []
for i, n in enumerate(nrl_name):
  n = node_collection.one({'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': n})
  print "\n ", (i+1), " ", n._id, " -- ", n.name, " -- ", n.property_order
  nrl.append(n._id)

ncpo = [["Basic", ncl], ["Requirements", nrl]]

nussd_course = node_collection.one({'_type': "GSystemType", 'name': "NUSSD Course"})
node_collection.collection.update({'_id': nussd_course._id}, {'$set': {'property_order': ncpo}}, upsert=False, multi=False)
nussd_course.reload()
"""
# ================================================================== Tabs for "CourseSection"

csl_name = ["name"]
csl = []
for i, n in enumerate(csl_name):
  old_n = n
  n = node_collection.one({'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': n})
  if n:
    print "\n ", (i+1), " ", n._id, " -- ", n.name, " -- ", n.property_order
    csl.append(n._id)
  else:
    print "\n ", (i+1), " ", old_n
    csl.append(old_n)

cspo = [["Basic", csl]]
cs = node_collection.one({'_type': "GSystemType", 'name': "CourseSection"})
node_collection.collection.update({'_id': cs._id}, {'$set': {'property_order': cspo}}, upsert=False, multi=False)
cs.reload()

# ================================================================== Tabs for "CourseSubSection"

cssl_name = ["name", "course_structure_minutes", "course_structure_assignment", "course_structure_assessment", "min_marks", "max_marks"]
cssl = []
for i, n in enumerate(cssl_name):
  old_n = n
  n = node_collection.one({'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': n})
  if n:
    print "\n ", (i+1), " ", n._id, " -- ", n.name, " -- ", n.property_order
    cssl.append(n._id)
  else:
    print "\n ", (i+1), " ", old_n
    cssl.append(old_n)

csspo = [["Basic", cssl]]
css = node_collection.one({'_type': "GSystemType", 'name': "CourseSubSection"})
node_collection.collection.update({'_id': css._id}, {'$set': {'property_order': csspo}}, upsert=False, multi=False)
css.reload()

"""
# ======================================================================== Additional Tab for Announced Course

# acl_name = ["nussd_course_type", "start_time", "end_time", "start_enroll", "end_enroll", "announced_for", "acourse_for_college", "ann_course_closure"]
acl_name = ["nussd_course_type", "start_time", "end_time", "announced_for", "acourse_for_college", "ann_course_closure"]
acl = []
for i, n in enumerate(acl_name):
  n = node_collection.one({'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': n})
  print "\n ", (i+1), " ", n._id, " -- ", n.name, " -- ", n.property_order
  acl.append(n._id)

acpo = ["Basic", acl]

announced_course = node_collection.one({'_type': "GSystemType", 'name': "Announced Course"})
node_collection.collection.update({'_id': announced_course._id}, {'$set': {'property_order': [acpo]}}, upsert=False, multi=False)
announced_course.reload()

# ==================================================================== Tabs for Organization

ol_name = ["name", "tags", "location", "email_id", "mobile_number", "alternate_number", "content_org"]
ol = []
for i, n in enumerate(ol_name):
  old_n = n
  n = node_collection.one({'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': n})
  if n:
    print "\n ", (i+1), " ", n._id, " -- ", n.name, " -- ", n.property_order
    ol.append(n._id)
  else:
    print "\n ", (i+1), " ", old_n
    ol.append(old_n)

al_name = ["organization_belongs_to_state", "organization_belongs_to_district", "house_street", "village", "taluka", "town_city", "pin_code"]
al = []
for i, n in enumerate(al_name):
  n = node_collection.one({'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': n})
  print "\n ", (i+1), " ", n._id, " -- ", n.name, " -- ", n.property_order
  al.append(n._id)

ppo = [["Organizational", ol], ["Address", al]]

organization = node_collection.one({'_type': "GSystemType", 'name': "Organization"})
node_collection.collection.update({'_id': organization._id}, {'$set': {'property_order': ppo}}, upsert=False, multi=False)
organization.reload()

organization_cur = node_collection.find({'type_of': organization._id})
from gnowsys_ndf.ndf.views.methods import get_property_order_with_value
for n in organization_cur:
  node_collection.collection.update({'_id': n._id}, {'$set': {'property_order': []}}, upsert=False, multi=False)
  n.reload()
  print "\n ", n._id, " -- ", n.name, " -- ", get_property_order_with_value(n)

# ======================================================================== Additional Tab for University

cl_name = ["affiliated_college"]
cl = []
for i, n in enumerate(cl_name):
  n = node_collection.one({'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': n})
  print "\n ", (i+1), " ", n._id, " -- ", n.name, " -- ", n.property_order
  cl.append(n._id)

ucl = ["College", cl]

university = node_collection.one({'_type': "GSystemType", 'name': "University"})
node_collection.collection.update({'_id': university._id}, {'$addToSet': {'property_order': ucl}}, upsert=False, multi=False)
university.reload()

# ==================================================================== Tabs for College

ol_name = ["name", "enrollment_code", "tags", "location", "email_id", "mobile_number", "alternate_number", "content_org"]
ol = []
for i, n in enumerate(ol_name):
  old_n = n
  n = node_collection.one({'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': n})
  if n:
    print "\n ", (i+1), " ", n._id, " -- ", n.name, " -- ", n.property_order
    ol.append(n._id)
  else:
    print "\n ", (i+1), " ", old_n
    ol.append(old_n)

al_name = ["organization_belongs_to_state", "organization_belongs_to_district", "house_street", "village", "taluka", "town_city", "pin_code"]
al = []
for i, n in enumerate(al_name):
  n = node_collection.one({'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': n})
  print "\n ", (i+1), " ", n._id, " -- ", n.name, " -- ", n.property_order
  al.append(n._id)

ppo = [["Organizational", ol], ["Address", al]]

college = node_collection.one({'_type': "GSystemType", 'name': "College"})
node_collection.collection.update({'_id': college._id}, {'$set': {'property_order': ppo}}, upsert=False, multi=False)
college.reload()

# ==================================================================== Tabs for Person

pl_name = ["first_name", "middle_name", "last_name", "gender", "dob", "religion", "email_id", "languages_known", "signature", "user_photo", "mobile_number", "alternate_number"]
pl = []
for i, n in enumerate(pl_name):
  n = node_collection.one({'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': n})
  print "\n ", (i+1), " ", n._id, " -- ", n.name, " -- ", n.property_order
  pl.append(n._id)

al_name = ["person_belongs_to_state", "person_belongs_to_district", "house_street", "village", "taluka", "town_city", "pin_code"]
al = []
for i, n in enumerate(al_name):
  n = node_collection.one({'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': n})
  print "\n ", (i+1), " ", n._id, " -- ", n.name, " -- ", n.property_order
  al.append(n._id)

ppo = [["Personal", pl], ["Address", al]]

person = node_collection.one({'_type': "GSystemType", 'name': "Person"})
node_collection.collection.update({'_id': person._id}, {'$set': {'property_order': ppo}}, upsert=False, multi=False)
person.reload()

person_cur = node_collection.find({'type_of': person._id})
from gnowsys_ndf.ndf.views.methods import get_property_order_with_value
for n in person_cur:
  node_collection.collection.update({'_id': n._id}, {'$set': {'property_order': []}}, upsert=False, multi=False)
  n.reload()
  print "\n ", n._id, " -- ", n.name, " -- ", get_property_order_with_value(n)

# ======================================================================== Tabs for Student

pl_name = ["first_name", "middle_name", "last_name", "gender", "dob", "religion", "email_id", "languages_known", "student_of_caste_category", "signature", "user_photo", "mobile_number", "alternate_number", "aadhar_id"]
pl = []
for i, n in enumerate(pl_name):
  n = node_collection.one({'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': n})
  print "\n ", (i+1), " ", n._id, " -- ", n.name, " -- ", n.property_order
  pl.append(n._id)

al_name = ["person_belongs_to_state", "person_belongs_to_district", "house_street", "village", "taluka", "town_city", "pin_code"]
al = []
for i, n in enumerate(al_name):
  n = node_collection.one({'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': n})
  print "\n ", (i+1), " ", n._id, " -- ", n.name, " -- ", n.property_order
  al.append(n._id)

ppo = [["Personal", pl], ["Address", al]]

esl_name = ["12_passing_year", "12_passing_certificate", "degree_name", "degree_specialization", "degree_year", "student_belongs_to_college", "college_enroll_num", "is_nss_registered", "registration_date"]
esl = []
for i, n in enumerate(esl_name):
  n = node_collection.one({'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': n})
  print "\n ", (i+1), " ", n._id, " -- ", n.name, " -- ", n.property_order
  esl.append(n._id)

espo = ["Educational", esl]

student = node_collection.one({'_type': "GSystemType", 'name': "Student"})
node_collection.collection.update({'_id': student._id}, {'$set': {'property_order': ppo}}, upsert=False, multi=False)
node_collection.collection.update({'_id': student._id}, {'$addToSet': {'property_order': espo}}, upsert=False, multi=False)
student.reload()

# ================================================================================== Additional Tab for Voluntary Teacher

# ovl_name = ["trainer_of_course", "voln_tr_qualifications", "trainer_of_college"]
ovl_name = ["trainer_teaches_course_in_college", "voln_tr_qualifications"]
ovl = []
for i, n in enumerate(ovl_name):
  n = node_collection.one({'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': n})
  print "\n ", (i+1), " ", n._id, " -- ", n.name, " -- ", n.property_order
  ovl.append(n._id)

ovpo = ["Course", ovl]
print ovpo

evl_name = ["degree_name", "degree_specialization", "degree_passing_year", "other_qualifications"]
evl = []
for i, n in enumerate(evl_name):
  n = node_collection.one({'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': n})
  print "\n ", (i+1), " ", n._id, " -- ", n.name, " -- ", n.property_order
  evl.append(n._id)

evpo = ["Educational", evl]

pvl_name = ["key_skills", "profession", "designation", "work_exp"] #, "is_tot_attended", "tot_when", "nxt_mon_sch"]
pvl = []
for i, n in enumerate(pvl_name):
  n = node_collection.one({'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': n})
  print "\n ", (i+1), " ", n._id, " -- ", n.name, " -- ", n.property_order
  pvl.append(n._id)

pvpo = ["Professional", pvl]

vt = node_collection.one({'_type': "GSystemType", 'name': "Voluntary Teacher"})

# node_collection.collection.update({'_id': vt._id}, {'$set': {'property_order': []}}, upsert=False, multi=False)
node_collection.collection.update({'_id': vt._id}, {'$addToSet': {'property_order': ovpo}}, upsert=False, multi=False)
node_collection.collection.update({'_id': vt._id}, {'$addToSet': {'property_order': evpo}}, upsert=False, multi=False)
node_collection.collection.update({'_id': vt._id}, {'$addToSet': {'property_order': pvpo}}, upsert=False, multi=False)

vt.reload()

# ================================================================================== Additional Tab for Master Trainer

ovl_name = ["master_trainer_of_course", "mast_tr_qualifications", "master_trainer_of_university"]
ovl = []
for i, n in enumerate(ovl_name):
  n = node_collection.one({'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': n})
  print "\n ", (i+1), " ", n._id, " -- ", n.name, " -- ", n.property_order
  ovl.append(n._id)

ovpo = ["Course", ovl]

evl_name = ["degree_name", "degree_specialization", "degree_passing_year", "other_qualifications"]
evl = []
for i, n in enumerate(evl_name):
  n = node_collection.one({'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': n})
  print "\n ", (i+1), " ", n._id, " -- ", n.name, " -- ", n.property_order
  evl.append(n._id)

evpo = ["Educational", evl]

pvl_name = ["key_skills", "profession", "designation", "work_exp"] #, "is_tot_attended", "tot_when", "nxt_mon_sch"]
pvl = []
for i, n in enumerate(pvl_name):
  n = node_collection.one({'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': n})
  print "\n ", (i+1), " ", n._id, " -- ", n.name, " -- ", n.property_order
  pvl.append(n._id)

pvpo = ["Professional", pvl]

mt = node_collection.one({'_type': "GSystemType", 'name': "Master Trainer"})

node_collection.collection.update({'_id': mt._id}, {'$addToSet': {'property_order': ovpo}}, upsert=False, multi=False)
node_collection.collection.update({'_id': mt._id}, {'$addToSet': {'property_order': evpo}}, upsert=False, multi=False)
node_collection.collection.update({'_id': mt._id}, {'$addToSet': {'property_order': pvpo}}, upsert=False, multi=False)

mt.reload()

# ======================================================================== Additional Tab for Program Officer

pol_name = ["officer_incharge_of"]
pol = []
for i, n in enumerate(pol_name):
  n = node_collection.one({'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': n})
  print "\n ", (i+1), " ", n._id, " -- ", n.name, " -- ", n.property_order
  pol.append(n._id)

popo = ["Other", pol]

program_officer = node_collection.one({'_type': "GSystemType", 'name': "Program Officer"})
node_collection.collection.update({'_id': program_officer._id}, {'$addToSet': {'property_order': popo}}, upsert=False, multi=False)
program_officer.reload()

# ================================================================================== Additional Tab for Faculty Coordinator

ofl_name = ["faculty_incharge_of_university", "faculty_incharge_of_college"]
ofl = []
for i, n in enumerate(ofl_name):
  n = node_collection.one({'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': n})
  print "\n ", (i+1), " ", n._id, " -- ", n.name, " -- ", n.property_order
  ofl.append(n._id)

ofpo = ["Other", ofl]

fc = node_collection.one({'_type': "GSystemType", 'name': "Faculty Coordinator"})
node_collection.collection.update({'_id': fc._id}, {'$addToSet': {'property_order': ofpo}}, upsert=False, multi=False)
fc.reload()

# ================================================================================== Additional Tab for Course Developer

ocl_name = ["developer_of_course"]
ocl = []
for i, n in enumerate(ocl_name):
  n = node_collection.one({'_type': {'$in': ["AttributeType", "RelationType"]}, 'name': n})
  print "\n ", (i+1), " ", n._id, " -- ", n.name, " -- ", n.property_order
  ocl.append(n._id)

ocpo = ["Other", ocl]

cd = node_collection.one({'_type': "GSystemType", 'name': "Course Developer"})
node_collection.collection.update({'_id': cd._id}, {'$addToSet': {'property_order': ocpo}}, upsert=False, multi=False)
cd.reload()
"""
