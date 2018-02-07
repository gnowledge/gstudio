from django.conf.urls import patterns, url, include

from django.views.generic import TemplateView

urlpatterns = patterns('gnowsys_ndf.ndf.views.file',
                       url(r'^[/]$', 'file', name='file'),
                       # url(r'^/(?P<file_id>[\w-]+)$', 'file', name='file'),
                       url(r'^/uploadDoc/$', 'uploadDoc', name='uploadDoc'), #Direct ot html template                               
                       url(r'^/submitDoc/', 'submitDoc', name='submitDoc'),
                       url(r'^/submit/', 'submitDoc', name='submitDoc'),
                       url(r'^/documentList/', 'GetDoc', name='documentList'),
                       url(r'^/readDoc/', include('gnowsys_ndf.ndf.urls.readDoc')),
                       url(r'^/search/$', 'file_search', name='file_search'),
                       url(r'^/details/(?P<_id>[\w-]+)$', 'file_detail', name='file_detail'),
                       url(r'^/(?P<_id>[\w-]+)$', 'file_detail', name='file_detail'),
                       url(r'^/thumbnail/(?P<_id>[\w-]+)$', 'getFileThumbnail', name='getFileThumbnail'),
                       #url(r'^/delete_file/(?P<_id>[\w-]+)$', 'delete_file', name='delete_file'),
                       url(r'^/delete/(?P<_id>[\w-]+)$', 'delete_file', name='delete_file'),
                       url(r'^/edit_file/(?P<_id>[\w-]+)$', 'file_edit', name='file_edit'),
                       # url(r'^/data-review/$', 'data_review', name='data_review'),
                       # url(r'^/data-review/page-no=(?P<page_no>\d+)/$', 'data_review', name='data_review_page'),
                       # url(r'^/data-review/save/$', 'data_review_save', name='data_review_save'),
                       url(r'^/edit/(?P<_id>[\w-]+)$', 'file_edit', name='file_edit'),
                       url(r'^/(?P<filetype>[\w-]+)/page-no=(?P<page_no>\d+)/$', 'paged_file_objs', name='paged_file_objs'),
                       url(r'^/file_content/$', 'file_content', name='file_content'),
)

