import json

from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import get_course_completetion_status, dig_nodes_field
from gnowsys_ndf.ndf.templatetags.simple_filters import get_dict_from_list_of_dicts
benchmark_collection = db[Benchmark.collection_name]

class AnalyticsMethods(object):

	print "=== Class Defination === "

	def __init__(self, request, group_id):
		super(AnalyticsMethods, self).__init__()
		self.request = request
		self.group_id = group_id
		self.group_obj = node_collection.one({'_id': ObjectId(self.group_id)})
		self.user_id = self.request.user.id

	def get_total_units_count(self):
		# print "\n\n get_total_units_count === "
		unit_event_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseUnitEvent"})
		all_unit_event_cur = node_collection.find({'member_of': unit_event_gst._id, 'group_set': ObjectId(self.group_id)})
		return all_unit_event_cur.count()

	def get_completed_units_count(self):
		# print "\n\n get_completed_units_count === "
		unit_event_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseUnitEvent"})
		if hasattr(self,'obj_ids'):
			completed_unit_event_cur = node_collection.find({'member_of': unit_event_gst._id,
			 'group_set': ObjectId(self.group_id), '_id': {'$in': self.obj_ids}})
		else:
			result_status = get_course_completetion_status(self.group_obj, self.user_id, True)
			if "completed_ids_list" in result_status:
				str_ids = json.loads(result_status['completed_ids_list'])
				self.obj_ids = map(ObjectId, str_ids)
				completed_unit_event_cur = node_collection.find({'member_of': unit_event_gst._id,
				 'group_set': ObjectId(self.group_id), '_id': {'$in': self.obj_ids}})
		return completed_unit_event_cur.count()

	def get_total_resources_count(self):
		# print "\n get_total_resources_count === "
		self.all_res_nodes = []
		self.all_res_nodes = dig_nodes_field(self.group_obj,'collection_set',True,['Page','File'],self.all_res_nodes)
		return len(self.all_res_nodes)

	def get_completed_resources_count(self):
		# print "\n get_completed_resources_count === "
		if hasattr(self,'obj_ids'):
			return len(self.obj_ids)
		result_status = get_course_completetion_status(self.group_obj, self.user_id, True)
		if "completed_ids_list" in result_status:
			str_ids = json.loads(result_status['completed_ids_list'])
			return len(self.obj_ids)
			self.obj_ids = map(ObjectId, str_ids)

	def get_total_quizitems_count(self):
		quizitem_event_gst = node_collection.one({'_type': "GSystemType", 'name': "QuizItemEvent"})
		all_quizitem_event_cur = node_collection.find({'member_of': quizitem_event_gst._id, 'group_set': ObjectId(self.group_id)})
		return all_quizitem_event_cur.count()

	def get_attempted_quizitems_count(self, return_cur=False):
		quizitem_post_gst = node_collection.one({'_type': "GSystemType", 'name': "QuizItemPost"})
		self.quizitem_post_cur = node_collection.find({'member_of': quizitem_post_gst._id,
		 'group_set': ObjectId(self.group_id), 'created_by': self.user_id})
		if return_cur:
			return self.quizitem_post_cur
		return self.quizitem_post_cur.count()

	def get_correct_quizitems_count(self):
		total_qi_cur = self.get_attempted_quizitems_count(True)
		for each_qi in total_qi_cur:
			# print each_qi._id, " == ",each_qi.origin, "\n == \n\n"
			prior_node_id = each_qi.origin[0].get('prior_node_id_of_thread',None)
			if prior_node_id:
				prior_node_obj = node_collection.one({'_id': ObjectId(prior_node_id)})
				# print "\n\n prior_node_obj=== ",prior_node_obj.attribute_set
				if prior_node_obj.attribute_set:
					for pr_each_attr in prior_node_obj.attribute_set:
						if pr_each_attr and 'correct_answer' in pr_each_attr:
							correct_ans_list = pr_each_attr['correct_answer']
							print "\n correct_ans_list == ",correct_ans_list
			if each_qi.attribute_set:
				for each_attr in each_qi.attribute_set:
					if each_attr and 'quizitempost_user_submitted_ans' in each_attr:
						# print "\n --- each_attr['quizitempost_user_submitted_ans'] --- ",each_attr['quizitempost_user_submitted_ans']
						submitted_ans = get_dict_from_list_of_dicts(each_attr['quizitempost_user_submitted_ans'])
						submitted_ans = reduce(lambda x, y: x+y, submitted_ans.values())
						print "\n\n submitted_ans == ", submitted_ans

		# return quizitem_post_cur.count()

	def get_incorrect_quizitems_count(self):
		quizitem_post_gst = node_collection.one({'_type': "GSystemType", 'name': "QuizItemPost"})
		quizitem_post_cur = node_collection.find({'member_of': quizitem_post_gst._id,
		 'group_set': ObjectId(self.group_id), 'created_by': self.user_id})
		return quizitem_post_cur.count()
