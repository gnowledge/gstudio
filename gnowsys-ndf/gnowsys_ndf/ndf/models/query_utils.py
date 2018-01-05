from gnowsys_ndf.ndf.models import *
# Conventions followed for names w.r.t mongoDB:
# {"key": "value"}

def get_unique_values(collection_name, field_key):
	return db[collection_name].find().distinct(field_key)