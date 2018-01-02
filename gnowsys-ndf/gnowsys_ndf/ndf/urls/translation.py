from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.translation',

			# show all translations of provided node
			url(r'^/(?P<node_id>[\w-]+)/translations/?$', 'all_translations', name='all_translations'),

			# for VIEW/READ: show translated provided node to provided LANG CODE
			# lang could be either proper/full language-name/language-code
			url(r'^/(?P<node_id>[\w-]+)/translation/(?P<lang>[\w-]+)/?$', 'show_translation', name='show_translation'),

			# for EDIT: translate provided node to provided LANG CODE
			# lang could be either proper/full language-name/language-code
			url(r'^/(?P<node_id>[\w-]+)/translate/(?P<lang>[\w-]+)/?$', 'translate', name='translate'),
			url(r'^/(?P<node_id>[\w-]+)/translate/(?P<lang>[\w-]+)/(?P<translated_node_id>[\w-]+)/?$', 'translate', name='translated'),

)
