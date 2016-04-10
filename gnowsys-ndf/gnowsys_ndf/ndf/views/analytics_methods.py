import json
import time
from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.methods import get_course_completetion_status, dig_nodes_field, sublistExists
from gnowsys_ndf.ndf.templatetags.simple_filters import get_dict_from_list_of_dicts
benchmark_collection = db[Benchmark.collection_name]

class AnalyticsMethods(object):
	print "=== Class Defination === "

	def __init__(self, request, user_id, username, group_id):
		super(AnalyticsMethods, self).__init__()
		self.request = request
		self.group_id = group_id
		self.group_obj = node_collection.one({'_id': ObjectId(self.group_id)})
		self.user_id = user_id
		self.username = username

	def get_total_modules_count(self):
		t0 = time.time()

		if not hasattr(self,'course_section_event_gst'):
			self.course_section_event_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseSectionEvent"})

		all_modules_cur = node_collection.find({'member_of': self.course_section_event_gst._id, 'group_set': ObjectId(self.group_id)},{'_id': 1})
		t1 = time.time()
		time_diff = t1 - t0
		# print "\n get_total_units_count == ", time_diff

		return all_modules_cur.count()

	def get_completed_modules_count(self):
		t0 = time.time()

		if not hasattr(self,'course_section_event_gst'):
			self.course_section_event_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseUnitEvent"},{'_id': 1})

		if hasattr(self,'user_completed_obj_ids'):
			completed_modules_cur = node_collection.find({'member_of': self.course_section_event_gst._id,
			 'group_set': ObjectId(self.group_id), '_id': {'$in': self.user_completed_obj_ids}},{'_id': 1})
		else:
			if not hasattr(self,'result_status'):
				self.result_status = get_course_completetion_status(self.group_obj, self.user_id, True)
			if "completed_ids_list" in self.result_status:
				str_ids = json.loads(self.result_status['completed_ids_list'])
				self.user_completed_obj_ids = map(ObjectId, str_ids)
				completed_modules_cur = node_collection.find({'member_of': self.course_section_event_gst._id,
				 'group_set': ObjectId(self.group_id), '_id': {'$in': self.user_completed_obj_ids}},{'_id': 1})

		t1 = time.time()
		time_diff = t1 - t0
		# print "\n get_completed_units_count == ", time_diff

		return completed_modules_cur.count()


	def get_total_units_count(self):
		t0 = time.time()

		# print "\n\n get_total_units_count === "
		if not hasattr(self,'unit_event_gst'):
			self.unit_event_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseUnitEvent"})

		all_unit_event_cur = node_collection.find({'member_of': self.unit_event_gst._id, 'group_set': ObjectId(self.group_id)},{'_id': 1})
		t1 = time.time()
		time_diff = t1 - t0
		# print "\n get_total_units_count == ", time_diff

		return all_unit_event_cur.count()

	def get_completed_units_count(self):
		t0 = time.time()

		# print "\n\n get_completed_units_count === "
		if not hasattr(self,'unit_event_gst'):
			self.unit_event_gst = node_collection.one({'_type': "GSystemType", 'name': "CourseUnitEvent"},{'_id': 1})

		if hasattr(self,'user_completed_obj_ids'):
			completed_unit_event_cur = node_collection.find({'member_of': self.unit_event_gst._id,
			 'group_set': ObjectId(self.group_id), '_id': {'$in': self.user_completed_obj_ids}},{'_id': 1})
		else:
			if not hasattr(self,'result_status'):
				self.result_status = get_course_completetion_status(self.group_obj, self.user_id, True)
			if "completed_ids_list" in self.result_status:
				str_ids = json.loads(self.result_status['completed_ids_list'])
				self.user_completed_obj_ids = map(ObjectId, str_ids)
				completed_unit_event_cur = node_collection.find({'member_of': self.unit_event_gst._id,
				 'group_set': ObjectId(self.group_id), '_id': {'$in': self.user_completed_obj_ids}},{'_id': 1})

		t1 = time.time()
		time_diff = t1 - t0
		# print "\n get_completed_units_count == ", time_diff

		return completed_unit_event_cur.count()

	def get_total_resources_count(self):
		t0 = time.time()

		# print "\n get_total_resources_count === "
		self.all_res_nodes = []
		self.all_res_nodes = dig_nodes_field(self.group_obj,'collection_set',True,['Page','File'],self.all_res_nodes)
		t1 = time.time()
		time_diff = t1 - t0
		# print "\n get_total_resources_count == ", time_diff

		return len(self.all_res_nodes)

	def get_completed_resources_count(self):
		t0 = time.time()

		# print "\n get_completed_resources_count === "
		if hasattr(self,'completed_res_ids_list'):
			t1 = time.time()
			time_diff = t1 - t0
			print "\n get_completed_resources_count == ", time_diff

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
			t1 = time.time()
			time_diff = t1 - t0
			# print "\n get_completed_resources_count == ", time_diff

			return len(self.completed_res_ids_list)

	def get_total_quizitems_count(self):
		t0 = time.time()

		quizitem_event_gst = node_collection.one({'_type': "GSystemType", 'name': "QuizItemEvent"},{'_id': 1})
		all_quizitem_event_cur = node_collection.find({'member_of': quizitem_event_gst._id, 'group_set': ObjectId(self.group_id)},{'_id': 1})
		t1 = time.time()
		time_diff = t1 - t0
		# print "\n get_total_quizitems_count == ", time_diff
		
		return all_quizitem_event_cur.count()

	def get_attempted_quizitems_count(self, return_cur_obj=False):
		t0 = time.time()

		quizitem_post_gst = node_collection.one({'_type': "GSystemType", 'name': "QuizItemPost"},{'_id': 1})
		self.quizitem_post_cur = node_collection.find({'member_of': quizitem_post_gst._id,
		 'group_set': ObjectId(self.group_id), 'created_by': self.user_id},{'_id': 1, 'origin': 1, 'attribute_set': 1})
		if return_cur_obj:
			t1 = time.time()
			time_diff = t1 - t0
			# print "\n get_attempted_quizitems_count == ", time_diff

			return self.quizitem_post_cur
		t1 = time.time()
		time_diff = t1 - t0
		# print "\n get_attempted_quizitems_count == ", time_diff

		return self.quizitem_post_cur.count()

	def get_evaluated_quizitems_count(self,correct_ans_flag=False, incorrect_ans_flag=False):
		t0 = time.time()

		if not hasattr(self,'list_of_qi_ids') and not hasattr(self,'total_qi_cur'):
			self.total_qi_cur = self.get_attempted_quizitems_count(True)
			self.list_of_qi_ids = []
			for each_qi in self.total_qi_cur:
				prior_node_id = each_qi.origin[0].get('prior_node_id_of_thread',None)
				if prior_node_id:
					prior_node_obj = node_collection.one({'_id': ObjectId(prior_node_id)},{'_id':1, 'attribute_set':1})
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
			t1 = time.time()
			time_diff = t1 - t0
			# print "\n get_evaluated_quizitems_count == ", time_diff

			return len(self.list_of_qi_ids)
		elif incorrect_ans_flag:
			t1 = time.time()
			time_diff = t1 - t0
			# print "\n get_evaluated_quizitems_count == ", time_diff

			return (self.total_qi_cur.count()-len(self.list_of_qi_ids))
		else:
			return 0

	def get_total_notes_count(self):
		t0 = time.time()

		if not hasattr(self,"blog_page_gst") and not hasattr(self,"page_gst"):
			self.blog_page_gst = node_collection.one({'_type': "GSystemType", 'name': "Blog page"},{'_id': 1})
			self.page_gst = node_collection.one({'_type': "GSystemType", 'name': "Page"},{'_id': 1})
		self.all_notes_cur = node_collection.find({'member_of': self.page_gst._id, 'type_of': self.blog_page_gst._id,
			'group_set': self.group_obj._id},{'_id': 1})
		t1 = time.time()
		time_diff = t1 - t0
		# print "\n get_total_notes_count == ", time_diff

		return self.all_notes_cur.count()

	def get_user_notes_count(self, return_cur_obj=False):
		t0 = time.time()

		if not hasattr(self,'user_notes_cur'):
			if not hasattr(self,"blog_page_gst") and not hasattr(self,"page_gst"):
				self.blog_page_gst = node_collection.one({'_type': "GSystemType", 'name': "Blog page"},{'_id': 1})
				self.page_gst = node_collection.one({'_type': "GSystemType", 'name': "Page"},{'_id': 1})
			self.user_notes_cur = node_collection.find({'member_of': self.page_gst._id,
			 'type_of': self.blog_page_gst._id, 'created_by': self.user_id, 'group_set': self.group_obj._id},{'_id': 1})
		if return_cur_obj:
			t1 = time.time()
			time_diff = t1 - t0
			# print "\n get_user_notes_count == ", time_diff
			return self.user_notes_cur
		t1 = time.time()
		time_diff = t1 - t0
		# print "\n get_user_notes_count == ", time_diff
		return self.user_notes_cur.count()

	def get_comments_counts_on_users_notes(self, return_cur_obj=False):
		t0 = time.time()

		if not hasattr(self,"user_notes_cur"):
			self.user_notes_cur = self.get_user_notes_count(True)

		user_notes_cur_ids = [each_user_note._id for each_user_note in self.user_notes_cur]

		if not hasattr(self, "reply_gst"):
			self.reply_gst = node_collection.one({'_type': "GSystemType", 'name': "Reply"},{'_id': 1})

		list_of_dict_notes = []
		for each_user_note_id in user_notes_cur_ids:
			list_of_dict_notes.append({'prior_node_id_of_thread': ObjectId(each_user_note_id)})

		self.all_comments_on_user_notes = node_collection.find({'member_of': self.reply_gst._id, 'origin': {'$in': list_of_dict_notes}},{'_id': 1, 'created_by': 1})
		if return_cur_obj:
			t1 = time.time()
			time_diff = t1 - t0
			# print "\n get_comments_counts_on_users_notes == ", time_diff

			return self.all_comments_on_user_notes
		t1 = time.time()
		time_diff = t1 - t0
		# print "\n get_comments_counts_on_users_notes == ", time_diff

		return self.all_comments_on_user_notes.count()

	def get_commented_unique_users_count(self, for_notes=False,for_files=False):
		t0 = time.time()
		notes_or_files_cur = None
		commentors_ids = []

		'''
		# APPROACH 1
		if for_notes:
			if not hasattr(self,"user_notes_cur"):
				notes_or_files_cur = self.get_user_notes_count(True)
			else:
				notes_or_files_cur = self.user_notes_cur.rewind()
		elif for_files:
			if not hasattr(self,"user_files_cur"):
				notes_or_files_cur = self.get_user_files_count(True)
			else:
				notes_or_files_cur = self.user_files_cur.rewind()

		twist_gst = node_collection.one({'_type': "GSystemType", 'name': 'Twist'})
		user_notes_or_files_cur_ids = []

		for each_note_or_file in notes_or_files_cur:
			if each_note_or_file.relation_set:
				for each_note_or_file_rel in each_note_or_file.relation_set:
					if each_note_or_file_rel and 'has_thread' in each_note_or_file_rel:
						user_notes_or_files_cur_ids.append(each_note_or_file_rel['has_thread'][0])

		user_notes_or_files_threads_cur = node_collection.find({'member_of': twist_gst._id, '_id': {'$in': user_notes_or_files_cur_ids}})
		for each_thread in user_notes_or_files_threads_cur:
			commentors_ids.extend(each_thread.author_set)
		if commentors_ids:
			commentors_ids = set(list(commentors_ids))
		t1 = time.time()
		time_diff = t1 - t0
		print "\n Total seconds == ", time_diff
		# total_time_minute = round( (time_diff/60), 2) if time_diff else 0
		# total_time_hour = round( (time_diff/(60*60)), 2) if time_diff else 0
		return len(commentors_ids)

		'''
		# APPROACH 2

		if for_notes:
			if not hasattr(self,"all_comments_on_user_notes"):
				notes_or_files_cur = self.get_comments_counts_on_users_notes(True)
			else:
				notes_or_files_cur = self.all_comments_on_user_notes.rewind()
		if for_files:
			if not hasattr(self,"all_comments_on_user_files"):
				notes_or_files_cur = self.get_comments_counts_on_users_files(True)
			else:
				notes_or_files_cur = self.all_comments_on_user_files.rewind()
		for each_note_file_cmt in notes_or_files_cur:
			commentors_ids.append(each_note_file_cmt.created_by)

		if commentors_ids:
			commentors_ids = set(list(commentors_ids))

		t1 = time.time()
		time_diff = t1 - t0
		# print "\n get_commented_unique_users_count == ", time_diff
		return len(commentors_ids)

	def get_total_files_count(self):
		t0 = time.time()

		if not hasattr(self,"file_gst"):
			self.file_gst = node_collection.one({'_type': "GSystemType", 'name': "File"},{'_id': 1})
		self.all_files_cur = node_collection.find({'member_of': self.file_gst._id, 'group_set': self.group_obj._id},{'_id': 1})
		t1 = time.time()
		time_diff = t1 - t0
		# 	print "\n get_total_files_count == ", time_diff

		return self.all_files_cur.count()

	def get_user_files_count(self, return_cur_obj=False):
		t0 = time.time()

		if not hasattr(self,"file_gst"):
			self.file_gst = node_collection.one({'_type': "GSystemType", 'name': "File"},{'_id': 1})
		self.user_files_cur = node_collection.find({'member_of': self.file_gst._id, 'created_by': self.user_id, 'group_set': self.group_obj._id},{'_id': 1, 'created_by': 1})
		if return_cur_obj:
			t1 = time.time()
			time_diff = t1 - t0
			# print "\n get_user_files_count == ", time_diff

			return self.user_files_cur
		t1 = time.time()
		time_diff = t1 - t0
		# print "\n get_user_files_count == ", time_diff

		return self.user_files_cur.count()

	def get_comments_counts_on_users_files(self, return_cur_obj=False):
		t0 = time.time()

		if not hasattr(self,"user_files_cur"):
			self.user_files_cur = self.get_user_notes_count(True)
		else:
			self.user_files_cur.rewind()
		user_files_cur_ids = [each_user_file._id for each_user_file in self.user_files_cur]
		if not hasattr(self, "reply_gst"):
			self.reply_gst = node_collection.one({'_type': "GSystemType", 'name': "Reply"},{'_id': 1})
		list_of_dict_files = []
		for each_user_file_id in user_files_cur_ids:
			list_of_dict_files.append({'prior_node_id_of_thread': ObjectId(each_user_file_id)})
		self.all_comments_on_user_files = node_collection.find({'member_of': self.reply_gst._id, 'origin': {'$in': list_of_dict_files}},{'_id': 1, 'created_by': 1})
		if return_cur_obj:
			t1 = time.time()
			time_diff = t1 - t0
			# print "\n get_comments_counts_on_users_files == ", time_diff

			return self.all_comments_on_user_files
		t1 = time.time()
		time_diff = t1 - t0
		# print "\n get_comments_counts_on_users_files == ", time_diff

		return self.all_comments_on_user_files.count()
			
	def get_total_comments_by_user(self):
		t0 = time.time()
		if not hasattr(self, 'reply_gst'):
			self.reply_gst = node_collection.one({'_type': "GSystemType", 'name': "Reply"},{'_id': 1})
		self.users_replies_cur = node_collection.find({'member_of': self.reply_gst._id,
		 'created_by': self.user_id, 'group_set': self.group_obj._id})
		t1 = time.time()
		time_diff = t1 - t0
		# print "\n get_total_comments_by_user == ", time_diff
		return self.users_replies_cur.count()

	def get_others_notes_read_count(self):
		t0 = time.time()
		unique_notes_read_list = []
		if not hasattr(self, 'page_gst'):
			self.page_gst = node_collection.one({'_type': "GSystemType", 'name': "Page"},{'_id': 1})
		if not hasattr(self, 'blog_page_gst'):
			self.blog_page_gst = node_collection.one({'_type': "GSystemType", 'name': "Blog page"},{'_id': 1})

		self.other_than_user_notes = node_collection.find({'type_of': self.blog_page_gst._id,
		 'member_of': self.page_gst._id, 'group_set': self.group_obj._id, 'created_by': {'$ne': self.user_id}},{'_id': 1})
		others_notes_ids = [str(each_note_by_others._id) for each_note_by_others in self.other_than_user_notes]
		others_notes_ids_str = "|".join(others_notes_ids)
		if others_notes_ids_str:
			self.other_than_user_notes_read_count = benchmark_collection.find({'name': "course_notebook",
				'group': unicode(self.group_obj._id), 'calling_url': {'$regex': others_notes_ids_str}, 'user':self.username}).sort('last_update',-1)
			unique_notes_read_list = self.calc_my_visits(self.other_than_user_notes_read_count)

		t1 = time.time()
		time_diff = t1 - t0
		# print "\n get_others_notes_read_count == ", time_diff
		return len(unique_notes_read_list)

	def get_others_files_read_count(self):
		t0 = time.time()
		unique_files_read_list = []
		if not hasattr(self,"file_gst"):
			self.file_gst = node_collection.one({'_type': "GSystemType", 'name': "File"},{'_id': 1})
		self.other_than_user_files = node_collection.find({'member_of': self.file_gst._id,
		 'group_set': self.group_obj._id, 'created_by': {'$ne': self.user_id}},{'_id': 1})

		others_files_ids = [str(each_file_by_others._id) for each_file_by_others in self.other_than_user_files]
		others_files_ids_str = "|".join(others_files_ids)
		if others_files_ids_str:
			self.other_than_user_files_read_count = benchmark_collection.find({'name': {'$regex': "course_gallery|course_raw_material"},
				'group': unicode(self.group_obj._id), 'calling_url': {'$regex': others_files_ids_str}, 'user':self.username}).sort('last_update',-1)
			unique_files_read_list = self.calc_my_visits(self.other_than_user_files_read_count)

		t1 = time.time()
		time_diff = t1 - t0
		# print "\n get_others_files_read_count == ", time_diff
		# print "\n get_others_files_read_count == ", unique_files_read_list

		return len(unique_files_read_list)

	def calc_my_visits(self, cursor_obj):

		unique_list = []
		for each in cursor_obj:
			oid = ObjectId(each['calling_url'].split('/')[-1])
			if isinstance(oid, ObjectId):
				oid = ObjectId(oid)
				if oid not in unique_list :
					unique_list.append(oid)
		return unique_list

	def calc_unique_users(self, cursor_obj):
		# unique_user_list = []
		unique_user_list = [each['user'] for each in cursor_obj if each['user']]
		unique_user_list = list(set(list(unique_user_list)))
		# for each in cursor_obj:

		# 	authenticated_user = each['user']
		# 	if authenticated_user:
		# 		if authenticated_user not in unique_user_list :
		# 			unique_user_list.append(authenticated_user)
		return unique_user_list

	def total_users_read_my_notes(self):
		t0 = time.time()
		unique_users_read_my_notes = []
		if not hasattr(self,"user_notes_cur"):
			self.user_notes_cur = self.get_user_notes_count(True)
		else:
			self.user_notes_cur.rewind()
		users_notes_ids = [str(each_user_note_obj._id) for each_user_note_obj in self.user_notes_cur]
		users_notes_ids_str = "|".join(users_notes_ids)
		if users_notes_ids_str:
			self.my_notes_read_count = benchmark_collection.find({'name': "course_notebook",
				'group': unicode(self.group_obj._id), 'calling_url': {'$regex': users_notes_ids_str},
				'user':{'$ne': self.username}}).sort('last_update',-1)

			unique_users_read_my_notes = self.calc_unique_users(self.my_notes_read_count)
		t1 = time.time()
		time_diff = t1 - t0
		# print "\n total_users_read_my_notes == ", time_diff

		return len(unique_users_read_my_notes)

	def total_users_visted_my_files(self):
		t0 = time.time()
		unique_users_read_my_files = []
		if not hasattr(self,"user_files_cur"):
			self.user_files_cur = self.get_user_files_count(True)
		else:
			self.user_files_cur.rewind()
		users_files_ids = [str(each_user_file_obj._id) for each_user_file_obj in self.user_files_cur]
		users_files_ids_str = "|".join(users_files_ids)
		if users_files_ids_str:
			self.my_files_read_count = benchmark_collection.find({'name': {'$regex': "course_gallery|course_raw_material"},
				'group': unicode(self.group_obj._id), 'calling_url': {'$regex': users_files_ids_str},
				'user':{'$ne': self.username}}).sort('last_update',-1)
			unique_users_read_my_files = self.calc_unique_users(self.my_files_read_count)

		t1 = time.time()
		time_diff = t1 - t0
		# print "\n total_users_visted_my_files == ", time_diff

		return len(unique_users_read_my_files)

	def get_other_files_commented_by_user_count(self):
		t0 = time.time()
		prior_node_ids = []
		self.twist_gst = node_collection.one({'_type': "GSystemType", 'name': "Twist"})
		twist_cur = node_collection.find({'member_of': self.twist_gst._id, 'author_set': self.user_id})
		prior_node_ids = [eachtw.prior_node for eachtw in twist_cur if eachtw.prior_node]
		# for eachtw in twist_cur:
		# 	if eachtw.prior_node:
		# 		prior_node_ids.append(eachtw.prior_node)
		if not hasattr(self,"file_gst"):
			self.file_gst = node_collection.one({'_type': "GSystemType", 'name': "File"},{'_id': 1})

		files_count = node_collection.find({'member_of': self.file_gst._id,
		 'group_set': self.group_obj._id, 'created_by': {'$ne': self.user_id},
		 '_id': {'$in': prior_node_ids}})

		t1 = time.time()
		time_diff = t1 - t0
		# print "\n get_other_files_commented_by_user_count == ", time_diff
		return files_count.count()

	def get_other_notes_commented_by_user_count(self):
		t0 = time.time()
		prior_node_ids = []
		self.twist_gst = node_collection.one({'_type': "GSystemType", 'name': "Twist"})
		twist_cur = node_collection.find({'member_of': self.twist_gst._id, 'author_set': self.user_id})
		prior_node_ids = [eachtw.prior_node for eachtw in twist_cur if eachtw.prior_node]
		# for eachtw in twist_cur:
		# 	if eachtw.prior_node:
		# 		prior_node_ids.append(eachtw.prior_node)
		if not hasattr(self, 'page_gst'):
			self.page_gst = node_collection.one({'_type': "GSystemType", 'name': "Page"},{'_id': 1})
		if not hasattr(self, 'blog_page_gst'):
			self.blog_page_gst = node_collection.one({'_type': "GSystemType", 'name': "Blog page"},{'_id': 1})
		notes_count = node_collection.find({'type_of': self.blog_page_gst._id,
		 'member_of': self.page_gst._id, 'group_set': self.group_obj._id, 'created_by': {'$ne': self.user_id},
		 '_id': {'$in': prior_node_ids}})

		t1 = time.time()
		time_diff = t1 - t0
		# print "\n get_other_notes_commented_by_user_count == ", time_diff
		return notes_count.count()

	def get_ratings_received_on_user_notes(self):
		t0 = time.time()
		avg_rating_notes = total_rating = 0
		unique_user_list = []
		if not hasattr(self, 'page_gst'):
			self.page_gst = node_collection.one({'_type': "GSystemType", 'name': "Page"},{'_id': 1})
		if not hasattr(self, 'blog_page_gst'):
			self.blog_page_gst = node_collection.one({'_type': "GSystemType", 'name': "Blog page"},{'_id': 1})
		query = {'member_of': self.page_gst._id,'type_of': self.blog_page_gst._id,'group_set': self.group_obj._id,
				'created_by': self.user_id }
		# print "\n\nquery", query

		all_notes = node_collection.collection.aggregate([
						{ "$match": query },
						{ "$unwind": "$rating" },
						{ "$group": { "_id": None, "count": { "$sum": 1 }, "rating": { "$addToSet": "$rating" } } }
					])
		if 'result' in all_notes:
			result = all_notes['result']
			if result:
				cnt = result[0]['count']
				rating_list = result[0]['rating']
				for rdict in rating_list:
					total_rating += rdict['score']
					if rdict['user_id'] not in unique_user_list:
						unique_user_list.append(rdict['user_id'])
				avg_rating_notes = int(total_rating/float(cnt))
		t1 = time.time()
		time_diff = t1 - t0
		# print "\n get_ratings_received_on_user_notes == ", time_diff
		return avg_rating_notes,len(unique_user_list)


	def get_ratings_received_on_user_files(self):
		t0 = time.time()
		avg_rating_files = total_rating = 0
		unique_user_list = []

		if not hasattr(self,"file_gst"):
			self.file_gst = node_collection.one({'_type': "GSystemType", 'name': "File"},{'_id': 1})
		query = {'member_of': self.file_gst._id, 'created_by': self.user_id, 'group_set': self.group_obj._id,
		'created_by': self.user_id }
		all_files = node_collection.collection.aggregate([
						{ "$match": query },
						{ "$unwind": "$rating" },
						{ "$group": { "_id": None, "count": { "$sum": 1 }, "rating": { "$addToSet": "$rating" } } }
					])
		if 'result' in all_files:
			result = all_files['result']
			if result:
				cnt = result[0]['count']
				rating_list = result[0]['rating']
				for rdict in rating_list:
					total_rating += rdict['score']
					if rdict['user_id'] not in unique_user_list:
						unique_user_list.append(rdict['user_id'])

				avg_rating_files = int(total_rating/float(cnt))
		t1 = time.time()
		time_diff = t1 - t0
		# print "\n get_ratings_received_on_user_files == ", time_diff
		return avg_rating_files,len(unique_user_list)



	def get_users_points(self):
		t0 = time.time()
		total_points = 0
		user_files = self.get_user_files_count()
		user_notes = self.get_user_notes_count()
		correct_attempted_quizitems = self.get_evaluated_quizitems_count(True,False)
		total_points = (user_files*25) + (user_notes*30) + (correct_attempted_quizitems*5)
		# print "\n get_users_points -- ",total_points
		return total_points
