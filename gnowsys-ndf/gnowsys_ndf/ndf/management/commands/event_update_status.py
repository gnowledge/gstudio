from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import create_gattribute
from django.core.management.base import BaseCommand, CommandError

import datetime

class Command(BaseCommand):
	help = "This command updates the status of all events"

	def handle(self, *args, **options):
		self.event_upd()

	def event_upd(self):

		# Update for meeting
		all_meets = node_collection.find({'url':u'meeting'})
		self.updater(all_meets)

		# Update for session
		all_sessions = node_collection.find({'url':u'session'})
		self.updater(all_sessions)

		# Update for inaugrations
		all_inaug = node_collection.find({'url':u'inauguration'})
		self.updater(all_inaug)

		# Update for field visit
		all_fv = node_collection.find({'url':u'field visit'})
		self.updater(all_fv)

		# Update for orientation
		all_or = node_collection.find({'url':u'orientation'})
		self.updater(all_or)

		# Update for master trainer program
		all_mtp = node_collection.find({'url':u'master trainer program'})
		self.updater(all_mtp)

		# Update for master trainer program
		all_mtp = node_collection.find({'url':u'master trainer program'})
		self.updater(all_mtp)

		# Update for training of teachers
		all_tot = node_collection.find({'url':u'training of teachers'})
		self.updater(all_tot)

		# Update for course developers meeting
		all_cdm = node_collection.find({'url':u'course developers meeting'})
		self.updater(all_cdm)

		# Update for lab session
		all_ls = node_collection.find({'url':u'lab session'})
		self.updater(all_ls)



	def updater(self,all_events):
		'''
		This function will iterate over all events and will mark the "Scheduled" meets whose end_time is 
		over as "Completed" in event_status of event object's Attribute Set
		'''

		now = datetime.datetime.now()
		e_status = node_collection.one({'_type' : 'AttributeType' , 'name': 'event_status'})

		for event in all_events:
			for i in event.attribute_set:
				if unicode('end_time') in i.keys():
					end_time = i['end_time']
				elif unicode('event_status') in i.keys():
					status = i['event_status']	

			if status == unicode("Scheduled"):
				if now > end_time:
					create_gattribute(event._id , e_status , unicode("Completed"))