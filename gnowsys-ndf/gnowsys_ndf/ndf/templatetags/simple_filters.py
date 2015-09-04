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


@register.filter
def split(str,splitter):
    return str.split(splitter)