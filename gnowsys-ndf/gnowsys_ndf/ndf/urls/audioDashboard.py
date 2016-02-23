from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.audioDashboard',
			url(r'^[/]$', 'audioDashboard', name='audio'),
                        # url(r'^/get_audio_file/(?P<_id>[\w-]+)$', 'get_audio_file', name='get_audio_file'),
# #                       url(r'^/(?P<image_id>[\w-]+)$', 'imageDashboard', name='image'),
#                         #url(r'^images/', 'imageDashboard', name='imageDashboard'),                                                 
#                         url(r'^/thumbnail/(?P<_id>[\w-]+)$', 'getImageThumbnail', name='getImageThumbnail'),
#                         url(r'^/fullImage/(?P<_id>[\w-]+)/(?P<file_name>[^/]+)$', 'getFullImage', name='getFullImage'),
#                         url(r'^/image_search/$', 'image_search', name='image_search'),
#                         url(r'^/(?P<_id>[\w-]+)$', 'image_detail', name='image_detail'),
#                         url(r'^/details/(?P<_id>[\w-]+)$', 'image_detail', name='image_detail'),
#                         url(r'^/edit/(?P<_id>[\w-]+)$', 'image_edit', name='image_edit'),

)
