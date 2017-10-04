from django.contrib.auth.models import User
from django.db.models import Q

from dlkit_gstudio.osid.errors import NotFound


class GStudioRequest:

    def __init__(self, username='', email=None, id=0, META={}):
        try:
            # self.user = User.objects.filter(Q(username=username) | Q(id=id) | Q(email=email))[0]
	        self.user = User.objects.get(Q(username=username) | Q(id=id) | Q(email=email))
	        self.username = self.user.username
	        self.authenticated = self.user.is_authenticated()
        except Exception, e:
            raise NotFound(e)
            # raise 'User with provided user does not exists.'
        self.META = META

    def get_user(self):
        return self.user

    def get_username(self):
        return self.username

    def is_authenticated(self):
        return self.authenticated
