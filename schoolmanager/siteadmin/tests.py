"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
import datetime

import django.utils.simplejson as json

from schoolmanager.tests.utils import TestCase
from schoolmanager.courses.models import *


class SiteAdminViewsTestCase(TestCase):
	fixtures = ("auth_fixtures.json", "course_fixtures.json")
	
	def testAddUser(self):
		c = self.login("admin", "test")
		
		url = "/siteadmin/users/add/"
		
		self.assertFalse(User.objects.filter(username="Test").exists())
		response = c.post(url, { 'username': "Test", 'first_name': "Test", 'last_name': "Tester", 'password1': "test", 'password2': "test", 'user_type': "administrator" })
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertTrue(json_response['success'])
		self.assertTrue(User.objects.filter(username="Test").exists())
	
		response = c.post(url, { 'username': "Test", 'first_name': "Test", 'last_name': "Tester", 'password1': "test", 'password2': "test", 'user_type': "administrator" })
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertFalse(json_response['success'])
		
		response = c.post(url)
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertFalse(json_response['success'])
	
	def testDeleteUser(self):
		c = self.login("admin", "test")
		
		url = "/siteadmin/users/delete/"
		
		user = User.objects.create_user("test", "test@test.com", "test")
		
		self.assertTrue(User.objects.filter(username=user.username).exists())
		response = c.post(url, { 'username': user.username })
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertTrue(json_response['success'])
		self.assertFalse(User.objects.filter(username=user.username).exists())
		
		response = c.post(url)
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertFalse(json_response['success'])
		
		response = c.post(url, { 'username': "notausername" })
		self.assertEqual(response.status_code, 200)
	
	def testSearchUser(self):
		c = self.login("admin", "test")
		
		url = "/siteadmin/users/search/"
		
		response = c.post(url, { 'search': "i" })
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertTrue(json_response['success'])
		
		response = c.post(url)
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertTrue(json_response['success'])
	
	def testEnrollUser(self):
		c = self.login("admin", "test")
		
		user = User.objects.get(username="student1")
		
		course = Course.objects.all()[0]
		user.courses.remove(course)
		
		url = "/siteadmin/users/%d/enroll/" % user.id
		
		self.assertFalse(user.courses.filter(id=course.id).exists())
		response = c.post(url, { 'course_id': course.id })
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertTrue(json_response['success'])
		self.assertTrue(user.courses.filter(id=course.id).exists())
		
		response = c.post(url, { 'course_id': course.id })
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertTrue(json_response['success'])
		self.assertTrue(user.courses.filter(id=course.id).exists())
	
		response = c.post(url, { 'course_id': 12309123098120398 })
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertFalse(json_response['success'])
		
	def testCourseFromUser(self):
		c = self.login("admin", "test")
		
		user = User.objects.get(username="student1")
		course = user.courses.all()[0]
		
		url = "/siteadmin/users/%d/remove/" % user.id
		
		self.assertTrue(user.courses.filter(id=course.id).exists())
		response = c.post(url, { 'course_id': course.id })
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertTrue(json_response['success'])
		self.assertFalse(user.courses.filter(id=course.id).exists())
		
		response = c.post(url, { 'course_id': course.id })
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertFalse(json_response['success'])
		self.assertFalse(user.courses.filter(id=course.id).exists())
	
		response = c.post(url, { 'course_id': 12309123098120398 })
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertFalse(json_response['success'])
		
	def testAddTerm(self):
		c = self.login("admin", "test")
	
		url = "/siteadmin/terms/add/"
		
		response = c.post(url, { 'name': "TS", 'start': "01/01/2010", 'end': "12/12/2010" })
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertTrue(json_response['success'])
		self.assertTrue(Term.objects.filter(name="TS", start=datetime.datetime(2010, 1, 1), end=datetime.datetime(2010, 12, 12)).exists())
		
		response = c.post(url, { 'name': "FAS", 'start': "12312", 'end': "23422" })
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertFalse(json_response['success'])
		
	def testDeleteTerm(self):
		c = self.login("admin", "test")
		
		url = "/siteadmin/terms/delete/"
		
		self.assertTrue(Term.objects.filter(id=1).exists())
		self.assertTrue(Course.objects.filter(term__id=1).exists())
		response = c.post(url, { 'id': 1 })
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertTrue(json_response['success'])
		self.assertFalse(Term.objects.filter(id=1).exists())
		self.assertFalse(Course.objects.filter(term__id=1).exists())
		
		response = c.post(url)
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertFalse(json_response['success'])
		
		response = c.post(url, { 'id': 12309123098123 })
		self.assertEqual(response.status_code, 200)
	
	def testChangeTerm(self):
		c = self.login("admin", "test")
		
		term = Term.objects.all()[0]
		
		url = "/siteadmin/terms/%d/change/" % term.id
			
	def testAddDepartment(self):
		c = self.login("admin", "test")
		
		url = "/siteadmin/departments/add/"
		
		response = c.post(url, { 'name': "TEST" })
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertTrue(json_response['success'])
		self.assertTrue(Department.objects.filter(name="TEST").exists())
		
		response = c.post(url, { 'name': "TEST" })
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertFalse(json_response['success'])
		self.assertTrue(json_response['errors'])
		
		response = c.post(url)
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertFalse(json_response['success'])
	
	def testChangeDepartment(self):
		c = self.login("admin", "test")
		
		department = Department.objects.create(name="TEST")
		
		url = "/siteadmin/departments/%d/change/" % department.id
	
		response = c.post(url, { 'name': "TST" })
		self.assertEquals(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertTrue(json_response['success'])
		self.assertTrue(Department.objects.filter(name="TST").exists())
		
		response = c.post(url, { 'name': "TST" })
		self.assertEquals(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertTrue(json_response['success'])
		self.assertTrue(Department.objects.filter(name="TST").exists())
	
		response = c.post(url)
		self.assertEquals(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertFalse(json_response['success'])
	
	def testDeleteDepartment(self):
		c = self.login("admin", "test")
		
		url = "/siteadmin/departments/delete/"
		
		self.assertTrue(Department.objects.filter(id=1).exists())
		self.assertTrue(Course.objects.filter(department__id=1).exists())
		response = c.post(url, { 'id': 1 })
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertTrue(json_response['success'])
		self.assertFalse(Department.objects.filter(id=1).exists())
		self.assertFalse(Course.objects.filter(department__id=1).exists())
		
		response = c.post(url)
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertFalse(json_response['success'])
		
		response = c.post(url, { 'id': 12309123098123 })
		self.assertEqual(response.status_code, 200)
		
	def testAddCourse(self):
		c = self.login("admin", "test")
		
		url = "/siteadmin/courses/add/"
		
		response = c.post(url, { 'term': 1, 'department': 1, 'name': "Test", 'number': 999 })
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertTrue(json_response['success'])
		self.assertTrue(Course.objects.filter(term__id=1, department__id=1, name="Test", number=999).exists())
		
		response = c.post(url, { 'term': 1, 'department': 1, 'name': "Test2", 'number': 999 })
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertFalse(json_response['success'])
		self.assertTrue(json_response['errors']['__all__'])
		
		response = c.post(url)
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertFalse(json_response['success'])
		
	def testDeleteCourse(self):
		c = self.login("admin", "test")
		
		url = "/siteadmin/courses/delete/"
		
		self.assertTrue(Course.objects.filter(id=1).exists())
		response = c.post(url, { 'id': 1 })
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertTrue(json_response['success'])
		
		response = c.post(url)
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertFalse(json_response['success'])
		
		response = c.post(url, { 'id': 123124314 })
		self.assertEqual(response.status_code, 200)
		
	def testPrintCourseGrades(self):
		c = self.login("admin", "test")
		try:
			course = Course.objects.get(pk=1)
		
			url = "/siteadmin/courses/%d/grades/" % course.id
		
			response = c.get(url)
			self.assertEqual(response.status_code, 200)
		
			CourseGrades.objects.filter(course=course).delete()
			
			response = c.get(url)
			self.assertEqual(response.status_code, 404)
			
			response = c.get("/siteadmin/courses/%d/" % course.id)
			self.assertEqual(response.status_code, 200)
		
		except Course.DoesNotExist:
			self.fail("Could not exist")
	
	def testAddUserToCourse(self):
		c = self.login("admin", "test")
		
		course = Course.objects.all()[0]
		
		url = "/siteadmin/courses/%d/add_user/" % course.id
		
		user = User.objects.create_user('test', 'test@test.com', 'test')
		
		self.assertFalse(course.users.filter(id=user.id).exists()) #user not in course
		response = c.post(url, { 'username': user.username })
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertTrue(json_response['success'])
		self.assertTrue(course.users.filter(username=user.username).exists())
		
		response = c.post(url, { 'username': user.username })
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertTrue(json_response['success'])
		
		response = c.post(url, { 'username': "notausername" })
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertFalse(json_response['success'])
		
		response = c.post(url)
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertFalse(json_response['success'])
		
	def testRemoveUserFromCourse(self):
		c = self.login("admin", "test")
		
		course = Course.objects.all()[0]
		
		url = "/siteadmin/courses/%d/remove_user/" % course.id
		
		user = course.users.all()[0]
				
		self.assertTrue(course.users.filter(id=user.id).exists()) #user is in course
		response = c.post(url, { 'username': user.username })
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertTrue(json_response['success'])
		self.assertFalse(course.users.filter(username=user.username).exists())
		
		response = c.post(url, { 'username': user.username })
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertFalse(json_response['success'])
		
		response = c.post(url, { 'username': "notausername" })
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertFalse(json_response['success'])
		
		response = c.post(url)
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertFalse(json_response['success'])
		
