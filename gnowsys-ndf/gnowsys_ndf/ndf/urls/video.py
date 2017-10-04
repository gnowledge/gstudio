from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.videoDashboard',
                        url(r'^[/]$', 'videoDashboard', name='video'),   
                        url(r'^/thumbnail/(?P<_id>[\w-]+)$', 'getvideoThumbnail', name='getvideoThumbnail'),
                        url(r'^/fullvideo/(?P<_id>[\w-]+)$', 'getFullvideo', name='getFullvideo'),
                        url(r'^/video_search/$', 'video_search', name='video_search'),
                        url(r'^/(?P<_id>[\w-]+)$', 'video_detail', name='video_detail'),
                        url(r'^/details/(?P<_id>[\w-]+)$', 'video_detail', name='video_detail'),
                        url(r'^/edit/(?P<_id>[\w-]+)$', 'video_edit', name='video_edit')
)
