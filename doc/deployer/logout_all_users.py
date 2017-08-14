from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.http import HttpRequest
from django.utils.importlib import import_module
from django.utils import timezone



def main():
    """
    Read all available users and all available not expired sessions. Then
    logout from each session.
    """
    request = HttpRequest()

    # sessions = Session.objects.filter(expire_date__gte=timezone.now())
    sessions = Session.objects.filter(expire_date__gte=timezone.now()).distinct('session_data')

    # Experimental trial (aggregate query):
    # unique_sessions_list = Session.objects.filter(expire_date__gte=timezone.now()).values('session_data').annotate(Count('session_data')).filter(session_data__count__lte=1)
    
    print('Found %d non-expired session(s).' % len(sessions))

    for session in sessions:
        try:
            user_id = session.get_decoded().get('_auth_user_id')
            engine = import_module(settings.SESSION_ENGINE)
            request.session = engine.SessionStore(session.session_key)

            request.user = User.objects.get(id=user_id)
            print ('\nProcessing session of [ %d : "%s" ]\n' % (request.user.id, request.user.username))

            logout(request)
            print('- Successfully logout user with id: %r ' % user_id)

        except Exception as e:
            # print "Exception: ", e
            pass


if __name__ == '__main__':
    main()