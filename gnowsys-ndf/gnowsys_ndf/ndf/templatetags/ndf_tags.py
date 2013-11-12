"""Template tags for ndf"""
from gnowsys_ndf.ndf.models import *
from django.template import Library

register=Library()
db=get_database()

"""Get the common template for editing and displaying content 
"""
@register.inclusion_tag('ndf/edit_content.html', takes_context=True)
def edit_content(context):
  request = context['request']
  user = request.user
  
  doc_obj = context['node']
  return {'template': 'ndf/edit_content.html', 'user': user, 'node': doc_obj}

""" Get Existing Groups """
@register.assignment_tag
def get_existing_groups():
  group = []
  col_Group = db[Group.collection_name]
  colg = col_Group.Group.find()
  gr=list(colg)
  for items in gr:
    group.append(items.name)
  group.append("abcd")
  group.append("cdef")
  return group
