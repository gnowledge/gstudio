from django.core.management.base import BaseCommand
from operator import or_
from django.db.models import Q
from django.contrib.auth.models import User
from gnowsys_ndf.ndf.models import node_collection

class Command(BaseCommand):
    def handle(self, *args, **options):
        '''
            For all users having any of the following element in their username,
            must have the agency-type set to Teacher for their respective Author objects
        '''
        print "\n 'agency-type=Teacher' setting Script Invoked."
        teacher_element_set = ['carbon', 'chlorine', 'copper', 'helium',
             'iron', 'nitrogen', 'oxygen', 'silver', 'sodium', 'zinc']
        ele_user_id_list = list(User.objects.filter(reduce(or_, [Q(username__icontains=ele_name) for ele_name in teacher_element_set])).values_list('id', flat=True))
        ele_auth_cur = node_collection.find({'_type': 'Author',
            'created_by': {'$in': ele_user_id_list}, 'agency_type': {'$ne': 'Teacher'}})
        print "\n Total Authors not having Teacher agency-type: ", ele_auth_cur.count()
        for each_auth in ele_auth_cur:
            try:
                each_auth.agency_type = 'Teacher'
            except Exception, e:
                each_auth['agency_type'] = 'Teacher'
            each_auth.save()
        print "\n 'agency-type=Teacher' setting Script Exited."
