from django.conf.urls.defaults import patterns, include, url
from django.views.generic import ListView, DetailView
from django.views.generic import TemplateView
from gstudio_mdb.models import Node
from gstudio_mdb.views import NodeDetailView, NodeRelationsView
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', ListView.as_view(
        queryset=Node.objects.all(),
        context_object_name="node_list"),
        name="home"
    ),
    url(r'^node/(?P<slug>[a-zA-Z0-9-]+)/$', NodeDetailView.as_view(
        queryset=Node.objects.all(),
        context_object_name="node"),
        name="node"
    ),
    url(r'^admin/', include(admin.site.urls)),

)
