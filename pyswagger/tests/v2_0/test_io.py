# -*- coding: utf-8 -*-

from pyswagger import App, io, primitives
from ..utils import get_test_data_folder
import unittest
import os
import six


class RequestTestCase(unittest.TestCase):
    """ test Request """

    @classmethod
    def setUpClass(kls):
        kls.app = App.create(get_test_data_folder(
            version='2.0',
            which=os.path.join('io', 'request')
        ))

    def test_scheme(self):
        """ make sure Request.scheme works """

        # when didn't assign preference, use the first one in schemes
        req, _ = self.app.s('/t').get()
        req.prepare(scheme=['https', 'http'])
        self.assertTrue(req.url.startswith('http://'))

        # when assigned with preference, use the preference
        req, _ = self.app.s('/t').get()
        req.scheme = 'https'
        req.prepare(scheme=['http', 'https'])
        self.assertTrue(req.url.startswith('https://'))

        # when assinged with preference, and not available in input, raise Exception
        req, _ = self.app.s('/t').get()
        req.scheme = 'wss'
        self.assertRaises(Exception, req.prepare, scheme=['http'])

        # failed with scheme is not a list or string
        req, _ = self.app.s('/t').get()
        self.assertRaises(ValueError, req.prepare, scheme=1)


class ResponseTestCase(unittest.TestCase):
    """ test Response """

    @classmethod
    def setUpClass(kls):
        kls.app = App.create(get_test_data_folder(
            version='2.0',
            which=os.path.join('io', 'response')
        ))

    def test_response_schema_with_status(self):
        """ make sure schema works as expected """

        # make sure exception raised
        resp = io.Response(self.app.s('/resp').get)
        self.assertRaises(Exception, resp.apply_with, None, 'some string')

        # test for 'default'
        resp = io.Response(self.app.s('/resp').get)
        resp.apply_with(0, 'test string', {'content-type': 'text/plain'})
        self.assertEqual(resp.status, 0)
        self.assertEqual(resp.raw, 'test string')
        self.assertEqual(resp.data, 'test string')

        # test for specific status code
        r = '{"id": 0, "message": "test string 2"}'
        resp = io.Response(self.app.s('/resp').get)
        resp.apply_with(404, r)
        self.assertEqual(resp.status, 404)
        self.assertEqual(resp.raw, r)
        self.assertTrue(isinstance(resp.data, primitives.Model))

    def test_error_only_status(self):
        """ it's legal for a Swagger without any successful status Response object.
        in this case, users need to access response via Response.raw
        """
        resp = io.Response(self.app.s('/resp').post)

        # make sure we are ok when no matching status and without a 'default'
        resp.apply_with(200, 'some data')
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.raw, 'some data')
        self.assertEqual(resp.data, None)

        # make sure header also works fine
        header = {
            'A': 1,
            'B': '222'
        }
        resp.apply_with(200, None, header)
        self.assertEqual(resp.header, {
            'A': [1],
            'B': ['222']
        })

    def test_raw_body_only(self):
        """ an option skip passing body byte stream to swagger-primitive-factory
        """
        r = '{"id": 0, "message": "test string 2"}'
        resp = io.Response(self.app.s('/resp').get)
        resp.raw_body_only = True
        resp.apply_with(404, r)
        self.assertEqual(resp.status, 404)
        self.assertEqual(resp.raw, r)
        self.assertFalse(isinstance(resp.data, primitives.Model))

    def test_raw_in_utf8(self):
        """ utf-8 encoding should support by default
        """
        resp = io.Response(self.app.s('/resp2').get)
        resp.apply_with(status=200, raw=six.BytesIO(six.u('{"message":"測試資料A"}').encode('utf8')).getvalue())

