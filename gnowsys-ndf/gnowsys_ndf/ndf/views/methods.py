
''' Common methods for gnowsys_ndf  '''

from gnowsys_ndf.ndf.models import *
from django.contrib.auth.models import User

db = get_database()

def check_existing_group(groupname):
  col_Group = db[Group.collection_name]
  colg = col_Group.Group.find({"name":groupname})
  if colg.count() >= 1:
    return True
  else:
    return False
