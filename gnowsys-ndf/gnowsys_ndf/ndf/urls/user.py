from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.userDashboard',                       
                       url(r'^userDashboard/', 'dashboard', name='userDashboard'),                                            
                       url(r'^user_preference/(?P<auth_id>[\w-]+)$','user_preferences',name='user_preferences'),
                       
)

