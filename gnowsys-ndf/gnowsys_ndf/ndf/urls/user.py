from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.userDashboard',                       
                       url(r'^userpreference/', 'userpref',name='userpreference'),
                       url(r'^dashboard', 'uDashboard', name='dashboard'),                                            
                       url(r'^(?P<usrid>[\w-]+)/userDashboard$', 'dashboard', name='userDashboard'),  
                       url(r'^useractivity', 'user_activity', name='user_activity'),                                          
                       

                       url(r'^user_preference/(?P<auth_id>[\w-]+)$','user_preferences',name='user_preferences'),
                       
)

