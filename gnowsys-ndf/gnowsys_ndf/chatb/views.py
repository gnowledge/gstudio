# Create your views here.
from django.http import HttpResponse
import datetime
from django.template import RequestContext,Context
from django.shortcuts import render_to_response,render
def chatb_view(request,offset):
	try:
		offset=int(offset)
	except ValueError:
		raise Http404()
	
	now=datetime.datetime.now()
	#t=get_template('chatb_template.html')
	#t=Template("<html><body>It is now {{current_date}} .</body></html>" )
	#html=t.render(Context({'current_date':now}))
	context = RequestContext(request , {'current_date': now})
	#return render_to_response("chatb_template.html",context) #HttpResponse(html)
	return render_to_response("chatb_index.html",context) #HttpResponse(html)
