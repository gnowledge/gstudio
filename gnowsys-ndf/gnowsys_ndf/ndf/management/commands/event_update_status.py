from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import create_gattribute

import datetime

def event_upd():	

	# Update for meeting
	all_meets = node_collection.find({'url':u'meeting'})
	updater(all_meets)

	# Update for session
	all_sessions = node_collection.find({'url':u'session'})
	updater(all_sessions)

	# Update for inaugrations
	all_inaug = node_collection.find({'url':u'inauguration'})
	updater(all_inaug)

	# Update for field visit
	all_fv = node_collection.find({'url':u'field visit'})
	updater(all_fv)

	# Update for orientation
	all_or = node_collection.find({'url':u'orientation'})
	updater(all_or)

	# Update for master trainer program
	all_mtp = node_collection.find({'url':u'master trainer program'})
	updater(all_mtp)

	# Update for master trainer program
	all_mtp = node_collection.find({'url':u'master trainer program'})
	updater(all_mtp)

	# Update for training of teachers
	all_tot = node_collection.find({'url':u'training of teachers'})
	updater(all_tot)

	# Update for course developers meeting
	all_cdm = node_collection.find({'url':u'course developers meeting'})
	updater(all_cdm)

	# Update for lab session
	all_ls = node_collection.find({'url':u'lab session'})
	updater(all_ls)



def updater(all_events):

	now = datetime.datetime.now()
	status = node_collection.one({'_type' : 'AttributeType' , 'name': 'event_status'})

	for event in all_events:
		for i in event.attribute_set:
			try:
				end_time = i['end_time']
				break
			except:
				pass

		if now > end_time:
			create_gattribute(event._id , status , unicode("Completed"))
			
