class UserId(object):
    '''
    Set's cookie named "user_id".
    '''

    # desired cookie will be available in every django view
    def process_request(self, request):
        # will only add cookie if request does not have it already
        try:
            # if not request.COOKIES.get('user_id'):
            request.COOKIES['user_id'] = request.user.id
        except Exception, e:
            pass

    # desired cookie will be available in every HttpResponse parser like browser but not in django view
    def process_response(self, request, response):
        try:
            if not request.COOKIES.get('your_desired_cookie'):
                response.set_cookie('user_id', request.user.id)
        except Exception, e:
            pass
        return response