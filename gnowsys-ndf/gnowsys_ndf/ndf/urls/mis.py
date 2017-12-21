from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.mis',
  url(r'^[/]$', 'mis_detail', name='mis'),
  url(r'^/reports/$', 'get_mis_reports', name='get_mis_reports'),
  # url(r'^/reports/data$', 'get_paged_reports_data', name='get_paged_reports_data'),
  url(r'^/(?P<app_id>[\w-]+)$', 'mis_detail', name='mis_list'),  # MIS app landing
  url(r'^/(?P<app_id>[\w-]+)/(?P<app_set_id>[\w-]+)$', 'mis_detail', name='mis_app_detail'),  # mis_app_detail
  url(r'^/(?P<app_id>[\w-]+)/(?P<app_set_id>[\w-]+)/enroll/(?P<app_set_instance_id>[\w-]+)$', 'mis_enroll', name='mis_enroll'),  # Person enrollment in Courses link
  # url(r'^/(?P<app_id>[\w-]+)/(?P<app_set_id>[\w-]+)/enroll/$', 'mis_enroll', name='mis_enroll'),  # Person enrollment in Courses link
  url(r'^/(?P<app_id>[\w-]+)/(?P<app_set_id>[\w-]+)/(?P<app_set_instance_id>[\w-]+)$', 'mis_detail', name='mis_app_instance_detail'),  # mis_app_instance_detail
  url(r'^/(?P<app_id>[\w-]+)/(?P<app_set_id>[\w-]+)/edit/(?P<app_set_instance_id>[\w-]+)/$', 'mis_create_edit', name='mis_app_instance_edit'),          # mis_app_instance_edit
  url(r'^/(?P<app_id>[\w-]+)/(?P<app_set_id>[\w-]+)/new/$', 'mis_create_edit', name='mis_app_instance_create'),  # mis_app_instance_create
)

