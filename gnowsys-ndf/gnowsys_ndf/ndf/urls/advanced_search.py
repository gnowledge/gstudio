from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.advanced_search',
                        
                        url(r'^$', 'search_detail',name='advanced_search'),
                        
)
