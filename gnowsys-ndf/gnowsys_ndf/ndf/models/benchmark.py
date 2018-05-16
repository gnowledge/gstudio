from base_imports import *
from gnowsys_ndf.settings import GSTUDIO_ELASTIC_SEARCH_IN_BENCHMARK_CLASS
from gnowsys_ndf.ndf.gstudio_es.es import *
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
    'has_data' : dict
  }

  required_fields = ['name']
  use_dot_notation = True

  def __unicode__(self):
    return self._id

  def identity(self):
    return self.__unicode__()

  def save(self, *args, **kwargs):
    super(Benchmark, self).save(*args, **kwargs)
    if GSTUDIO_ELASTIC_SEARCH_IN_BENCHMARK_CLASS:
      esearch.save_to_es(self)

benchmark_collection= db["Benchmarks"]