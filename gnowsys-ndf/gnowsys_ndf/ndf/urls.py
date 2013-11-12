from django.conf.urls import patterns, url

from django.views.generic import TemplateView

from gnowsys_ndf.ndf.views import *

urlpatterns = patterns('gnowsys_ndf.ndf.views.home',
                       url(r'^$', 'homepage', name='homepage'),
)

urlpatterns += patterns('gnowsys_ndf.ndf.views.group',
                       url(r'^create_group/', 'create_group', name='create_group'),
)

urlpatterns += patterns('gnowsys_ndf.ndf.views.wikipage',
                        url(r'^wikipage/', 'wikipage', name='wikipage'),
                        url(r'^create_wiki/', 'create_wiki', name='create_wiki'),
                        url(r'^resources/page/(?P<page_id>[\w-]+)$', 'display_page', name='display_page'),
                        url(r'^delete/(?P<_id>[\w-]+)$', 'delete_node', name='delete_node'),
)

urlpatterns += patterns('gnowsys_ndf.ndf.views.doc',
                        url(r'^uploadDoc/$', TemplateView.as_view(template_name='ndf/UploadDoc.html')), #Direct ot html template
                        url(r'^submitDoc/', 'submitDoc', name='submitDoc'),
                        url(r'^submit/', 'submitDoc', name='submitDoc'),
                        url(r'^documentList/', 'GetDoc', name='documentList'),
                        url(r'^readDoc/(?P<_id>[\w-]+)$', 'readDoc', name='read_file'),
)
                       
urlpatterns += patterns('gnowsys_ndf.ndf.views.ajax-views',
                        url(r'^ajax/edit_content/', 'edit_content', name='edit_content'),
)
