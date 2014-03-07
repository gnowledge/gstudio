from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.userDashboard',                       
                       url(r'^(?P<user>[^/]+)/(?P<uploaded>[^/]+)/userDashboard', 'dashboard', name='userDashboard')                                             
                       
)

