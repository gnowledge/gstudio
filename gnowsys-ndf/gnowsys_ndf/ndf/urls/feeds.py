from django.conf.urls import patterns, url

from django.views.generic import TemplateView

from gnowsys_ndf.ndf.views import feeds

from gnowsys_ndf.ndf.views.feeds import activity_feed


urlpatterns = patterns('gnowsys_ndf.ndf.views.feeds',  
    
    # URL for registering custom actions through AJAX
    url(r'^/updates[/]$', activity_feed(), name='activity_feed')
)
