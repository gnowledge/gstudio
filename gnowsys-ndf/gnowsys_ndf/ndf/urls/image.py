from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.imageDashboard',
			url(r'^[/]$', 'imageDashboard', name='image'),
#                        url(r'^/(?P<image_id>[\w-]+)$', 'imageDashboard', name='image'),
                        #url(r'^images/', 'imageDashboard', name='imageDashboard'),                                                 
                        url(r'^/thumbnail/(?P<_id>[\w-]+)$', 'getImageThumbnail', name='getImageThumbnail'),
                        url(r'^/fullImage/(?P<_id>[\w-]+)/(?P<file_name>[^/]+)$', 'getFullImage', name='getFullImage'),
                        url(r'^/get_mid_size_img/(?P<_id>[\w-]+)$', 'get_mid_size_img', name='get_mid_size_img'),
                        url(r'^/image_search/$', 'image_search', name='image_search'),
                        url(r'^/(?P<_id>[\w-]+)$', 'image_detail', name='image_detail'),
                        url(r'^/details/(?P<_id>[\w-]+)$', 'image_detail', name='image_detail'),
                        url(r'^/edit/(?P<_id>[\w-]+)$', 'image_edit', name='image_edit'),

)
