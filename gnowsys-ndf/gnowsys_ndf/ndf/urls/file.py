

from django.conf.urls import patterns, url

from django.views.generic import TemplateView

from gnowsys_ndf.ndf.views import *




urlpatterns = patterns('gnowsys_ndf.ndf.views.file',
                        url(r'^(?P<file_id>[\w-]+)$', 'file', name='file'),
                        #url(r'^uploadDoc/$', TemplateView.as_view(template_name='ndf/UploadDoc.html')), #Direct ot html template  
                        # url(r'^uploadDoc/(?P<pageurl>\w+)/$', 'uploadDoc', name='uploadDoc'), #Direct ot html template            
                        url(r'^uploadDoc/$', 'uploadDoc', name='uploadDoc'), #Direct ot html template                               
                        url(r'^submitDoc/', 'submitDoc', name='submitDoc'),
                        url(r'^submit/', 'submitDoc', name='submitDoc'),
                        url(r'^documentList/', 'GetDoc', name='documentList'),
                        url(r'^readDoc/(?P<_id>[\w-]+)$', 'readDoc', name='read_file'),
                        url(r'^search/$', 'file_search', name='file_search'),
                       
)
