from __future__ import division

import datetime

import django.utils.simplejson as json

from django.test.client import Client
from django.contrib.auth.models import User

import urllib2

from schoolmanager.utils import *

from schoolmanager.tests.utils import TestCase
from schoolmanager.courses.models import *
from schoolmanager.courses.utils import *
from schoolmanager.assignments.models import Assignment
from schoolmanager.bulletins.models import *
from schoolmanager.user_backends import *

class SchoolmanagerUtilsTestCase(TestCase):
	fixtures = ['auth_fixtures.json', 'course_fixtures.json', 'assignment_fixtures.json', 'quiz_fixtures.json']
	
	def testQueryList(self):
		users = QueryList(User.objects.all())
		
		self.assertEquals(5, users.count())
		self.assertEquals(1, users.count(is_superuser=True))
		self.assertEquals(1, users.count(is_superuser=True, is_staff=True))
		self.assertEquals(3, users.count(is_superuser=False, is_staff=False))
		self.assertRaises(AttributeError, users.count, not_an_attribute=True)
		
		self.assertEquals(5, users.count(is_superuser__isnull=False))
		
		self.assertEquals(0, users.count(is_superuser__isnull=True))
		
		assignments = QueryList(Assignment.objects.all())
		self.assertEquals(4, assignments.count(course__department_id=1))
		
		users = QueryList(User.objects.all().order_by("-id"))
		self.assertEquals(users[-1].id, 1)
		
		users = users.order_by("id")
		self.assertEquals(users[0].id, 1)
		
		users = users.order_by("-id")
		self.assertEquals(users[-1].id, 1)
		
		self.assertEquals(4, users.exclude(id=1).count())
		self.assertEquals(4, users.exclude(is_superuser=True).count())
	
		#test group by
		courses = QueryList(Course.objects.all())
		terms = []
		for term in Term.objects.all():
			if term.courses.all().exists():
				terms.append(term)
				
		for term in terms:
			term._object_list = list(term.courses.all())
			
		grouped_terms = courses.group_by("term")
		self.assertListEqual(grouped_terms, terms)
	
	def testJsonResponse(self):
		jsr = JsonResponse({ 'name': "Blah" })
				
		self.assertTrue(jsr.content, json.dumps({ 'name': "Blah" }))

class CourseUtilsTestCase(TestCase):
	fixtures = ['auth_fixtures.json', 'course_fixtures.json', 'assignment_fixtures.json', 'quiz_fixtures.json']
	
	def testGetGroupsWithNullScores(self):
		course1 = Course.objects.all()[0]
		
		empty_course = Course(term=course1.term, department=course1.department, name="Empty", number=0, section=0)
		empty_course.save()
		
		groups = get_groups_with_null_scores(empty_course)
		self.assertEquals(groups, {})
		
		
class CourseModelTestCase(TestCase):
	fixtures = ['auth_fixtures.json', 'course_fixtures.json', 'assignment_fixtures.json', 'quiz_fixtures.json']
	
	def setUp(self):
		self.courses = Course.objects.all()
	
	def testShortname(self):
		course = self.courses[0]
		self.assertEquals(course.shortname(), "MATH100")
		course = self.courses[1]
		self.assertEquals(course.shortname(), "ART100")
		course = self.courses[3]
		self.assertEquals(course.shortname(), "ART100 (1)")
	
	def testGetUrl(self):
		course = self.courses[0]
		self.assertEquals(course.get_url(), "MATH100SFA2010")
		
		course = self.courses[3]
		self.assertEquals(course.get_url(), "ART100S1FA2010")
	
	def testGetLink(self):
		course = self.courses[0]
		self.assertEquals(course.get_link(), "<a href='/courses/MATH100SFA2010/'>Algebra I</a>")
		
		course = self.courses[3]
		self.assertEquals(course.get_link(), "<a href='/courses/ART100S1FA2010/'>Beginning Art (1)</a>")
	
	def testGetGradingScheme(self):
		course = self.courses[0]
		self.assertEquals(course.get_grading_scheme(), GradingScheme.objects.get(course=course))
		#test cache
		self.assertEquals(course.get_grading_scheme(), GradingScheme.objects.get(course=course))
	
	def testGetStudents(self):
		course = self.courses[0]
		self.assertEquals(list(course.get_students()), list(course.users.filter(is_staff=False, is_superuser=False)))
	
	def testGetGrade(self):
		blank_course = self.courses[2]
		weighted_grade_course = self.courses[1]
		cumulative_grade_course = self.courses[0]
				
		#make sure assignment 4 is not viewable
		Assignment.objects.filter(name="Homework 4").update(viewable_date=datetime.datetime.now() + datetime.timedelta(weeks=2))
		
		all_as = User.objects.get(username="student1")
		average = User.objects.get(username="student2")
		no_grades = User.objects.get(username="student3")
		
		self.assertEqual(weighted_grade_course.get_grade(all_as), 90)
		self.assertEqual(int(weighted_grade_course.get_grade(average)), 67)
		self.assertEqual(weighted_grade_course.get_grade(no_grades), 0)
		
		self.assertEqual(cumulative_grade_course.get_grade(all_as), 100)
		self.assertEqual(cumulative_grade_course.get_grade(average), (120 * 100)/160)
		self.assertEqual(cumulative_grade_course.get_grade(no_grades), 0)

		self.assertEqual(blank_course.get_grade(all_as), 0)
		

class CourseViewsTestCase(TestCase):
	fixtures = ['auth_fixtures.json', 'course_fixtures.json']
	
	def setUp(self):
		try:
			self.course = Course.objects.get(number=100, department__name="ART", section=None)
		except Course.DoesNotExist:
			self.fail("Could not find course")
	
	def testCourses(self):
		self.assertTrue(User.objects.filter(username="admin").exists())
		self.assertTrue(Course.objects.filter(number=100).exists())
	
	def testViewCourse(self):
		c = self.login('instructor', 'teacher')
		
		course = self.course
		
		response = c.get("/courses/%s/" % course.get_url())
		self.assertEqual(response.status_code, 200)
			
	def testGetGrade(self):
		student = User.objects.filter(is_superuser=False, is_staff=False)[0]
		c = self.login(student.username, 'student')
		
		course = self.course
		response = c.get("/courses/%s/grade/" % course.get_url(), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
		self.assertEqual(response.status_code, 200)
	
	def testGrades(self):
		c = self.login('instructor', 'teacher')
		
		course = self.course
		
		url = "/courses/%s/grades/" % course.get_url()
		
		response = c.get(url)
		self.assertEqual(response.status_code, 200)
	
		self.assertTrue(course.grades)
		
		grades = CourseGrades.objects.get(course=course)
		grades.delete()
		
		response = c.get(url)
		self.assertEqual(response.status_code, 200)
		
		grades = CourseGrades.objects.get(course=course)
	
		response = c.post(url, { 'form_name': "scale" })
		self.assertEqual(response.status_code, 200)
		
		response = c.post(url, { 'form_name': "scale", 'a': "45" })
		self.assertEqual(response.status_code, 200)
		
		response = c.post(url, { 'form_name': "grading" })
		self.assertEqual(response.status_code, 200)
		
		response = c.post(url, { 'form_name': "grading", 'print': None })
		self.assertEqual(response.status_code, 200)
		
		response = c.post(url, { 'form_name': "grading", 'print': "true" })
		self.assertEqual(response.status_code, 200)
	
	def testGetStream(self):
		c = self.login('instructor', 'teacher')
		
		course = self.course
		response = c.get("/courses/%s/stream/" % course.get_url())
		self.assertEqual(response.status_code, 200)
	
		
	
class GradingSchemeTestCase(TestCase):
	
	def testGrading(self):
		scheme = GradingScheme()
		
		self.assertEqual(scheme.grade_for_percent(50), "F")
		self.assertEqual(scheme.grade_for_percent(100), "A")
		self.assertEqual(scheme.grade_for_percent(90), "A-")
		self.assertEqual(scheme.grade_for_percent(85), "B")
		self.assertEqual(scheme.grade_for_percent(80), "B-")
		self.assertEqual(scheme.grade_for_percent(79), "C+")
		self.assertEqual(scheme.grade_for_percent(75), "C")
		self.assertEqual(scheme.grade_for_percent(70), "C-")
		self.assertEqual(scheme.grade_for_percent(69), "D+")
		self.assertEqual(scheme.grade_for_percent(65), "D")
		self.assertEqual(scheme.grade_for_percent(60), "D-")
		
class CourseGradesTestCase(TestCase):
	fixtures = ['course_fixtures.json']

	def setUp(self):
		self.course = Course.objects.all()[0]
	
	def testSetAndGetGradeText(self):
		self.course.grades.grades = { '3': 'A' }
		self.assertEquals(self.course.grades.grade_text, '{"3": "A"}')
		
		self.assertEquals(self.course.grades.grades, {'3': 'A'})
		
		self.course.grades.grades = { '2': '"A"', '3': '"B"' }
		self.assertEquals(self.course.grades.grades, {'2': '"A"', '3': '"B"'})
		
		
		
class DjangoUserBackendTestCase(TestCase):
	fixtures = ['auth_fixtures.json']
	
	def setUp(self):
		self.backend = DjangoUserBackend()
	
	def testGet(self):
		user = User.objects.get(username="admin")
		self.assertEquals(user, self.backend.get("admin"))
		
		try:
			self.backend.get("This_is_not_a_username")
			self.fail("UserDoesNotExist not thrown")
		except User.DoesNotExist:
			pass
			
	def testSave(self):
		user = User.objects.get(username="admin")
		user.first_name = "Joe"
		
		self.backend.save(user)
		
		user = User.objects.get(username="admin")
		self.assertEquals(user.first_name, "Joe")
		
	def testDelete(self):
		user = User.objects.get(username="student1")
		
		self.backend.delete(user)
		
		self.assertFalse(User.objects.filter(username="student1").exists())
		
	def testContaining(self):
		searched_users = self.backend.containing("o")
		
		users = User.objects.filter(Q(username__icontains="o") | Q(first_name__icontains="o") | Q(last_name__icontains="o"))
		
		for user in users:
			if not user in searched_users:
				self.fail("%s not found." % user)
				
		
	def testStartingWith(self):
		searched_users = self.backend.startingwith("g", "students")
		
		users = User.objects.filter(last_name__istartswith="g", is_staff=False, is_superuser=False)
		for user in users:
			if not user in searched_users:
				self.fail("%s not found." % user)
				
		searched_users = self.backend.startingwith("g", "administrators")
		self.assertEquals(list(searched_users), [])




		