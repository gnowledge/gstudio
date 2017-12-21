from django import template
from django.template.loader_tags import do_extends
# from datetime import date, timedelta
from django.template.defaultfilters import stringfilter

import tokenize
import StringIO

from gnowsys_ndf.ndf.views.methods import get_execution_time

register = template.Library()


# @get_execution_time
# @register.filter
# def list_of_dicts_to_dict(list_of_dicts):
	
# 	req_dict = {}
# 	[req_dict.update(d) for d in list_of_dicts]

# 	return req_dict


register = template.Library()

class XExtendsNode(template.Node):
    def __init__(self, node, kwargs):
        self.node = node
        self.kwargs = kwargs

    def render(self, context):
        # TODO: add the values to the bottom of the context stack instead?
        context.update(self.kwargs)
        try:
           return self.node.render(context)
        finally:
           context.pop()

def do_xextends(parser, token):
    bits = token.contents.split()
    kwargs = {}
    if 'with' in bits:
        pos = bits.index('with')
        argslist = bits[pos+1:]
        bits = bits[:pos]
        for i in argslist:
            try:
                a, b = i.split('=', 1); a = a.strip(); b = b.strip()
                keys = list(tokenize.generate_tokens(StringIO.StringIO(a).readline))
                if keys[0][0] == tokenize.NAME:
                    kwargs[str(a)] = parser.compile_filter(b)
                else: raise ValueError
            except ValueError:
                raise template.TemplateSyntaxError, "Argument syntax wrong: should be key=value"
        # before we are done, remove the argument part from the token contents,
        # or django's extends tag won't be able to handle it.
        # TODO: find a better solution that preserves the orginal token including whitespace etc.
        token.contents = " ".join(bits)

    # let the orginal do_extends parse the tag, and wrap the ExtendsNode
    return XExtendsNode(do_extends(parser, token), kwargs)

register.tag('xextends', do_xextends)
'''
	Examples:
		{% xextends "base.html" %}
		{% xextends "base.html" with first_body_column=3 %}
		{% xextends "base.html" with some_arg_to_pass="sample_value" %}
'''


@get_execution_time
@register.assignment_tag
def get_dict_from_list_of_dicts(list_of_dicts,convert_objid_to_str=False):
    req_dict = {}
    [req_dict.update(d) for d in list_of_dicts]
    if convert_objid_to_str:
        str_val_dict = {key: map(str,val) for key, val in req_dict.items()}
        return str_val_dict
    return req_dict


@get_execution_time
@register.filter
def split(str, delimiter):
    return str.split(delimiter)

@get_execution_time
@register.filter
def apply_eval(arg):
    import ast
    return ast.literal_eval(arg)


@register.filter
def joinby(delimiter, arg):
    return arg.join(delimiter)

@register.filter
@stringfilter
def re_format(value):
    import re
    l = []
    if value:
        value = eval(value)
        for e in value:
            l.append(re.sub(r'[\r]', '', e))
    return l

@get_execution_time
@register.assignment_tag
def get_latest_git_hash():
	"""
	Template tag that returns latest git hash no.

	Returns:
	    str: Returned hash no is 7 digit smaller unique (hash).
	"""
	# import subprocess
	# gitproc = subprocess.Popen(['git', 'rev-parse', '--short', 'HEAD'], stdout = subprocess.PIPE)
	# (stdout, _) = gitproc.communicate()
	# return stdout.strip()

	import os
	git_commit_hash = os.popen("git rev-parse --short HEAD").read().strip()
	return git_commit_hash

@get_execution_time
@register.assignment_tag
def get_active_branch_name():
    """
    Template tag that returns current active git branch.

    Returns:
        str: branch-name
    """

    import os
    git_branch_name = os.popen("git rev-parse --abbrev-ref HEAD").read().strip()
    return git_branch_name

@get_execution_time
@register.filter
def get_type(value):
    return type(value)

@get_execution_time
@register.filter
def multiply(value,multiply_factor):
	"""
	Simple Filter for multiplication purpose

	How to use:
	value and multiply_factor are first and second argument respectively, passed through multiply filter.

	Ex: ratings.avg|multiply:30 
	    ratings.avg multiply with 30.

	"""
	return value*multiply_factor


@register.filter
def get_dict_value_from_key(dict_obj, key):
    try:
        if isinstance(dict_obj, dict):
            return dict_obj[key]
    except KeyError:
        return ''


@register.assignment_tag
def datetime_now():
	import datetime
	return datetime.datetime.now()


@get_execution_time
@register.filter
# filter added to remove underscore from string
def replace(str_to_process, to_be_replace, replace_by):
   replaced_str = str_to_process.replace(to_be_replace, replace_by)   
   return replaced_str
