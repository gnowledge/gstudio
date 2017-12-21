from django.core.urlresolvers import reverse
import datetime
from django.test import TestCase
from django.conf import settings

from django_mongokit import get_database
from models import Node

try:
    from django.db import connections
    __django_12__ = True
except ImportError:
    __django_12__ = False


class ExampleTest(TestCase):

    def setUp(self):
        if not __django_12__:
            # Ugly but necessary
            from django.db import load_backend
            backend = load_backend('django_mongokit.mongodb')

            def get(key):
                return getattr(settings, key, None)
            self.connection = backend.DatabaseWrapper({
                'DATABASE_HOST': get('MONGO_DATABASE_HOST'),
                'DATABASE_NAME': settings.MONGO_DATABASE_NAME,
                'DATABASE_OPTIONS': get('MONGO_DATABASE_OPTIONS'),
                'DATABASE_PASSWORD': get('MONGO_DATABASE_PASSWORD'),
                'DATABASE_PORT': get('MONGO_DATABASE_PORT'),
                'DATABASE_USER': get('MONGO_DATABASE_USER'),
                'TIME_ZONE': settings.TIME_ZONE,
            })
            self.old_database_name = settings.MONGO_DATABASE_NAME
            self.connection.creation.create_test_db()

        db = get_database()
        assert 'test_' in db.name, db.name

    def tearDown(self):
        for name in get_database().collection_names():
            if name not in ('system.indexes',):
                get_database().drop_collection(name)

        # because we have to manually control the creation and destruction of
        # databases in Django <1.2, I'll destroy the database here
        if not __django_12__:
            self.connection.creation.destroy_test_db(self.old_database_name)

    def test_creating_basic_node(self):
        """test to create a basic node """
        collection = get_database()[Node.collection_name]
        node = collection.Node()
        node.name = u"gnowsys"
        node.creationtime = datetime.datetime.now()
        node.tags = [u"semantic web", u"network"]
        node.validate()
        node.save()

        self.assertTrue(node['_id'])
        self.assertEqual(node.name, u"gnowsys")

    def test_homepage(self):
        """homepage shows a list of nodes and allows to add or delete
        existing nodes """
        response = self.client.get(reverse('homepage'))
        self.assertTrue(response.status_code, 200)
        self.assertTrue('No nodes in the gnowledge base' in response.content)

        data = {'name': '',
                'creationtime': '2010-12-31',
                'tags': ' semantic web , network '}
        response = self.client.post(reverse('homepage'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('class="errorlist"' in response.content)
        self.assertTrue('This field is required' in response.content)

        data['name'] = 'gnowsys'
        response = self.client.post(reverse('homepage'), data)
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('homepage'))
        self.assertTrue(response.status_code, 200)
        self.assertTrue('gnowsys' in response.content)
        self.assertTrue('31 December 2010' in response.content)
        self.assertTrue('Tags: semantic web, network' in response.content)

        collection = get_database()[Node.collection_name]
        node = collection.Node.one()
        assert node.topic == u"gnowsys"
        delete_url = reverse('delete_node', args=[str(node._id)])
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('homepage'))
        self.assertTrue(response.status_code, 200)
        self.assertTrue('gnowsys' not in response.content)
