from django.conf.urls import patterns, url

from django.views.generic import TemplateView

urlpatterns = patterns('gnowsys_ndf.ndf.views.file',
                        url(r'^(?P<file_id>[\w-]+)$', 'file', name='file'),
                        url(r'^uploadDoc/$', 'uploadDoc', name='uploadDoc'), #Direct ot html template                               
                        url(r'^submitDoc/', 'submitDoc', name='submitDoc'),
                        url(r'^submit/', 'submitDoc', name='submitDoc'),
                        url(r'^documentList/', 'GetDoc', name='documentList'),
                        url(r'^readDoc/(?P<_id>[\w-]+)/(?P<file_name>[^/]+)$', 'readDoc', name='read_file'),
                        url(r'^search/$', 'file_search', name='file_search'),
                        url(r'^file_detail/(?P<_id>[\w-]+)$', 'file_detail', name='file_detail'),
                        url(r'^fileThumbnail/(?P<_id>[\w-]+)$', 'getFileThumbnail', name='getFileThumbnail'),
                        url(r'^delete_file/(?P<_id>[\w-]+)$', 'delete_file', name='delete_file'),
                       
)
