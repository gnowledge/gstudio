"""Template tags for ndf"""
from gnowsys_ndf.ndf.models import *
from django.template import Library


register=Library()
db=get_database()

""" Get Existing Groups """
@register.assignment_tag
def get_existing_groups():
    group=[]
    col_Group = db[Group.collection_name]
    colg=col_Group.Group.find()
    gr=list(colg)
    for items in gr:
        group.append(items.name)
    group.append("abcd")
    group.append("cdef")
    return group
