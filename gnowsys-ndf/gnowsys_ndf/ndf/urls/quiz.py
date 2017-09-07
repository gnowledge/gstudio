from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.quiz',
                       url(r'^[/]$', 'quiz', name='quiz'),
                       url(r'^/question/create/$', 'create_edit_quiz_item', name='quiz_item_create'),
                       url(r'^/create/', 'create_edit_quiz', name='quiz_create'),
                       url(r'^/details/(?P<node_id>[\w-]+)$', 'quiz_details', name='quiz_details'),
                       url(r'^/details/(?P<node_id>[\w-]+)$', 'quiz_details', name='quizitemevent_detail'),
                       url(r'^/details/(?P<node_id>[\w-]+)$', 'quiz_details', name='quizitem_detail'),
                       # url(r'^/(?P<quiz_node_id>[\w-]+)/question/edit/(?P<node_id>[\w-]+)$', 'create_edit_quiz_item', name='quiz_item_edit'),
                       url(r'^/question/edit/(?P<node_id>[\w-]+)$', 'create_edit_quiz_item', name='quiz_item_edit'),
                       url(r'^/edit/(?P<node_id>[\w-]+)$', 'create_edit_quiz', name='quiz_edit'),
                       url(r'^/save_quizitem_answer/', 'save_quizitem_answer', name='save_quizitem_answer'),
                       url(r'^/question/detail/(?P<node_id>[\w-]+)$', 'quiz_item_detail', name='quiz_item_detail'),
                       url(r'^/question/(?P<node_id>[\w-]+)/translate/(?P<lang>[\w-]+)/?$', 'create_edit_quiz_item', name='quiz_item_translate_create'),
                       url(r'^/question/(?P<node_id>[\w-]+)/translate/(?P<trans_node_id>[\w-]+)/(?P<lang>[\w-]+)/?$', 'create_edit_quiz_item', name='quiz_item_translate_edit'),

                       # url(r'^(?P<node_id>[\w-]+)/version/(?P<version_no>\d+\.\d+)$', 'version_node', name='node_version'),
)
