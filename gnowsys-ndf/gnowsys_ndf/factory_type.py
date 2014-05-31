# factory data to create in database for gnowsys-ndf project


#append gsystem_type name to create factory GSystemType
factory_gsystem_types = [{'name':'Twist','meta_type':'factory_types'}, {'name':'Reply','meta_type':'factory_types'}, {'name':'Author','meta_type':'factory_types'}, {'name':'Shelf','meta_type':'factory_types'}, {'name':'QuizItem','meta_type':'factory_types'}, {'name':'Pandora_video','meta_type':'factory_types'},{'name':'Foundation Course','meta_type':'factory_types'}]


#fill attribute name,data_type,gsystem_type name in bellow dict to create factory Attribute Type
factory_attribute_types = [{'quiz_type':{'gsystem_names_list':['QuizItem'], 'data_type':'str(QUIZ_TYPE_CHOICES_TU)', 'meta_type':'factory_types'}},{'options':{'gsystem_names_list':['QuizItem'], 'data_type':'"[" + DATA_TYPE_CHOICES[6] + "]"', 'meta_type':'factory_types'}}, {'correct_answer':{'gsystem_names_list':['QuizItem'], 'data_type':'"[" + DATA_TYPE_CHOICES[6] + "]"','meta_type':'factory_types'}},{'start_time':{'gsystem_names_list':['QuizItem','Forum'], 'data_type':'DATA_TYPE_CHOICES[9]','meta_type':'factory_types'}}, {'end_time':{'gsystem_names_list':['QuizItem','Forum'], 'data_type':'DATA_TYPE_CHOICES[9]','meta_type':'factory_types'}}, {'module_set_md5':{'gsystem_names_list':['Module'], 'data_type':'u""','meta_type':'factory_types'}},{'source_id':{'gsystem_names_list':['Pandora_video'], 'data_type':'u""','meta_type':'factory_types'}},{'version':{'gsystem_names_list':['Module'], 'data_type':'u""', 'meta_type':'factory_types'}},{'apps_list':{'gsystem_names_list':['Group'],'data_type':'list','meta_type':'factory_types'}},{'user_preference_off':{'gsystem_names_list':['Author'],'data_type':'list','meta_type':'factory_types'}}]


#fill relation_type_name,inverse_name,subject_type,object_type in bellow dict to create factory Relation Type
factory_relation_types = [{'has_shelf':{'subject_type':['Author'],'object_type':['Shelf'], 'inverse_name':'shelf_of','meta_type':'factory_types'}}, {'translation_of':{'subject_type':['Page'],'object_type':['Page'], 'inverse_name':'translation_of', 'meta_type':'factory_types'}}, {'has_module':{'subject_type':['Page'],'object_type':['Module'], 'inverse_name':'generated_from', 'meta_type':'factory_types'}}, {'has_profile_pic':{'subject_type':['Author'],'object_type':['Image'], 'inverse_name':'profile_pic_of', 'meta_type':'factory_types'}}, {'has_course':{'subject_type':['Batch'],'object_type':['Foundation Course'], 'inverse_name':'course_of', 'meta_type':'factory_types'}}] 
