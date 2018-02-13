from base_imports import *

@connection.register
class Analytics(DjangoDocument):

  objects = models.Manager()

  collection_name = 'analytics_collection'

  structure = {
    'timestamp': datetime.datetime,
    'action' : dict,
    'user' : dict,
    'obj' : dict,
    'group_id' : basestring,
    'session_key' : basestring
  }

  required_fields = ['timestamp']
  use_dot_notation = True

  def __unicode__(self):
    return self._id

  def identity(self):
    return self.__unicode__()
