from django.test.client import Client
from django.contrib.auth.models import User

import urllib2

from schoolmanager.tests.utils import TestCase
from schoolmanager.courses.models import *
from schoolmanager.bulletins.models import *

class BulletinViewsTestCase(TestCase):
	fixtures = ['auth_fixtures.json', 'course_fixtures.json']
	
	def setUp(self):
		try:
			self.course = Course.objects.all()[0]
		except Course.DoesNotExist:
			self.fail("Could not find course")
	
	def testGetBulletinBoard(self):
		c = self.login('instructor', 'teacher')
		
		course = self.course
			
		response = c.get("/courses/%s/bulletins/" % course.get_url(), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertEqual(response.status_code, 200)
		
		bulletin_board = course.bulletin_board
		self.assertTrue(bulletin_board)
		
		#create bulletins
		
	def testAddBulletin(self):
		c = self.login('instructor', 'teacher')
		
		course = self.course
	
		url = "/courses/%s/bulletins/add/" % course.get_url()
	
		response = c.get(url)
		self.assertEqual(response.status_code, 200)
		
		self.assertFalse(Bulletin.objects.filter(title="Test", text="Text").exists())
		response = c.post(url, { 'title': "Title", 'text': "Text" })
		self.assertEqual(response.status_code, 200)
		self.assertTrue(Bulletin.objects.filter(title="Title", text="Text").exists())
	
		response = c.post(url)
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertFalse(json_response['success'])
	
	def testDeleteBulletin(self):
		
		admin = User.objects.filter(is_superuser=True)[0]
		instructor = User.objects.get(username='instructor')
		student = User.objects.filter(is_superuser=False, is_staff=False)[0]
		
		course = self.course
		
		bulletin_board, created = BulletinBoard.objects.get_or_create(course=course)
		
		bulletin = bulletin_board.bulletins.create(user=admin, title="new", text="blah")
		comment = bulletin.comments.create(user=admin, text="blah")
		
		c = self.login(student.username, 'student')
		
		response = c.get("/courses/%s/bulletins/%s/delete/" % (course.get_url(), bulletin.id))
		self.assertEqual(response.status_code, 403)
		
		c = self.login('instructor', 'teacher')
		
		response = c.get("/courses/%s/bulletins/%s/delete/" % (course.get_url(), bulletin.id))
		self.assertFalse(Bulletin.objects.filter(id=bulletin.id).exists())
		self.assertFalse(BulletinComment.objects.filter(id=comment.id).exists())
	
	def testAddComment(self):
		c = self.login('instructor', 'teacher')
		
		course = self.course
		
		url = "/courses/%s/bulletins/comments/add/" % course.get_url()
		
		response = c.get(url)
		self.assertEqual(response.status_code, 200)
		
		response = c.post(url)
		self.assertEqual(response.status_code, 200)
		
		response = c.post(url, { 'text': "Text" })
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertFalse(json_response['success'])
		
		user = course.users.all()[0]
		
		board, created = BulletinBoard.objects.get_or_create(course=course)
		bulletin = board.bulletins.create(user=user, title="Title", text="Text")
		
		self.assertFalse(bulletin.comments.filter(text="Text").exists())
		response = c.post(url, { 'text': "Text", 'bulletin_id': bulletin.id })
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertTrue(json_response['success'])
		self.assertTrue(bulletin.comments.filter(text="Text").exists())
	
	def testDeleteComment(self):
		course = self.course
		
		admin = User.objects.get(username='admin')
		student = User.objects.filter(is_superuser=False, is_staff=False)[0]
		
		bulletin_board, created = BulletinBoard.objects.get_or_create(course=course)
		
		bulletin = bulletin_board.bulletins.create(user=admin, title="new", text="balh")
		comment = bulletin.comments.create(user=admin, text="blah")
		
		c = self.login(student, 'student')
		
		response = c.get("/courses/%s/bulletins/comments/%s/delete/" % (course.get_url(), comment.id))
		self.assertEqual(response.status_code, 403)
		
		c = self.login('instructor', 'teacher')
		
		response = c.get("/courses/%s/bulletins/comments/%s/delete/" % (course.get_url(), comment.id))
		self.assertFalse(BulletinComment.objects.filter(id=comment.id).exists())
	