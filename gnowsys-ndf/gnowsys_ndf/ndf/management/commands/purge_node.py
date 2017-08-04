from django.core.management.base import BaseCommand
from gnowsys_ndf.ndf.models import Group, Node
from gnowsys_ndf.ndf.views.methods import delete_node

class Command(BaseCommand):
    def handle(self, *args, **options):
        '''
        python manage.py purge_node <objectId> <proceed_flag y/Y>
        '''
        proceed_flag = False
        group_id = None
        if args:
            group_id = args[0]
            if len(args) == 2 and args[1] in ['y', 'Y']:
                proceed_flag = True
                # If proceed_flag is passed y, there will be no
                # prompt for confirmation to the user and
                # directly proceeds to purge the nodes.
        else:
            group_id = raw_input("Enter Group name or _id: ")
        print "\ngroup_id: ", group_id

        def validate_deletion(node_id,force_deletion=False):
            try:
                node_obj = Node.get_node_by_id(node_id)
                if node_obj:
                    if force_deletion:
                        print "\n Force Deletion on: ", node_obj._id
                        node_obj.delete()
                    else:
                        del_status, del_status_msg = delete_node(node_id=node_obj._id, deletion_type=1)
                        validate_deletion(node_id,force_deletion=True)
            except Exception as validate_deletion_err:
                print "\n Error occurred.", str(validate_deletion_err)

        def _group_deletion(group_id):
            try:
                group_obj = Group.get_group_name_id(group_id, get_obj=True)
                if group_obj:
                    Group.purge_group(group_id, proceed=proceed_flag)
                    validate_deletion(group_id)
                else:
                    node_obj = Node.get_node_by_id(group_id)
                    # If the ObjectId entered is not of a Group
                    if node_obj:
                        if node_obj.collection_set:
                            for each_obj_id in node_obj.collection_set:
                                _group_deletion(each_obj_id)
                        del_status, del_status_msg = delete_node(node_id=node_obj._id, deletion_type=1)
                        validate_deletion(node_obj._id)
            except Exception as group_del_err:
                print "\n Error occurred.", str(group_del_err)

        if group_id:
            _group_deletion(group_id)
        else:
            import os
            print "\n Please enter a Valid group_id."
            os._exit(0)
