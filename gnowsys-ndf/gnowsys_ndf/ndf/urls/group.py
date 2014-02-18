from django.conf.urls import patterns, url

from django.views.generic import TemplateView

from gnowsys_ndf.ndf.views import *

urlpatterns = patterns('gnowsys_ndf.ndf.views.group',
                       	url(r'^$','group_dashboard', name='groupchange'),
                       	url(r'^(?P<app_id>[\w-]+)$', 'group', name='group'),
                       	url(r'^create_group/', 'create_group', name='create_group'),

		       			url(r'^(?P<group_id>[\w-]+)/edit_group/', 'edit_group', name='edit_group')
)
urlpatterns += patterns('gnowsys_ndf.ndf.views.ajax-views',
                        url(r'^check_group/', 'checkgroup', name='check_group'),

)
urlpatterns += patterns('gnowsys_ndf.ndf.views.notify',
                        url(r'^notify/join/$', 'notifyuser', name='notifyuser'),
                        url(r'^notify/remove/$', 'notify_remove_user', name='notifyremuser'),
                        url(r'^notify/send_invitation/$', 'send_invitation', name='sendinvitation'),

)
