from django import template
# from datetime import date, timedelta

from gnowsys_ndf.ndf.views.methods import get_execution_time

register = template.Library()


# @get_execution_time
# @register.filter
# def list_of_dicts_to_dict(list_of_dicts):
	
# 	req_dict = {}
# 	[req_dict.update(d) for d in list_of_dicts]

# 	return req_dict


@get_execution_time
@register.assignment_tag
def get_dict_from_list_of_dicts(list_of_dicts):
	req_dict = {}
	[req_dict.update(d) for d in list_of_dicts]
	return req_dict


@get_execution_time
@register.filter
def split(str, splitter):
    return str.split(splitter)


@get_execution_time
@register.simple_tag
def get_latest_git_hash():
	"""
	Template tag that returns latest git hash no.

	Returns:
	    str: Returned hash no is 7 digit smaller unique (hash).
	"""
	import subprocess
	# gitproc = subprocess.Popen(['git', 'rev-parse', '--short', 'HEAD'], stdout = subprocess.PIPE)
	# (stdout, _) = gitproc.communicate()
	return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])
