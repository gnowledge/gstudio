from gnowsys_ndf.ndf.models import *
import send_page

def update_page(name,content,id):
	gst_page = node_collection.one({u'_id':ObjectId(id)})
	gst_page.name = unicode(name)
	gst_page.content = unicode(content)

	try:
		gst_page.save()
	except:
		print 'in except'