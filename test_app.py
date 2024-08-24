#!/usr/bin/python3
import unittest
from app import app

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        # Set up the test client
        app.testing = True
        self.client = app.test_client()

    def test_posts(self):
        # Test the /add endpoint
        response = self.client.get('/posts')
        self.assertEqual(response.status_code, 200)

    def test_post_create_noauth(self):
        response = self.client.get('/post/create')
        self.assertEqual(response.status_code, 302)

    def test_post_create_auth(self):
        self.client.set_cookie('Cookie', 'auth', 'admin')
        response = self.client.get('/post/create')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()


