from django.core.cache import cache

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control

class Gcache(object):
	"""docstring for Gcache"""
	def __init__(self, arg):
		super(Gcache, self).__init__()
		self.arg = arg

	def set(cache_key, cache_value, time_to_cache):
		cache.set(cache_key, (group_name, group_id), 60*60)

	def get():
		pass
