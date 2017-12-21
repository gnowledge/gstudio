from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.search_views import *
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
	def handle(self, *args, **options):
		try:
			dltr=list(collection.ToReduceDocs.find({'required_for':to_reduce_doc_requirement}))

			for doc in dltr:
				if doc:
					doc_id = doc.doc_id

					orignal_doc = collection.Node.find_one({"_id":doc_id})
					if orignal_doc:
						content_dict = dict(map_reduce(orignal_doc.content_org,mapper,reducer))
						
						dord = collection.ReducedDocs.find_one({"orignal_id":doc_id,'required_for':reduced_doc_requirement}) #doc of reduced docs
						if dord:
							dord.content=content_dict
							dord.is_indexed = False
							dord.save()
						else:
							new_doc = collection.ReducedDocs()
							new_doc.content = content_dict
							new_doc.orignal_id = doc_id
							new_doc.required_for = reduced_doc_requirement
							new_doc.is_indexed = False
							new_doc.save()

						doc.delete()
			
			print "\n Documents have been Map Reduced. It's Done!\n"
			
		except Exception as e:
			print "\n MapReduceError: " + str(e) + "!!!\n"

