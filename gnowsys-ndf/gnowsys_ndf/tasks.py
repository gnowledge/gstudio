# from __future__ import absolute_import
import sys
import os

from gnowsys_ndf.celery import app
from celery import Celery
import time
from gnowsys_ndf.ndf.models.base_imports import *
from gnowsys_ndf.ndf.models.history_manager import HistoryManager
from gnowsys_ndf.ndf.models.models_utils import NodeJSONEncoder
from gnowsys_ndf.ndf.models import *
node_collection = db["Nodes"].Node

class Map(dict):
    """
    Example:
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """
    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.iteritems():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.iteritems():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]

# @app.task()
# def longtime_add(x, y):
# 	print "longtime_add method called"
# 	print 'long time task begins'
# 	# sleep 5 seconds
# 	time.sleep(5)
# 	print 'long time task finished'
# 	return x + y


@app.task()
def rcs_function(is_new,data_save_into_file,json_data,kew_args):
    history_manager = HistoryManager()
    rcs_obj = RCS()
    self=Map(json.loads(json_data))
    from bson import json_util
    json_data1 = json_util.loads(data_save_into_file)
    kew_args = json.loads(kew_args)
    if True:
        # print self
        if is_new:
            # Create history-version-file
            # print "Create history-version-file"
            try:
                if history_manager.create_or_replace_json_file(self,data_save_into_file):
                    fp = history_manager.get_file_path(self)
                    print fp
                    user_list = User.objects.filter(pk=self.created_by)
                    user = user_list[0].username if user_list else 'user'
                    # user = User.objects.get(pk=self.created_by).username
                    if self.created_at:
                        # message = "This document (" + self.name + ") is created by " + user + " on " + self.created_at.strftime("%d %B %Y")
                        message = "This document (" + self.name + ") is created by " + user + " on " + self.created_at
                        rcs_obj.checkin(fp, 1, message.encode('utf-8'), "-i")
                    else:
                        message = "This document (" + self.name + ") is created by " + user + " on "+ datetime.datetime.now().strftime("%d %B %Y")
                        rcs_obj.checkin(fp, 1, message.encode('utf-8'), "-i")
            except Exception as err:
                print err
                print "\n DocumentError: This document (", self._id, ":", self.name, ") can't be created!!!\n"
                # node_collection.collection.remove({'_id': self._id})
                raise RuntimeError(err)

        else:
            # Update history-version-file
            # print "Update history-version-file"
            fp = history_manager.get_file_path(self)
            # print fp

            try:
                rcs_obj.checkout(fp, otherflags="-f")
            except Exception as err:
                try:
                    if history_manager.create_or_replace_json_file(self,data_save_into_file):
                        # print "if blocked executed"
                        fp = history_manager.get_file_path(self)
                        # user = User.objects.get(pk=self.created_by).username
                        # print fp
                        user_list = User.objects.filter(pk=self.created_by)
                        # print user_list
                        user = user_list[0].username if user_list else 'user'
                        # print fp
                        # print user
                        # print self.created_at
                        if self.created_at:
                            message = "This document (" + self.name + ") is re-created by " + user + " on " + self.created_at
                            rcs_obj.checkin(fp, 1, message.encode('utf-8'), "-i")
                        else:
                            message = "This document (" + self.name + ") is re-created by " + user + " on "+ datetime.datetime.now().strftime("%d %B %Y")
                            rcs_obj.checkin(fp, 1, message.encode('utf-8'), "-i")

                except Exception as err:
                    # print "else exception blocked"
                    # print err
                    print "\n DocumentError: This document (", self._id, ":", self.name, ") can't be re-created!!!\n"
                    node_collection.collection.remove({'_id': self._id})
                    raise RuntimeError(err)

            try:
                if history_manager.create_or_replace_json_file(self,data_save_into_file):
                    # user = User.objects.get(pk=self.modified_by).username
                    user_list = User.objects.filter(pk=self.created_by)
                    user = user_list[0].username if user_list else 'user'
                    # print "try block"
                    # print user
                    # print user_list
                    # print self.last_update
                    if self.last_update:
                        # message = "This document (" + self.name + ") is lastly updated by " + user + " status:" + self.status + " on " + json_data.last_update.strftime("%d %B %Y")
                        message = "This document (" + self.name + ") is re-created by " + user + " on " + self.created_at
                        rcs_obj.checkin(fp, 1, message.encode('utf-8'))
                    else:
                        message = "This document (" + self.name + ") is re-created by " + user + " on "+ datetime.datetime.now().strftime("%d %B %Y")
                        rcs_obj.checkin(fp, 1, message.encode('utf-8'))

            except Exception as err:
                print "\n DocumentError: This document (", self._id, ":", self.name, ") can't be updated!!!\n"
                raise RuntimeError(err)
                #update the snapshot feild
        if kew_args.get('groupid'):
            # gets the last version no.
            rcsno = history_manager.get_current_version(self)
            node_collection.collection.update({'_id':self._id}, {'$set': {'snapshot'+"."+str(kew_args['groupid']):rcsno }}, upsert=False, multi=True)
