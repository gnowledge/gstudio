from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.export_to_epub import *
n = node_collection.one({'_id': ObjectId('5752b5392e01310424dcf6cc')})
create_epub(n)