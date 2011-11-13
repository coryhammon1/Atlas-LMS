from django.test import TestCase as OriginalTestCase
from django.test.client import Client

#login helper
class TestCase(OriginalTestCase):
	def login(self, username, password):
		c = Client()
		response = c.login(username=username, password=password)
		self.assertTrue(response)
		return c