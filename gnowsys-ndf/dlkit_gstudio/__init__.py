"""Supporting objects to be instantiated at runtime"""

from dlkit.abstract_osid.osid.errors import OperationFailed
from dlkit.primordium.id.primitives import Id
import time
import datetime
from threading import Thread
from pymongo import DESCENDING
from bson import ObjectId
from bson.timestamp import Timestamp

VMAP = {
    'i': 'new',
    'u': 'changed',
    'd': 'deleted'
}

class MongoClientContainer:

    def __init__(self):
        self._mongo_client = None

    def is_mongo_client_set(self):
        """Check to see if the mongo client has been set."""
        return bool(self._mongo_client)

    def set_mongo_client(self, mongo_client):
        """Set the mongo client. Raises error if already set."""
        if self.is_mongo_client_set():
            raise OperationFailed('MongoClient already set')
        self._mongo_client = mongo_client

    def get_mongo_client(self):
        """Gets the mongo client. Raises error if no mongo client set."""
        if not self.is_mongo_client_set():
            raise OperationFailed('MongoClient not set')
        return self._mongo_client

    mongo_client = property(fget=get_mongo_client, fset=set_mongo_client)


MONGO_CLIENT = MongoClientContainer()

class MongoListener(Thread):
    """A utility thread that listens for database changes for notification sessions"""

    def __init__(self, wait_seconds=10, max_attempts=3):
        """Constructor"""
        Thread.__init__(self)
        self.setDaemon(True)
        self._wait_period = datetime.timedelta(seconds=wait_seconds)
        self._max_attempts = max_attempts
        self.receivers = dict()
        self.notifications = dict()

    def initialize(self, runtime):
        """Initialize this listener. Finds most recent timestamp"""
        if self.is_alive():
            raise IllegalState('notification thread is already initialized')
        if not MONGO_CLIENT.is_mongo_client_set() and runtime is not None:
            set_mongo_client(runtime)
        cursor = MONGO_CLIENT.mongo_client['local']['oplog.rs'].find().sort('ts', DESCENDING).limit(-1)
        try:
            self.last_timestamp = cursor.next()['ts']
        except StopIteration:
            self.last_timestamp = Timestamp(0, 0)

    def _notify_receiver(self, receiver, params, doc):
        """Send notification to the receiver"""
        verb = VMAP[doc['op']]
        ns = doc['ns']
        notification_id = Id(ns + 'Notification:' + str(ObjectId()) + '@' + params['authority'])
        object_id = Id(ns + ':' + str(doc['o']['_id']) + '@' + params['authority'])
        getattr(receiver, '_'.join([verb, params['obj_name_plural']]))(notification_id, [object_id])
        return notification_id

    def _run_namespace(self, doc):
        """Run through all receivers related to the doc's namespace"""
        for receiver in self.receivers[doc['ns']]:
            params = self.receivers[doc['ns']][receiver]
            if params[doc['op']]:
                if params[doc['op']] is True or str(doc['o']['_id']) in params[doc['op']]:
                    notification_id = self._notify_receiver(receiver, params, doc)
                    if params['reliable'] and self._max_attempts > 1:
                        self.notifications[notification_id] = {
                            'receiver': receiver,
                            'params': dict(params),
                            'doc': dict(doc),
                            'ts': datetime.datetime.now(),
                            'attempts': 1}

    def _retry(self):
        """Deal with unacknowledged notifications."""
        notifications_to_delete = []
        for notification_id in self.notifications:
            if datetime.datetime.now() > self.notifications[notification_id]['ts'] + self._wait_period:
                self._notify_receiver(
                    self.notifications[notification_id]['receiver'],
                    self.notifications[notification_id]['params'],
                    self.notifications[notification_id]['doc'])
                if self.notifications[notification_id]['attempts'] >= self._max_attempts - 1:
                    notifications_to_delete.append(notification_id)
                else:
                    self.notifications[notification_id]['ts'] = datetime.datetime.now()
                    self.notifications[notification_id]['attempts'] += 1
        for notification_id in notifications_to_delete:
            del self.notifications[notification_id]


    def run(self):
        """main control loop for thread"""
        while True:
            cursor = MONGO_CLIENT.mongo_client['local']['oplog.rs'].find(
                {'ts':{'$gt': self.last_timestamp}})
            # http://stackoverflow.com/questions/30401063/pymongo-tailing-oplog
            cursor.add_option(2)  # tailable
            cursor.add_option(8)  # oplog_replay
            cursor.add_option(32)  # await data
            self._retry()
            for doc in cursor:
                self.last_timestamp = doc['ts']
                if doc['ns'] in self.receivers:
                    self._run_namespace(doc)
            time.sleep(1)

MONGO_LISTENER = MongoListener()