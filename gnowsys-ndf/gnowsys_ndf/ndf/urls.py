from django.conf.urls import patterns, url

from django.views.generic import TemplateView

from gnowsys_ndf.ndf.views import *

urlpatterns = patterns('gnowsys_ndf.ndf.views.home',
                       url(r'^$', 'homepage', name='homepage'),
)

urlpatterns += patterns('gnowsys_ndf.ndf.views.page',
                        url(r'^apps/page/(?P<page_id>[\w-]+)$', 'page', name='page'),
                        url(r'^create_page/', 'create_page', name='create_page'),
                        url(r'^page/(?P<node_id>[\w-]+)$', 'edit_page', name='edit_page'),
                        #url(r'^page/(?P<node_id>[\w-]+)$', 'display_page', name='display_page'),
)

urlpatterns += patterns('gnowsys_ndf.ndf.views.group',
                        url(r'^apps/group/(?P<group_id>[\w-]+)$', 'group', name='group'),
                        url(r'^create_group/', 'create_group', name='create_group'),
)

urlpatterns += patterns('gnowsys_ndf.ndf.views.file',
                        url(r'^apps/file/(?P<file_id>[\w-]+)$', 'file', name='file'),
                        #url(r'^uploadDoc/$', TemplateView.as_view(template_name='ndf/UploadDoc.html')), #Direct ot html template
                        # url(r'^uploadDoc/(?P<pageurl>\w+)/$', 'uploadDoc', name='uploadDoc'), #Direct ot html template
                        url(r'^uploadDoc/$', 'uploadDoc', name='uploadDoc'), #Direct ot html template
                        url(r'^submitDoc/', 'submitDoc', name='submitDoc'),
                        url(r'^submit/', 'submitDoc', name='submitDoc'),
                        url(r'^documentList/', 'GetDoc', name='documentList'),
                        url(r'^readDoc/(?P<_id>[\w-]+)$', 'readDoc', name='read_file'),
)

urlpatterns += patterns('gnowsys_ndf.ndf.views.imageDashboard',
                        url(r'^gapp/image/(?P<image_id>[\w-]+)$', 'imageDashboard', name='image'),
                        #url(r'^images/', 'imageDashboard', name='imageDashboard'),
                        url(r'^imageThumbnail/(?P<_id>[\w-]+)$', 'getImageThumbnail', name='getImageThumbnail'),
                        url(r'^fullImage/(?P<_id>[\w-]+)$', 'getFullImage', name='getFullImage'),
)
                       
urlpatterns += patterns('gnowsys_ndf.ndf.views.ajax-views',
                        #url(r'^ajax/.../', '...', name='...'),
)
