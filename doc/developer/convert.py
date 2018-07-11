import os
import subprocess
from lxml import etree

folder = "./exportworking/"


def create_skeleton():
	if not os.path.exists(folder+ "activities"):
		os.mkdir(folder+"activities")
	if not os.path.exists(folder+ "course"):
		os.mkdir(folder+"course")
	if not os.path.exists(folder+ "files"):
		os.mkdir(folder+"files")
	if not os.path.exists(folder+ "sections"):
		os.mkdir(folder+"sections")


def generate_dummy_files():
	completion_xml = open(folder+"completion.xml","w")
	completion_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n<course_completion>\n</course_completion>')
	completion_xml.close()

	gradebook_xml = open(folder+"gradebook.xml","w")
	gradebook_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n<gradebook>\n</gradebook>')
	gradebook_xml.close()

	grade_history_xml = open(folder + "grade_history.xml", "w")
	grade_history_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n<grade_history>\n<grade_grades>\n</grade_grades>\n</grade_history>')
	grade_history_xml.close()

	groups_xml = open(folder + "groups.xml", "w")
	groups_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n<groups>\n<groupings>\n</groupings>\n</groups>')
	groups_xml.close()

	outcomes_xml = open(folder + "outcomes.xml", "w")
	outcomes_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n<outcomes_definition>\n</outcomes_definition>')
	outcomes_xml.close()

	questions_xml = open(folder + "questions.xml", "w")
	questions_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n<question_categories>\n</question_categories>')
	questions_xml.close()

	roles_xml = open(folder + "roles.xml", "w")
	roles_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n<roles_definition>\n</roles_definition>')
	roles_xml.close()

	scales_xml = open(folder + "scales.xml", "w")
	scales_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n<scales_definition>\n</scales_definition>')
	scales_xml.close()

def generate_moodle_backup_file(course_id,full_name,short_name):

	root = etree.Element("moodle_backup")
	info = etree.SubElement(root, "information")
	name = etree.SubElement(info, "name")
	name.text = full_name

	moodle_version = etree.SubElement(info, "moodle_version")
	moodle_version.text = '2017111302'

	moodle_release = etree.SubElement(info, "moodle_release")
	moodle_release.text = '3.4.2 (Build: 20180319)'

	backup_version = etree.SubElement(info, "backup_version")
	backup_version.text = '2017111300'

	backup_release = etree.SubElement(info, "backup_release")
	backup_release.text = '3.4'

	backup_date = etree.SubElement(info, "backup_date")
	backup_date.text = '1523717039'	#TODO: ADD CURRENT DATE

	mnet_remoteusers = etree.SubElement(info, "mnet_remoteusers")
	mnet_remoteusers.text = '0'

	include_files = etree.SubElement(info, "include_files")
	include_files.text = '1'

	include_file_references_to_external_content = etree.SubElement(info, "include_file_references_to_external_content")
	include_file_references_to_external_content.text = '0'

	original_wwwroot = etree.SubElement(info, "original_wwwroot")
	original_wwwroot.text = ''

	original_site_identifier_hash = etree.SubElement(info, "original_site_identifier_hash")
	original_site_identifier_hash.text = ''

	original_course_id = etree.SubElement(info, "original_course_id")
	original_course_id.text = '3' #hardcoded

	original_course_format = etree.SubElement(info, "original_course_format")
	original_course_format.text = 'topics'

	original_course_fullname = etree.SubElement(info, "original_course_fullname")
	original_course_fullname.text = full_name

	original_course_shortname = etree.SubElement(info, "original_course_shortname")
	original_course_shortname.text = short_name

	original_course_startdate = etree.SubElement(info, "original_course_startdate")
	original_course_startdate.text = '1523505600'
	
	original_course_enddate = etree.SubElement(info, "original_course_enddate")
	original_course_enddate.text = '1555041600'

	original_course_contextid = etree.SubElement(info, "original_course_contextid")
	original_course_contextid.text = '40'

	original_system_contextid = etree.SubElement(info, "original_system_contextid")
	original_system_contextid.text = '1'

	details = etree.SubElement(info, "details")
	
	detail = etree.SubElement(details, "detail")
	detail.set('backup_id','0')

	type_ = etree.SubElement(detail, "type")
	type_.text = 'course'

	format_ = etree.SubElement(detail, "format")
	format_.text = 'moodle2'

	interactive = etree.SubElement(detail, "interactive")
	interactive.text = '1'

	mode = etree.SubElement(detail, "mode")
	mode.text = '30'

	execution = etree.SubElement(detail, "execution")
	execution.text = '1'

	executiontime = etree.SubElement(detail, "executiontime")
	executiontime.text = '0'

	contents =  etree.SubElement(info, "contents")
	activities = etree.SubElement(contents, "activities")

	activity = etree.SubElement(activities, "activity")

	module_id = etree.SubElement(activity, "moduleid")
	module_id.text = '1' #TODO:Generate IDs

	section_id = etree.SubElement(activity, "sectionid")
	section_id.text = '1'

	module_name = etree.SubElement(activity, "modulename")
	module_name.text = 'resource'

	title = etree.SubElement(activity, "title")
	title.text = full_name

	directory = etree.SubElement(activity, "directory")
	directory.text = 'activities/resource_'+module_id.text

	sections = etree.SubElement(contents, "sections")

	section = etree.SubElement(sections, "section")

	section_id = etree.SubElement(section, "sectionid")
	section_id.text = '1'

	title = etree.SubElement(section, "title")
	title.text = 'Epub uploaded'

	directory = etree.SubElement(section, "directory")
	directory.text = 'sections/section_'+section_id.text	

	course = etree.SubElement(contents, "course")
	
	ccourse_id = etree.SubElement(course, "courseid")
	ccourse_id.text = course_id

	title = etree.SubElement(course, "title")
	title.text = short_name

	directory = etree.SubElement(course, "directory")
	directory.text = 'course'


	settings = etree.SubElement(info, "settings")

	setting =  etree.SubElement(settings, "setting")

	level = etree.SubElement(setting, "level")
	level.text = 'root'

	name = etree.SubElement(setting, "name")
	name.text = 'filename'

	value = etree.SubElement(setting,"value") 
	value.text = 'ExportWorking.mbz'			#TODO

	parts = ["users","anonymize","role_assignments","activities","blocks","filters","comments","badges","calendarevents","userscompletion","logs","grade_histories","questionbank","groups","competencies"]

	for i in parts:
		setting = etree.SubElement(settings,"setting")
		level = etree.SubElement(setting, "level")
		level.text = 'root'

		name = etree.SubElement(setting,"name")
		name.text = i

		value = etree.SubElement(setting,"value")
		value.text = '1' 


	setting = etree.SubElement(settings,"setting")

	level = etree.SubElement(setting, "level")
	level.text = 'section'

	section = etree.SubElement(setting, "section")
	section.text = 'section_1'

	name = etree.SubElement(setting,"name")
	name.text = 'section_1_included'

	value = etree.SubElement(setting,"value")
	value.text = '1'


	setting = etree.SubElement(settings,"setting")

	level = etree.SubElement(setting, "level")
	level.text = 'section'

	section = etree.SubElement(setting, "section")
	section.text = 'section_1'

	name = etree.SubElement(setting,"name")
	name.text = 'section_1_userinfo'

	value = etree.SubElement(setting,"value")
	value.text = '0'


	setting = etree.SubElement(settings,"setting")

	level = etree.SubElement(setting, "level")
	level.text = 'activity'

	activity = etree.SubElement(setting, "activity")
	activity.text = 'resource_1'

	name = etree.SubElement(setting,"name")
	name.text = 'resource_1_included'

	value = etree.SubElement(setting,"value")
	value.text = '1'

	setting = etree.SubElement(settings,"setting")

	level = etree.SubElement(setting, "level")
	level.text = 'activity'

	activity = etree.SubElement(setting, "activity")
	activity.text = 'resource_1'

	name = etree.SubElement(setting,"name")
	name.text = 'resource_1_userinfo'

	value = etree.SubElement(setting,"value")
	value.text = '0'

	backup_file = open(folder+ "moodle_backup.xml","wb")
	backup_file.write(etree.tostring(root,xml_declaration=True,encoding='UTF-8',pretty_print=True).replace(b"'", b'"'))
	backup_file.close();

def fill_sections_folder(section_id,sname,ssummary):

	if not os.path.exists(folder+ "sections/section_"+section_id): #hardcoded
		os.mkdir(folder+"sections/section_"+section_id)

	info_ref = open(folder + "sections/section_"+section_id+"/inforef.xml","w")
	info_ref.write('<?xml version="1.0" encoding="UTF-8"?>\n<inforef>\n</inforef>')

	root = etree.Element("section")
	root.set('id',section_id)

	number = etree.SubElement(root, "number")
	number.text = '1'

	name = etree.SubElement(root, "name")
	name.text = sname

	summary = etree.SubElement(root, "summary")
	summary.text = ssummary

	summary_format = etree.SubElement(root, "summaryformat")
	summary_format.text = '1'

	sequence = etree.SubElement(root, "sequence")
	sequence.text = '1'

	visible = etree.SubElement(root, "visible")
	visible.text = '1'

	availabilityjson = etree.SubElement(root, "availabilityjson")
	availabilityjson.text = '{"op":"&","c":[],"showc":[]}'

	timemodified = etree.SubElement(root, "timemodified")
	timemodified.text = '1523491174' #TODO


	section_file = open(folder+ "sections/section_"+section_id+"/section.xml","wb")
	section_file.write(etree.tostring(root,xml_declaration=True,encoding='UTF-8',pretty_print=True).replace(b"'", b'"'))
	section_file.close()




def fill_course_folder(course_id,context_id,full_name,short_name,csummary):
	calendar_xml = open(folder+"course/calendar.xml", "w")
	calendar_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n<events>\n</events>')
	calendar_xml.close()

	competencies_xml = open(folder+"course/competencies.xml", "w")
	competencies_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n<course_competencies>\n  <competencies>\n  </competencies>\n  <user_competencies>\n  </user_competencies>\n</course_competencies>')
	competencies_xml.close()

	completion_default_xml = open(folder+"course/completiondefault.xml", "w")
	completion_default_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n<course_completion_defaults>\n</course_completion_defaults>')
	completion_default_xml.close()

	#course_xml = open(folder + "course/course.xml", "w")
	#course_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n<course_completion_defaults>\n</course_completion_defaults>')
	#course_xml.close()

	filters_xml = open(folder+"course/filters.xml", "w")
	filters_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n<filters>\n  <filter_actives>\n  </filter_actives>\n  <filter_configs>\n  </filter_configs>\n</filters>')
	filters_xml.close()

	inforef_xml = open(folder+ "course/inforef.xml", "w")
	inforef_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n<inforef></inforef>')
	inforef_xml.close()

	roles_xml = open(folder+ "course/roles.xml", "w")
	roles_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n<roles>\n  <role_overrides>\n  </role_overrides>\n  <role_assignments>\n  </role_assignments>\n</roles>')
	roles_xml.close()

	root = etree.Element("course")
	root.set('id',course_id)
	root.set('contextid',context_id)

	dicti = {'shortname': short_name,
			'fullname': full_name,
			'idnumber': '',
			'summary': csummary,
			'summaryformat':'1',
			'format':'topics',
			'showgrades':'1',
			'newsitems':'1',
			'startdate':'1523505600',
			'enddate':'1555041600',
			'marker':'0',
			'maxbytes':'0',
			'legacyfiles':'0',
			'showreports':'0',
			'visible':'1',
			'groupmode':'0',
			'groupmodeforce':'0',
			'defaultgroupingid':'0',
			'lang':'',
			'theme':'',
			'timecreated':'1523491078',
			'timemodified':'1523712920',
			'requested':'0',
			'enablecompletion':'1',
			'completionnotify':'0',
			'hiddensections':'0',
			'coursedisplay':'0',
			'category':'',
			'tags':''} 

	for key,value in dicti.items():

		temp = etree.SubElement(root, key)
		temp.text = value

	course_file = open(folder+ "course/course.xml","wb")
	course_file.write(etree.tostring(root,xml_declaration=True,encoding='UTF-8',pretty_print=True).replace(b"'", b'"'))
	course_file.close()


def fill_activities_folder(type1, activity_id, section_id):

	if not os.path.exists(folder+ "activities/"+type1+"_"+activity_id): #hardcoded
		os.mkdir(folder+ "activities/"+type1+"_"+activity_id)

	current_path = folder+ "activities/"+type1+"_"+activity_id

	calender_xml = open(current_path+"/calendar.xml", "w")
	calender_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n<events>\n</events>')
	calender_xml.close()

	competencies_xml = open(current_path+"/competencies.xml", "w")
	competencies_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n<course_competencies>\n  <competencies>\n  </competencies>\n  <user_competencies>\n  </user_competencies>\n</course_competencies>')
	competencies_xml.close()

	filters_xml = open(current_path+"/filters.xml", "w")
	filters_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n<filters>\n  <filter_actives>\n  </filter_actives>\n  <filter_configs>\n  </filter_configs>\n</filters>')
	filters_xml.close()

	grade_history_xml = open(current_path+"/grade_history.xml", "w")
	grade_history_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n<grade_history>\n<grade_grades>\n</grade_grades>\n</grade_history>')
	grade_history_xml.close()

	grades_xml = open(current_path+"/grades.xml", "w")
	grades_xml.write('<?xml version="1.0" encoding="UTF-8"?><activity_gradebook><grade_items></grade_items><grade_letters></grade_letters></activity_gradebook>')
	grades_xml.close()

	roles_xml = open(current_path+"/roles.xml", "w")
	roles_xml.write('<?xml version="1.0" encoding="UTF-8"?>\n<roles>\n  <role_overrides>\n  </role_overrides>\n  <role_assignments>\n  </role_assignments>\n</roles>')
	roles_xml.close()

	#Time to make inforef

	root = etree.Element("inforef")
	fileref = etree.SubElement(root,"fileref")
	file = etree.SubElement(fileref,"file")

	file_ids = ['100', '101']	#Add for more file ids

	for i in file_ids:
		file1 = etree.SubElement(fileref,"file")
		id_ = etree.SubElement(file1, "id")
		id_.text = i

	inforef_file = open(folder+ "activities/"+type1+"_"+activity_id+"/inforef.xml","wb")
	inforef_file.write(etree.tostring(root,xml_declaration=True,encoding='UTF-8',pretty_print=True).replace(b"'", b'"'))
	inforef_file.close()

	#Time to make module.xml


	root = etree.Element("module")
	root.set('id',activity_id)
	root.set('version','2017111300')

	module_dic = {'modulename':type1,
					'sectionid':section_id,
					'sectionnumber':'1',
					'idnumber':'',
					'added':'1523491403',
					'score':'0',
					'indent':'0',
					'visible':'1',
					'visibleoncoursepage':'1',
					'visibleold':'1',
					'groupmode':'0',
					'groupingid':'0',
					'completion':'0',
					'completiongradeitemnumber':'$@NULL@$',
					'completionview':'0',
					'completionexpected':'0',
					'availability':'$@NULL@$',
					'showdescription':'0',
					'tags' : ''}

	for key,value in module_dic.items():
		temp = etree.SubElement(root, key)
		temp.text = value

	module_file = open(folder+ "activities/"+type1+"_"+activity_id+"/module.xml","wb")
	module_file.write(etree.tostring(root,xml_declaration=True,encoding='UTF-8',pretty_print=True).replace(b"'", b'"'))
	module_file.close()		


	#Time to mkae resource.xml
	root = etree.Element("activity")
	root.set('id',activity_id)
	root.set('moduleid', activity_id) #TODO figure out
	root.set('modulename', type1)
	root.set('contextid', '43')

	resource = etree.SubElement(root, type1)
	resource.set('id', activity_id)

	res_dic = {	'name': 'CLIX UNIT EPUB',
				'intro':'',
				'introformat':'1',
				'tobemigrated':'0',
				'legacyfiles':'0',
				'legacyfileslast':'$@NULL@$',
				'display':'0',
				'displayoptions':'a:1:{s:10:"printintro";i:1;}',
				'filterfiles':'0',
				'revision':'2',
				'timemodified':'1523494275'}

	for key,value in res_dic.items():
		temp = etree.SubElement(resource, key)
		temp.text = value

	res_file = open(folder+ "activities/"+type1+"_"+activity_id+"/resource.xml","wb")
	res_file.write(etree.tostring(root, xml_declaration=True, encoding='UTF-8', pretty_print=True).replace(b"'", b'"') )
	res_file.close()


def configure_files(filename):
	fileloc = "/home/bgargi/HBCSE/try_pandoc/le_unit-4-finding-postal-charges_ver11092017.epub"		
	hash1, name = subprocess.check_output("sha1sum "+fileloc, shell=True).split()
	hash1 = hash1.decode('ASCII')
	foldername = hash1[0:2]
	#foldername = foldername.decode('ASCII')
	x = folder+"files/"+foldername
	if not os.path.exists(x):
		os.mkdir(x)
	os.system('cp '+fileloc+' '+folder+"files/"+foldername+"/"+hash1)

	root = etree.Element('files')
	file = etree.SubElement(root, 'file')
	file.set('id', '100')	#TODO
	filesize = os.path.getsize(folder+ "files/"+foldername+'/'+hash1)
	filesize = str(filesize)
	files_dic = {'contenthash': hash1,
					'contextid':'43',	#TODO
					'component':'mod_resource',
					'filearea':'content',
					'itemid':'0',
					'filepath':'/',
					'filename': filename,
					'userid': '2',
					'filesize':filesize,
					'mimetype':'application/epub+zip',
					'status':'0',
					'timecreated':'1523491397',
					'timemodified':'1523491403',
					'source':filename,
					'author':'CLIx',
					'license':'allrightsreserved',
					'sortorder':'1',
					'repositorytype':'$@NULL@$',
					'repositoryid':'$@NULL@$',
					'reference':'$@NULL@$'}

	for key,value in files_dic.items():
		temp = etree.SubElement(file, key)
		temp.text = value

	file = etree.SubElement(root, 'file')
	file.set('id', '101')	#TODO
	files_dic = {'contenthash': 'da39a3ee5e6b4b0d3255bfef95601890afd80709',
					'contextid':'43',	#TODO
					'component':'mod_resource',
					'filearea':'content',
					'itemid':'0',
					'filepath':'/',
					'filename': '.',
					'userid': '2',
					'filesize':'0',
					'mimetype':'$@NULL@$',
					'status':'0',
					'timecreated':'1523491398',
					'timemodified':'1523494145',
					'source':'$@NULL@$',
					'author':'$@NULL@$',
					'license':'$@NULL@$',
					'sortorder':'0',
					'repositorytype':'$@NULL@$',
					'repositoryid':'$@NULL@$',
					'reference':'$@NULL@$'}

	for key,value in files_dic.items():
		temp = etree.SubElement(file, key)
		temp.text = value

	files_xml = open(folder+ "files.xml","wb")
	files_xml.write(etree.tostring(root, xml_declaration=True, encoding='UTF-8', pretty_print=True).replace(b"'", b'"') )
	files_xml.close()

def main():
	
	short_name = 'Content Exchange'
	full_name = 'Content Exchange for Moodle Export'
	course_id = '6'

	section_id = '1'
	section_name = 'Read read read!'
	section_summary = 'Enjoy reading!'
	contextid = '40'
	course_summary = 'Welcome to exchange of content trial of CLIx with Moodle!'


	create_skeleton()

	generate_dummy_files()

	generate_moodle_backup_file(course_id,full_name,short_name)

	fill_sections_folder(section_id,section_name,section_summary)

	fill_course_folder(course_id,contextid,full_name,short_name,course_summary)
	#type-resourc/book etc,with id

	type1 = 'resource'
	activity_id = '1'

	fill_activities_folder(type1,activity_id,'1')

	configure_files('le_unit-4-finding-postal-charges_ver11092017.epub') #pass epub file name

	#os.system("tar -czvf MoodleBackupUnit.mbz ./*")

main()	