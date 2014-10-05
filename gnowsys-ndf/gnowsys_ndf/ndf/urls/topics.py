from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.topics',
					   url(r'^$', 'themes', name='theme_page'),
                       url(r'^/(?P<app_id>[\w-]+)$', 'themes', name='theme_page'),
                       url(r'^/(?P<app_id>[\w-]+)/(?P<app_set_id>[\w-]+)$', 'themes', name='theme_list'),
                       url(r'^/(?P<app_set_id>[\w-]+)/', 'theme_topic_create_edit', name='theme_topic_create')

)