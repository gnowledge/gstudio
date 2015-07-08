from django.conf.urls import patterns, url

urlpatterns = patterns('gnowsys_ndf.ndf.views.trash',     
		 	url(r'^/delete/(?P<node_id>[\w-]+)$', 'trash_resource',name='trash_resource'),		
		 	  )                  


