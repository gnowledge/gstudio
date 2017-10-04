
class ProxyExample:
    pass
# Do whatever you do to get an HTTPRequest object that includes an
# user authenticated via Touchstone.
# That object is assumed to be stored the 'request' variable below:

    #from dlkit.services.proxy import ProxyManager
    #pm = ProxyManager()
    #condition = pm.get_proxy_condition()
    # a little record extension hoop might eventually need to
    # be jumped through here.  But we'll ignore that for now.
    #condition.set_http_request(request)
    #proxy = pm.get_proxy(condition)


# Now you have a proxy object that holds the user data and eventually other
# stuff, like locale information, etc, that can be used to instantiate new 
# Managers, which you will probably insert into your HttpRequest.session.

    #from dlkit.services.learning import LearningManager
    #request.session.lm = LearningManager(proxy)

# For the duration of the session you can use this for all the other things.
# that you normally do. My understanding is that your various Managers and 
# all their state will be save (in default mode) as Pickled objets in the db.
# For anonomous users you can still just instantiate as LearningManager()

class TestRequest:
    
    def __init__(self, username='pwilkins@mit.edu', authenticated=True, META={}):
        self.user = User(username, authenticated)
        self.META = META

    def get_user(self):
        return self.user


class User:

    def __init__(self, username, authenticated):
        self.username = username
        self.authenticated = authenticated

    def get_username(self):
        return self.username

    def is_authenticated(self):
        return self.authenticated
