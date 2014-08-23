from gnowsys_ndf.ndf.models import *
from gnowsys_ndf.ndf.views.search_views import *
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    def handle(self, *args, **options):

        try:
            col = get_database()[Node.collection_name]
        
            allNulls = col.Node.find({"_type":"GSystem", "access_policy":None})
            for obj in allNulls:
                obj.access_policy = u'PUBLIC'
                obj.save()
                

            allGSystems = col.Node.find({"_type":"GSystem"})
            Gapp_obj = col.Node.one({"_type":"MetaType", "name":"GAPP"})
            factory_obj = col.Node.one({"_type":"MetaType", "name":"factory_types"})

            for gs in allGSystems:
                gsType = gs.member_of[0]
                gsType_obj = col.Node.one({"_id":ObjectId(gsType)})
                if Gapp_obj._id in gsType_obj.member_of:
                    if gsType_obj.name == u"Quiz":
                        gs.url = u"quiz/details"
                    else:
                        gs.url = gsType_obj.name.lower()
                elif factory_obj._id in gsType_obj.member_of:
                    if gsType_obj.name == u"QuizItem":
                        gs.url = u"quiz/details"
                    if gsType_obj.name == u"Twist":
                        gs.url = u"forum/thread"
                    else:
                        gs.url = gsType_obj.name.lower()
                else:
                    gs.url = u"None"
                gs.save()
                
            allGSystems = col.Node.find({"$or": [ {"_type":"GSystem"}, {"_type":"File"} ] })
            for gs in allGSystems:
                gs.save()

            print "search script executed."

        except Exception, e:
            print "\n SearchScriptError: " + str(e)
            pass
