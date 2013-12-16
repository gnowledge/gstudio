
''' Common methods for gnowsys_ndf  '''

from gnowsys_ndf.ndf.models import *

db = get_database()

def check_existing_group(groupname):
  col_Group = db[Group.collection_name]
  colg = col_Group.Group.one({"name": groupname})
  if colg:
    return True
  else:
    return False
