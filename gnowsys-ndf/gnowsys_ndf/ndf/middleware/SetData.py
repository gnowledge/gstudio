from gnowsys_ndf.settings import GSTUDIO_INSTITUTE_ID
from gnowsys_ndf.ndf.models import node_collection

class UserDetails(object):
    ''' Set's cookie. Gstudio supports following cookies along with django defalut:
    - `institute_id`: contains value of `GSTUDIO_INSTITUTE_ID`
    - `user_id`
    - `buddy_ids`: seperated by '&'
    - `user_and_buddy_ids`: seperated by '&'. first id will be logged in user's id followed by buddy-ids.
    '''
    # desired cookie will be available in every django view
    def process_request(self, request):
        # will only add cookie if request does not have it already
        try:
            # if not request.COOKIES.get('user_id'):
            request.COOKIES['user_id'] = request.user.id
            request.COOKIES['buddy_ids'] = request.session['buddies_userid_list']
            # Not using following cookie as we are not using cookie in views
            # 'user_and_buddy_ids'
        except Exception, e:
            pass

    # desired cookie will be available in every HttpResponse parser like browser but not in django view
    def process_response(self, request, response):
        try:
            user_id = (request.user.id or 0)
            response.set_cookie('user_id', str(user_id))
            # keeping this as redundant entry to have this in every response's cookie irrespective of buddies existance.
            response.set_cookie('user_and_buddy_ids', str(user_id))
            # initializing
            response.set_cookie('buddy_ids', '')

            buddies_userid_str = '&'.join([str(i) for i in request.session['buddies_userid_list']])

            if buddies_userid_str:
                # using [1:] to truncate starting '&'
                response.set_cookie('buddy_ids', buddies_userid_str)
                response.set_cookie('user_and_buddy_ids', (str(user_id) + '&' + buddies_userid_str))
        except Exception, e:
            pass
        return response


class Author(object):
    ''' Set's data named "author". '''
    def process_request(self, request):
        request.author = node_collection.one({'_type': 'Author', 'created_by': request.user.id})
        return 


class AdditionalDetails(object):
    """ Additional details can be added in this class """
    def process_response(self, request, response):
        response.set_cookie('institute_id', GSTUDIO_INSTITUTE_ID)
        response.set_cookie('language_code', request.LANGUAGE_CODE)
        return response
