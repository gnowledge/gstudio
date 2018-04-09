from base_imports import *

@connection.register
class Benchmark(DjangoDocument):

  objects = models.Manager()

  collection_name = 'Benchmarks'

  structure = {
    '_type':unicode,
    'name': unicode,
    'time_taken':unicode,
    'parameters':unicode,
    'size_of_parameters':unicode,
    'function_output_length':unicode,
    'calling_url':unicode,
    'last_update': datetime.datetime,
    'action' : basestring,
    'user' : basestring,
    'session_key' : basestring,
    'group' : basestring,
    'has_data' : dict,
    'locale': basestring
  }

  required_fields = ['name']
  use_dot_notation = True

  def __unicode__(self):
    return self._id

  def identity(self):
    return self.__unicode__()


benchmark_collection= db["Benchmarks"]