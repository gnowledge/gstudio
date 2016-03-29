import json
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import get_course_completetion_status, dig_nodes_field, sublistExists
from gnowsys_ndf.ndf.templatetags.simple_filters import get_dict_from_list_of_dicts
benchmark_collection = db[Benchmark.collection_name]

class AnalyticsMethods(object):
	print "=== Class Defination === "

	def __init__(self, request, user_id, group_id):
		super(AnalyticsMethods, self).__init__()
		self.request = request
		self.group_id = group_id
		self.group_obj = node_collection.one({'_id': ObjectId(self.group_id)})
		self.user_id = user_id

	def get_total_units_count(self):
		# print "\n\n get_total_units_count === "
		if not hasattr(self,'unit_event_gst'):
			self.unit_event_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseUnitEvent"})

		all_unit_event_cur = node_collection.find({'member_of': self.unit_event_gst._id, 'group_set': ObjectId(self.group_id)})
		return all_unit_event_cur.count()

	def get_completed_units_count(self):
		# print "\n\n get_completed_units_count === "
		if not hasattr(self,'unit_event_gst'):
			self.unit_event_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseUnitEvent"})

		if hasattr(self,'user_completed_obj_ids'):
			completed_unit_event_cur = node_collection.find({'member_of': self.unit_event_gst._id,
			 'group_set': ObjectId(self.group_id), '_id': {'$in': self.user_completed_obj_ids}})
		else:
			if not hasattr(self,'result_status'):
				self.result_status = get_course_completetion_status(self.group_obj, self.user_id, True)
			if "completed_ids_list" in self.result_status:
				str_ids = json.loads(self.result_status['completed_ids_list'])
				self.user_completed_obj_ids = map(ObjectId, str_ids)
				completed_unit_event_cur = node_collection.find({'member_of': self.unit_event_gst._id,
				 'group_set': ObjectId(self.group_id), '_id': {'$in': self.user_completed_obj_ids}})
		return completed_unit_event_cur.count()

	def get_total_resources_count(self):
		# print "\n get_total_resources_count === "
		self.all_res_nodes = []
		self.all_res_nodes = dig_nodes_field(self.group_obj,'collection_set',True,['Page','File'],self.all_res_nodes)
		return len(self.all_res_nodes)

	def get_completed_resources_count(self):
		# print "\n get_completed_resources_count === "
		if hasattr(self,'completed_res_ids_list'):
			return len(self.completed_res_ids_list)
		if not hasattr(self,'result_status'):
			self.result_status = get_course_completetion_status(self.group_obj, self.user_id, True)
		if not hasattr(self,'all_res_nodes'):
			self.all_res_nodes = self.get_total_resources_count()
		if "completed_ids_list" in self.result_status:
			str_ids = json.loads(self.result_status['completed_ids_list'])
			self.user_completed_obj_ids = map(ObjectId, str_ids)
			# print "\n self.all_res_nodes === ",len(self.all_res_nodes)
			# print "\n self.user_completed_obj_ids === ",len(self.user_completed_obj_ids)
			self.completed_res_ids_list = [each_id for each_id in self.all_res_nodes if each_id in self.user_completed_obj_ids ]

			return len(self.completed_res_ids_list)

	def get_total_quizitems_count(self):
		quizitem_event_gst = node_collection.one({'_type': "GSystemType", 'name': "QuizItemEvent"})
		all_quizitem_event_cur = node_collection.find({'member_of': quizitem_event_gst._id, 'group_set': ObjectId(self.group_id)})
		return all_quizitem_event_cur.count()

	def get_attempted_quizitems_count(self, return_cur_obj=False):
		quizitem_post_gst = node_collection.one({'_type': "GSystemType", 'name': "QuizItemPost"})
		self.quizitem_post_cur = node_collection.find({'member_of': quizitem_post_gst._id,
		 'group_set': ObjectId(self.group_id), 'created_by': self.user_id})
		if return_cur_obj:
			return self.quizitem_post_cur
		return self.quizitem_post_cur.count()

	# def get_evaluated_quizitems_count(self,evaluation_result_type):
	def get_evaluated_quizitems_count(self,correct_ans_flag=False, incorrect_ans_flag=False):
		if not hasattr(self,'list_of_qi_ids') and not hasattr(self,'total_qi_cur'):
			self.total_qi_cur = self.get_attempted_quizitems_count(True)
			self.list_of_qi_ids = []
			for each_qi in self.total_qi_cur:
				prior_node_id = each_qi.origin[0].get('prior_node_id_of_thread',None)
				if prior_node_id:
					prior_node_obj = node_collection.one({'_id': ObjectId(prior_node_id)})
					if prior_node_obj.attribute_set:
						for pr_each_attr in prior_node_obj.attribute_set:
							if pr_each_attr and 'correct_answer' in pr_each_attr:
								correct_ans_list = pr_each_attr['correct_answer']
				if each_qi.attribute_set:
					for each_attr in each_qi.attribute_set:
						if each_attr and 'quizitempost_user_submitted_ans' in each_attr:
							submitted_ans = get_dict_from_list_of_dicts(each_attr['quizitempost_user_submitted_ans'])
							submitted_ans = reduce(lambda x, y: x+y, submitted_ans.values())

							if correct_ans_list and submitted_ans:
								if sublistExists(submitted_ans, correct_ans_list):
									if each_qi._id not in self.list_of_qi_ids:
										self.list_of_qi_ids.append(each_qi._id)
		if correct_ans_flag:
			return len(self.list_of_qi_ids)
		elif incorrect_ans_flag:
			return (self.total_qi_cur.count()-len(self.list_of_qi_ids))
		else:
			return 0

	def get_total_notes_count(self):
		if not hasattr(self,"blog_page_gst") and not hasattr(self,"page_gst"):
			self.blog_page_gst = node_collection.one({'_type': "GSystemType", 'name': "Blog page"})
			self.page_gst = node_collection.one({'_type': "GSystemType", 'name': "Page"})
		self.all_notes_cur = node_collection.find({'member_of': self.page_gst._id, 'type_of': self.blog_page_gst._id})
		return self.all_notes_cur.count()

	def get_user_notes_count(self, return_cur_obj=False):
		if not hasattr(self,"blog_page_gst") and not hasattr(self,"page_gst"):
			self.blog_page_gst = node_collection.one({'_type': "GSystemType", 'name': "Blog page"})
			self.page_gst = node_collection.one({'_type': "GSystemType", 'name': "Page"})
		self.user_notes_cur = node_collection.find({'member_of': self.page_gst._id, 'type_of': self.blog_page_gst._id, 'created_by': self.user_id})
		if return_cur_obj:
			return self.user_notes_cur
		return self.user_notes_cur.count()

	def get_comments_counts_on_users_notes(self):
		if not hasattr(self,"user_notes_cur"):
			self.user_notes_cur = self.get_user_notes_count(True)
		user_notes_cur_ids = [each_user_note._id for each_user_note in self.user_notes_cur]
		if not hasattr(self, "reply_gst"):
			self.reply_gst = node_collection.one({'_type': "GSystemType", 'name': "Reply"})
		list_of_dict_notes = []
		for each_user_note_id in user_notes_cur_ids:
			list_of_dict_notes.append({'prior_node_id_of_thread': ObjectId(each_user_note_id)})
		self.notes_reply_cur = node_collection.find({'member_of': self.reply_gst._id, 'origin': {'$in': list_of_dict_notes}})
		return self.notes_reply_cur.count()

	def get_total_files_count(self):
		if not hasattr(self,"file_gst"):
			self.file_gst = node_collection.one({'_type': "GSystemType", 'name': "File"})
		self.all_files_cur = node_collection.find({'member_of': self.file_gst._id, 'group_set': self.group_obj._id})
		return self.all_files_cur.count()


	def get_user_files_count(self, return_cur_obj=False):
		if not hasattr(self,"file_gst"):
			self.file_gst = node_collection.one({'_type': "GSystemType", 'name': "File"})
		self.user_files_cur = node_collection.find({'member_of': self.file_gst._id, 'created_by': self.user_id, 'group_set': self.group_obj._id})
		if return_cur_obj:
			return self.user_files_cur
		return self.user_files_cur.count()

	def get_comments_counts_on_users_files(self):
		if not hasattr(self,"user_files_cur"):
			self.user_files_cur = self.get_user_notes_count(True)
		user_files_cur_ids = [each_user_file._id for each_user_file in self.user_files_cur]
		if not hasattr(self, "reply_gst"):
			self.reply_gst = node_collection.one({'_type': "GSystemType", 'name': "Reply"})
		list_of_dict_files = []
		for each_user_file_id in user_files_cur_ids:
			list_of_dict_files.append({'prior_node_id_of_thread': ObjectId(each_user_file_id)})
		self.files_reply_cur = node_collection.find({'member_of': self.reply_gst._id, 'origin': {'$in': list_of_dict_files}})
		return self.files_reply_cur.count()
