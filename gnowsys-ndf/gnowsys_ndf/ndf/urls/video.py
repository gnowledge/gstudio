from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.videoDashboard',
                        url(r'^(?P<video_id>[\w-]+)$', 'videoDashboard', name='video'),
                        #url(r'^videos/', 'videoDashboard', name='videoDashboard'),              
                        url(r'^videoThumbnail/(?P<_id>[\w-]+)$', 'getvideoThumbnail', name='getvideoThumbnail'),
                        url(r'^fullvideo/(?P<_id>[\w-]+)$', 'getFullvideo', name='getFullvideo'),
                        url(r'^video_search/$', 'video_search', name='video_search'),
                        url(r'^video_detail/(?P<_id>[\w-]+)$', 'video_detail', name='video_detail'),
                        url(r'^video_edit/(?P<_id>[\w-]+)$', 'video_edit', name='video_edit')
)
