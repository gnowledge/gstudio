from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.userDashboard',                       
                       url(r'^(?P<user>[^/]+)/userDashboard', 'dashboard', name='userDashboard')                      
                       
                       
)

