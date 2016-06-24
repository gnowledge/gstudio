''' -- Imports from python libraries -- '''
import datetime
import json
import pymongo
import re


''' -- imports from installed packages -- '''
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, redirect, render
from django.template import RequestContext
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.core.files.storage import get_valid_filename
from django.core.files.move import file_move_safe
from django.core.files.temp import gettempdir
from django.core.files.uploadedfile import UploadedFile # django file handler
from mongokit import paginator
from gnowsys_ndf.ndf.org2any import org2html
from gnowsys_ndf.ndf.models import *
from pymongo import Connection


def map_view(request):

	return render_to_response("ndf/map_india.html",{ 'group_id':"home", 'groupid':"home" }
		, context_instance=RequestContext(request))