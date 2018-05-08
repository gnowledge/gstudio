from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

# from django.conf import settings
# from django.core.cache import cache, get_cache
# from django.utils.importlib import import_module


# class UserRestrictMiddleware(object):
#     def process_request(self, request):
#         """
#         Checks if different session exists for user and deletes it.
#         """
#         if request.user.is_authenticated():
#             cache = get_cache('default')
#             print "cache : ", cache
#             cache_timeout = 86400
#             cache_key = "user_pk_%s_restrict" % request.user.pk
#             cache_value = cache.get(cache_key)
#             print "cache_value : ", cache_value

#             if cache_value is not None:
#                 if request.session.session_key != cache_value:
#                     engine = import_module(settings.SESSION_ENGINE)
#                     session = engine.SessionStore(session_key=cache_value)
#                     session.delete()
#                     cache.set(cache_key, request.session.session_key,
#                               cache_timeout)
#             else:
#                 cache.set(cache_key, request.session.session_key, cache_timeout)



# # from django.contrib.sessions.models import Session
# # from tracking.models import Visitor
# # from datetime import datetime

# # class UserRestrictMiddleware(object):
# #     """
# #     Prevents more than one user logging in at once from two different IPs
# #     """
# #     def process_request(self, request):
# #         ip_address = request.META.get('REMOTE_ADDR','')
# #         print "ip_address : ", ip_address
# #         try:
# #             last_login = request.user.last_login
# #             print "last_login : ", last_login
# #         except:
# #             last_login = 0
# #         print unicode(last_login)[:19]
# #         print unicode(datetime.now())[:19]
# #         if unicode(last_login)==unicode(datetime.now())[:19]:
# #             previous_visitors = Visitor.objects.filter(user=request.user).exclude(ip_address=ip_address)
# #             print "previous_visitors : ", previous_visitors
# #             for visitor in previous_visitors:
# #                 print "visitor : ", visitor
# #                 Session.objects.filter(session_key=visitor.session_key).delete()
# #                 visitor.user = None
# #                 visitor.save()

class UserRestrictionMiddleware:
    """
    Prevents logged-in User from accessing login form
    """
    def process_request(self, request):
        if request.user.is_authenticated():
            if request.path_info.startswith('/accounts/login/'):
                return HttpResponseRedirect(reverse('landing_page'))