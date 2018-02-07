from gnowsys_ndf.ndf.models import node_collection

class Author(object):
    '''
    Set's data named "author".
    '''

    def process_request(self, request):
        request.author = node_collection.one({'_type': 'Author', 'created_by': request.user.id})
        return 