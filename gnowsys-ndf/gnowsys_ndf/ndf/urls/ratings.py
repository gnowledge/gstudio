from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.ratings',
                       url(r'^/add_ratings/','ratings', name='nameratings'),
)
