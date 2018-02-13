''' This script outputs all duplicate emails existing in the database '''


from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help="This script outputs all duplicate emails existing in the database."
    def handle(self,*args,**options):
        email_to_search=""
        if args:
            email_to_search=args[0]
        all_users=[]
        for each in User.objects.all():
            all_users.append(each.email)
        seq=all_users
        a=set()
        b=a.add
        c = set( x for x in seq if x in a or b(x) )
        if email_to_search:
            if email_to_search in c:
                sear="'"+email_to_search+"'"
                p=User.objects.filter(email=email_to_search)
                print p
        else:
            print list(c)
        
