''' -- imports from python libraries -- '''
# import os -- Keep such imports here


''' -- imports from installed packages -- '''
from django.shortcuts import render_to_response, render
from django.template import RequestContext

###########################################################################

def homepage(request):
    return render_to_response("ndf/base.html", context_instance=RequestContext(request))
