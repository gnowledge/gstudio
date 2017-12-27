from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.unit',
                        # list
                        url(r'^[/]?$', 'list_units', name='list_units'),
                        # create
                        url(r'^/create/?$', 'unit_create_edit', name='unit_create_edit'),
                        # edit
                        url(r'^/edit/(?P<unit_group_id>[\w-]+)/?$', 'unit_create_edit', name='unit_edit'),
                        # detail
                        url(r'^/lessons/$', 'unit_detail', name='unit_detail'),
                        # url(r'^/(?P<unit_group_id>[\w-]+)/?$', 'unit_detail', name='unit_detail'),

                        # LESSON
                        # create
                        url(r'^/lesson/create/?$', 'lesson_create_edit', name='lesson_create_edit'),


                        # ACTIVITY
                        # create
                        url(r'^/activity/create/?$', 'activity_create_edit', name='activity_create_edit'),
)
