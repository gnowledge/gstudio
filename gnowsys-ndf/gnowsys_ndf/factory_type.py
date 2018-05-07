from gnowsys_ndf.settings import GSTUDIO_DEFAULT_GROUPS_LIST
# factory data to create in database for gnowsys-ndf project


#append gsystem_type name to create factory GSystemType
factory_gsystem_types = [{'name':'Twist','meta_type':'factory_types'},
                         {'name':'Reply','meta_type':'factory_types'},
                         {'name':'Author','meta_type':'factory_types'},
                         {'name':'Shelf','meta_type':'factory_types'},
                         {'name':'QuizItem','meta_type':'factory_types'},
                         {'name':'Pandora_video','meta_type':'factory_types'},
                         {'name':'NUSSD Course','meta_type':'factory_types'},
                         {'name':'task_update_history','meta_type':'factory_types'},
                         {'name':'Topic','meta_type':'factory_types'},
                         {'name':'Theme','meta_type':'factory_types'},
                         {'name':'theme_item','meta_type':'factory_types'},
                         {'name':'Concept','meta_type':'factory_types'},
                         {'name':'article','meta_type':'factory_types'},
                         {'name':'book','meta_type':'factory_types'},
                         {'name':'conference','meta_type':'factory_types'},
                         {'name':'inbook','meta_type':'factory_types'},
                         {'name':'incollection','meta_type':'factory_types'},
                         {'name':'inproceedings','meta_type':'factory_types'},
                         {'name':'manual','meta_type':'factory_types'},
                         {'name':'masterthesis','meta_type':'factory_types'},
                         {'name':'misc','meta_type':'factory_types'},
                         {'name':'phdthesis','meta_type':'factory_types'},
                         {'name':'proceedings','meta_type':'factory_types'},
                         {'name':'techreport','meta_type':'factory_types'},
                         {'name':'unpublished_entry','meta_type':'factory_types'},
                         {'name':'booklet','meta_type':'factory_types'},
                         {'name':'GList','meta_type':'factory_types'},
                         {'name':'GListItem','meta_type':'factory_types'},
                         {'name':'Group','meta_type':'factory_types'},
                         {'name':'ProgramEventGroup','meta_type':'factory_types'},
                         {'name':'CourseEventGroup','meta_type':'factory_types'},
                         {'name':'PartnerGroup','meta_type':'factory_types'},
                         {'name':'ModeratingGroup','meta_type':'factory_types'},
                         {'name':'Info page','meta_type':'factory_types'},
                         {'name':'Blog page','meta_type':'factory_types'},
                         {'name':'Wiki page','meta_type':'factory_types'},
                         {'name':'BaseCourseGroup','meta_type':'factory_types'}
                        ]


#fill attribute name,data_type,gsystem_type name in bellow dict to create factory Attribute Type
factory_attribute_types = [{'start_time':{'gsystem_names_list':['QuizItem','Forum','Task'],
                                          'data_type':'datetime.datetime',
                                          'meta_type':'factory_types'}},
                           {'end_time':{'gsystem_names_list':['QuizItem','Forum','Task'],
                                        'data_type':'datetime.datetime',
                                        'meta_type':'factory_types'}},
                           {'module_set_md5':{'gsystem_names_list':['Module'],
                                              'data_type':'u""',
                                              'meta_type':'factory_types'}},
                           {'source_id':{'gsystem_names_list':['Pandora_video','File', 'E-Book'],
                                         'data_type':'u""',
                                         'meta_type':'factory_types'}},
                           {'version':{'gsystem_names_list':['Module'],
                                       'data_type':'u""',
                                       'meta_type':'factory_types'}},
                           {'apps_list':{'gsystem_names_list':['Group','Author'],
                                         'data_type':'list',
                                         'meta_type':'factory_types'}},
                           {'user_preference_off':{'gsystem_names_list':['Author'],
                                                   'data_type':'list',
                                                   'meta_type':'factory_types'}},
                           {'Status':{'gsystem_names_list':['Task'],
                                      'data_type':'basestring',
                                      'meta_type':'factory_types'}},
                           {'Priority':{'gsystem_names_list':['Task'],
                                        'data_type':'basestring',
                                        'meta_type':'factory_types'}},
                           {'Assignee':{'gsystem_names_list':['Task'],
                                        'data_type':'list',
                                        'meta_type':'factory_types'}},
                           {'Upload_Task':{'gsystem_names_list':['Task'],
                                        'data_type':'list',
                                        'meta_type':'factory_types'}},
                           {'Estimated_time':{'gsystem_names_list':['Task'],
                                              'data_type':'float',
                                              'meta_type':'factory_types'}},
                           {'age_range':{'gsystem_names_list':['Quiz','Topic','File','Page','Pandora_video', 'E-Book','Jsmol','Asset'],
                                         'data_type':'basestring',
                                         'meta_type':'factory_types'}},
                           {'audience':{'gsystem_names_list':['Quiz','Topic','File','Page','Pandora_video', 'E-Book','Jsmol','Asset'],
                                        'data_type':'list',
                                        'meta_type':'factory_types'}},
                           {'creator':{'gsystem_names_list':['Quiz','Topic','File','Page','Pandora_video', 'E-Book','Jsmol'],
                                        'data_type':'basestring',
                                        'meta_type':'factory_types'}},
                           {'other_contributors':{'gsystem_names_list':['Quiz','Topic','File','Page','Pandora_video', 'E-Book','Jsmol','Asset'],
                                        'data_type':'list',
                                        'meta_type':'factory_types'}},
                           {'timerequired':{'gsystem_names_list':['Quiz','Topic','File','Page','Pandora_video', 'E-Book','Jsmol','Asset'],
                                            'data_type':'basestring',
                                            'meta_type':'factory_types'}},
                           {'interactivitytype':{'gsystem_names_list':['Quiz','Topic','File','Page','Pandora_video','Jsmol','Asset'],
                                                 'data_type':'basestring',
                                                 'meta_type':'factory_types'}},
                           {'basedonurl':{'gsystem_names_list':['Quiz','Topic','File','Page','Pandora_video', 'E-Book','Jsmol','Asset'],
                                          'data_type':'basestring',
                                          'meta_type':'factory_types'}},
                           {'educationaluse':{'gsystem_names_list':['Quiz','Topic','File','Page','Pandora_video', 'E-Book','Jsmol','Asset'],
                                              'data_type':'basestring',
                                              'meta_type':'factory_types'}},
                           {'textcomplexity':{'gsystem_names_list':['Quiz','Topic','File','Page','Pandora_video', 'E-Book','Jsmol','Asset'],
                                              'data_type':'basestring',
                                              'meta_type':'factory_types'}},
                           {'readinglevel':{'gsystem_names_list':['Quiz','Topic','File','Page','Pandora_video', 'E-Book','Jsmol','Asset'],
                                            'data_type':'basestring',
                                            'meta_type':'factory_types'}},
                           {'educationalsubject':{'gsystem_names_list':['Quiz','Topic','File','Page','Pandora_video', 'E-Book','Jsmol', 'base_unit','Asset', 'announced_unit', 'Module'],
                                                  'data_type':'basestring',
                                                  'meta_type':'factory_types'}},
                           {'educationallevel':{'gsystem_names_list':['Quiz','Topic','File','Page','Pandora_video', 'E-Book','Jsmol', 'base_unit','Asset', 'announced_unit', 'Module', 'Author'],
                                                'data_type':'list',
                                                'meta_type':'factory_types'}},
                           {'educationalalignment':{'gsystem_names_list':['Quiz','QuizItem','Topic','File','Page','NUSSD Course', 'Pandora_video', 'Theme', 'E-Book','Jsmol','Asset'],
                                                    'data_type':'basestring',
                                                    'meta_type':'factory_types'}},
                           {'curricular':{'gsystem_names_list':['File','Page', 'Pandora_video', 'Theme', 'E-Book','Jsmol','Asset'],
                                         'data_type':'bool',
                                         'meta_type':'factory_types'}},
                           {'source':{'gsystem_names_list':['File', 'Page', 'Pandora_video', 'E-Book','Jsmol','Asset'],
                                      'data_type':'basestring',
                                      'meta_type':'factory_types'}},
                           {'adaptation_of':{'gsystem_names_list':['File','Page', 'Pandora_video', 'E-Book','Jsmol'],
                                             'data_type':'basestring',
                                             'meta_type':'factory_types'}},
                           {'name_eng':{'gsystem_names_list':['File', 'Page', 'Pandora_video', 'E-Book'],
                                      'data_type':'basestring',
                                      'meta_type':'factory_types'}},
                           {'description_eng':{'gsystem_names_list':['File','Page','Pandora_video', 'E-Book'],
                                      'data_type':'basestring',
                                      'meta_type':'factory_types'}},
                           {'BibTex_entry':{'gsystem_names_list':['conference','inbook','inproceedings','manual','masterthesis','misc','phdthesis','proceedings','techreport','unpublished_entry','incollection','article','book','booklet'],
                                            'data_type':'basestring',
                                            'meta_type':'factory_types'}},
                           {'website':{'gsystem_names_list':["PartnerGroup"],
                                        'data_type':'basestring',
                                        'meta_type':'factory_types'}},
                           {'Citation':{'gsystem_names_list':['conference','inbook','inproceedings','manual','masterthesis','misc','phdthesis','proceedings','techreport','unpublished_entry','incollection','article','book','booklet'],
                                        'data_type':'basestring',
                                        'meta_type':'factory_types'}},
                           {'release_response':{'gsystem_names_list':['Twist'],
                                        'data_type':'bool',
                                        'meta_type':'factory_types'}},
                           {'thread_interaction_type':{'gsystem_names_list':['Twist'],
                                        'data_type':'basestring',
                                        'meta_type':'factory_types'}},
                           {'co_contributors': {'gsystem_names_list':['Page', 'File', 'E-Book','Jsmol'],
                                        'data_type':'basestring',
                                        'meta_type':'factory_types'}},
                           {'entry_list':{'gsystem_names_list':['conference','inbook','inproceedings','manual','masterthesis','misc','phdthesis','proceedings','techreport','unpublished_entry','incollection','article','book','booklet'],
                                          'data_type':'basestring',
                                          'meta_type':'factory_types'}}]

# the following types are useful when BibApp's second phase
# development begins. Currently this data is not set as attributes
# {'author':{'gsystem_names_list':['book'],
# 'data_type':'basestring','meta_type':'factory_types'}},
# {'title':{'gsystem_names_list':['book'],
# 'data_type':'basestring','meta_type':'factory_types'}},
# {'publisher':{'gsystem_names_list':['book'],
# 'data_type':'basestring','meta_type':'factory_types'}},
# {'year':{'gsystem_names_list':['book'],
# 'data_type':'basestring','meta_type':'factory_types'}},
# {'volume':{'gsystem_names_list':['book'],
# 'data_type':'basestring','meta_type':'factory_types'}},
# {'edition':{'gsystem_names_list':['book'],
# 'data_type':'basestring','meta_type':'factory_types'}},
# {'month':{'gsystem_names_list':['book'],
# 'data_type':'basestring','meta_type':'factory_types'}},
# {'key':{'gsystem_names_list':['book'],
# 'data_type':'basestring','meta_type':'factory_types'}},
# {'note':{'gsystem_names_list':['book'],
# 'data_type':'basestring','meta_type':'factory_types'}},


#fill relation_type_name,inverse_name,subject_type,object_type in bellow dict to create factory Relation Type
factory_relation_types = [
    {'has_shelf': {
            'subject_type':['Author'],
            'object_type':['Shelf'],
            'inverse_name':'shelf_of',
            'meta_type':'factory_types'
        }
    },

    {'translation_of': {
            'subject_type':['*'],
            'object_type':['*'],
            # 'subject_type':['Page','Topic','Theme','theme_item','File','GAPP','factory_types','Binary'],
            # 'object_type':['Page','Topic','Theme','theme_item','File','GAPP','factory_types','Binary'],
            'inverse_name':'translation_of',
            'meta_type':'factory_types',
            'object_cardinality': 100,
            'is_reflexive': True,
            'is_transitive': True
        }
    },

    {'has_module': {
            'subject_type':['Page'],
            'object_type':['Module'],
            'inverse_name':'generated_from',
            'meta_type':'factory_types'
        }
    },

    {'has_profile_pic': {
            'subject_type':['Author','Group','ModeratingGroup','CourseEventGroup','ProgramEventGroup','PartnerGroup', 'BaseCourseGroup','Module'],
            'object_type':['Image','File'],
            'inverse_name':'profile_pic_of',
            'meta_type':'factory_types'
        }
    },

    {'has_banner_pic': {
            'subject_type':['Author','Group','ModeratingGroup','CourseEventGroup','ProgramEventGroup','PartnerGroup', 'BaseCourseGroup', 'announced_unit','Module'],
            'object_type':['Image','File'],
            'inverse_name':'banner_pic_of',
            'meta_type':'factory_types'
        }
    },

    {'teaches': {
            'subject_type':['Page','File', 'Topic','Pandora_video','Asset'],
            'object_type':['Page','Concept','Topic', 'File', 'Pandora_video'],
            'inverse_name':'taught_by',
            'meta_type':'factory_types',
            'object_cardinality': 100
        }
    },

    {'assesses': {
            'subject_type':['Quiz','QuizItem'],
            'object_type':['Topic','Concept','Page','Quiz','QuizItem'],
            'inverse_name':'assessed_by',
            'meta_type':'factory_types'
        }
    },

    {'has_bib_types': {
            'subject_type':['Bib_App'],
            'object_type':['conference','inbook','inproceedings','incollection','manual','masterthesis','misc','phdthesis','proceedings','techreport','unpublished_entry','article','booklet','book'],
            'inverse_name':'bib_type_of',
            'meta_type':'factory_types'
        }
    },

    {'has_type': {
            'subject_type': ['Task'],
            'object_type': ['GList'],
            'inverse_name': 'is_type_of',
            'meta_type': 'factory_types',
            'object_cardinality': 1
        }
    },

    {'has_cover_page': {
            'subject_type': ['File'],
            'object_type': ['File'],
            'inverse_name': 'cover_page_of',
            'meta_type': 'factory_types',
            'object_cardinality': 1
        }
    },

    {'has_thumbnail': {
            'subject_type': ['Page', 'File','Jsmol'],
            'object_type': ['File'],
            'inverse_name': 'thumbnail_of',
            'meta_type': 'factory_types',
            'member_of': 'Binary',
            'object_cardinality': 1
        }
    },

    {'has_help': {
            'subject_type':['*'],
            'object_type':['*'],
            'inverse_name':'help_of',
            'meta_type':'factory_types',
            'member_of': 'Binary',
            'object_cardinality': 100
        }
    },

    {'has_admin_page': {
            'subject_type':['*'],
            'object_type':['*'],
            'inverse_name':'admin_page_of',
            'meta_type':'factory_types',
            'member_of': 'Binary',
            'object_cardinality': 100
        }
    },

]


factory_default_groups = GSTUDIO_DEFAULT_GROUPS_LIST