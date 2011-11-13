from __future__ import division

import os
import datetime
import tempfile

import django.utils.simplejson as json

from django.core.files.base import File
from django.test.client import Client
from django.contrib.auth.models import User
from django.db.models import Sum

from schoolmanager.tests.utils import TestCase

from schoolmanager.courses.models import *
from schoolmanager.assignments.models import *
from schoolmanager.assignments.utils import *

from schoolmanager.quizzes.models import *

class AssignmentGroupModelTest(TestCase):
	fixtures = ["auth_fixtures.json", "course_fixtures.json", "assignment_fixtures.json", "quiz_fixtures.json"]
	
	def setUp(self):
		self.group = AssignmentGroup.objects.filter(weight=70, name="Homework")[0]
		
		self.all_as = User.objects.get(username="student1")
		self.average = User.objects.get(username="student2")
		self.no_grades = User.objects.get(username="student3")
	
		#make sure nonviewable assignments are not viewable
		Assignment.objects.filter(name="Homework 4").update(viewable_date=datetime.datetime.now() + datetime.timedelta(weeks=2))
	
	def testGetScoreTotals(self):
		self.assertEqual(self.group.get_score_totals(self.all_as), (60, 60))
		self.assertEqual(self.group.get_score_totals(self.average), (45, 60))
		self.assertEqual(self.group.get_score_totals(self.no_grades), (0, 60))

	def testGetWeightedGrade(self):
		self.assertEqual(self.group.get_weighted_grade(self.all_as), 70)
		self.assertEqual(self.group.get_weighted_grade(self.average), (45/60)*70)
		self.assertEqual(self.group.get_weighted_grade(self.no_grades), 0)


class AssignmentModelTest(TestCase):
	fixtures = ["auth_fixtures.json", "course_fixtures.json"]
	
	def setUp(self):
		try:
			self.course = Course.objects.get(pk=1)
		except Course.ObjectDoesNotExist:
			self.fail("Could not get course")
			
		self.group = AssignmentGroup.objects.create(course=self.course, name="Assignments")
		
		self.assignment = Assignment.objects.create(course=self.course, group=self.group, name="Assignment", due_date=datetime.datetime.now() + datetime.timedelta(weeks=1), possible_score=20, type='o')
		
	def testProperties(self):
		assignment = self.assignment
		
		self.assertEqual("Assignment-%d" % assignment.id, assignment.cache_key)
		self.assertEqual("Course-%d-Assignment-%s" % (assignment.course_id, assignment.url_safe_name), assignment.name_cache_key)
		
	
	def testGetInstructorUrl(self):
		self.assertEqual("/courses/%s/assignments/%d/" % (self.assignment.course.get_url(), self.assignment.id), self.assignment.get_instructor_url())
		
	
	def testDueDateTimeCategory(self):
		course = self.course
		group = self.group
				
		now = datetime.datetime(2010, 6, 7, 12)
				
		due_date = now
		assignment = Assignment(due_date=due_date)
		
		self.assertEqual("Today", assignment.due_date_time_category(now=now))
		assignment.due_date = now + datetime.timedelta(hours=3)
		self.assertEqual("Today", assignment.due_date_time_category(now=now))
		
		assignment.due_date = now + datetime.timedelta(hours=12)
		self.assertEqual("Tomorrow", assignment.due_date_time_category(now=now))
		
		assignment.due_date = now + datetime.timedelta(days=2)
		self.assertEqual("This week", assignment.due_date_time_category(now=now))
		
		now = datetime.datetime(2010, 6, 11, 12)
		assignment.due_date = now + datetime.timedelta(days=1)
		self.assertEqual("Tomorrow", assignment.due_date_time_category(now=now))
	
		now = datetime.datetime(2010, 6, 7, 12)
		assignment.due_date = now + datetime.timedelta(weeks=1)
		self.assertEqual("Next week", assignment.due_date_time_category(now=now))
	
		assignment.due_date = now + datetime.timedelta(weeks=2)
		self.assertEqual("In a couple weeks", assignment.due_date_time_category(now=now))
	
		assignment.due_date = now + datetime.timedelta(weeks=3)
		self.assertEqual("In a couple weeks", assignment.due_date_time_category(now=now))
	
		assignment.due_date = now + datetime.timedelta(weeks=4)
		self.assertEqual("In a while", assignment.due_date_time_category(now=now))
		
		assignment.due_date = now + datetime.timedelta(weeks=14)
		self.assertEqual("In a while", assignment.due_date_time_category(now=now))
		
		assignment.due_date = now + datetime.timedelta(weeks=56)
		self.assertEqual("In a while", assignment.due_date_time_category(now=now))
	
	def testGetDueDateTimeCategoryDisplay(self):
		now = datetime.datetime(2010, 6, 7, 12)
		
		assignment = Assignment(due_date=now + datetime.timedelta(hours=3))
		self.assertEqual("3 p.m.", assignment.get_time_category_display(now=now))
	
		assignment.due_date = now + datetime.timedelta(days=1, hours=3)
		self.assertEqual("3 p.m.", assignment.get_time_category_display(now=now))
	
		assignment.due_date = now + datetime.timedelta(days=3, hours=3)
		self.assertEqual("Thu, 3 p.m.", assignment.get_time_category_display(now=now))
		
		assignment.due_date = now + datetime.timedelta(weeks=1, hours=3)
		self.assertEqual("Mon, Jun 14", assignment.get_time_category_display(now=now))
	
		assignment.due_date = now + datetime.timedelta(weeks=3, hours=3)
		self.assertEqual("Mon, Jun 28", assignment.get_time_category_display(now=now))
	
		assignment.due_date = now + datetime.timedelta(weeks=7, hours=3)
		self.assertEqual("Jul 26", assignment.get_time_category_display(now=now))
	
	def testGetSubmissions(self):	
		self.assertEqual(len(self.assignment.get_submissions()), self.course.users.filter(is_staff=False, is_superuser=False).count())
		
		self.assignment.submissions.all().delete()
		
		self.assertEqual(self.assignment.submissions.count(), 0)
		self.assertEqual(len(self.assignment.get_submissions()), self.course.users.filter(is_staff=False, is_superuser=False).count())
		
		self.assignment.submissions.all().delete()
		
		submitted_user = self.course.users.filter(is_staff=False, is_superuser=False)[0]
		self.assignment.submissions.create(user=submitted_user)
		
		self.assertEqual(len(self.assignment.get_submissions()), self.course.users.filter(is_staff=False, is_superuser=False).count())
		
		self.assertEqual(len(self.assignment.get_submissions()), self.course.users.filter(is_staff=False, is_superuser=False).count())
	
	def testGetPossibleScore(self):
		assignment = self.assignment
		
		self.assertEqual(assignment.get_possible_score(), 0)
		
		OnlineQuiz.objects.create(assignment=assignment)
		
		self.assertEqual(assignment.get_possible_score(), 0)
		
		first_question = assignment.quiz.questions.create(text="First")
		
		assignment = Assignment.objects.get(pk=assignment.pk)
		
		self.assertEqual(assignment.get_possible_score(), 5)
		
		first_question.delete()
		
		assignment = Assignment.objects.get(pk=assignment.pk)
		
		self.assertEqual(assignment.get_possible_score(), 0)
		
		assignment.type = 'c'
		assignment.possible_score = 20
		assignment.save()
		
		self.assertEqual(assignment.get_possible_score(), 20)
	
	def testIsViewable(self):
		assignment = self.assignment
		
		self.assertTrue(assignment.is_viewable)
		
		past_date = datetime.datetime.now() - datetime.timedelta(weeks=2)
		future_date = datetime.datetime.now() + datetime.timedelta(weeks=2)
		
		assignment.viewable_date = past_date
		
		self.assertTrue(assignment.is_viewable)
		
		assignment.viewable_date = future_date
		
		self.assertFalse(assignment.is_viewable)
	
	def testGetAverageGrade(self):
		self.assignment.possible_score = 20
		self.assignment.type = 'c'
		self.assignment.save()
		
		self.assignment.submissions.all().delete()
		self.assertEqual(self.assignment.get_average_grade(), None)
		
		self.assignment.get_submissions() #create submissions for every user
	
		students = self.course.users.filter(is_superuser=False, is_staff=False)
		
		student1 = students[0]
		student2 = students[1]
		student3 = students[2]
		
		self.assignment.submissions.update(score=20)
		self.assertEqual(self.assignment.get_average_grade(), 1)
		
		student1.submissions.filter(assignment=self.assignment).update(score=None)
		self.assertEqual(self.assignment.get_average_grade(), 1)
		
		student1.submissions.filter(assignment=self.assignment).update(score=15)
		self.assertEqual(self.assignment.get_average_grade(), 55/60)
	
	
class SubmissionModelTest(TestCase):
	fixtures = ["auth_fixtures.json", "course_fixtures.json", "assignment_fixtures.json"]
	
	def setUp(self):
		self.assignment = Assignment.objects.all()[0]
		self.course = self.assignment.course
		self.student = self.course.users.all()[0]
		self.quiz = OnlineQuiz.objects.create(assignment=self.assignment)
		self.user = User.objects.all()[0]

	def testGetGrade(self):
		submission = self.assignment.submissions.create(user=self.student)
		
		submission.score = 20
		
		self.assertEqual(submission.get_grade(), 1)
		
		submission.score = 15
		
		self.assertEqual(submission.get_grade(), .75)
		
		submission.score = None
		
		self.assertEqual(submission.get_grade(), None)
		
		self.assignment.possible_score = 0
		
		submission.score = 10
		
		self.assertEqual(submission.get_grade(), None)


class FileSubmissionModelTest(TestCase):
	fixtures = ["auth_fixtures.json", "course_fixtures.json", "assignment_fixtures.json"]
	
	def setUp(self):
		self.assignment = Assignment.objects.all()[0]
		self.course = self.assignment.course
		self.student = self.course.users.all()[0]
		
		self.submission = self.assignment.submissions.create(user=self.student)
		
		self.file_submission = self.submission.files.create(file="student1/file.txt", content_type="text")
		
	def testLink(self):
		self.assertEqual("/courses/%s/assignments/files/%d/" % (self.course.get_url(), self.file_submission.id), self.file_submission.link())


class ResourceModelTest(TestCase):
	fixtures = ["auth_fixtures.json", "course_fixtures.json", "assignment_fixtures.json"]
	
	def setUp(self):
		self.assignment = Assignment.objects.all()[0]
		self.resource = AssignmentResource(assignment=self.assignment, type='u', url="nytimes.com", name="nytimes")
		self.resource.save()
		
	def testGetUrl(self):
		resource = self.resource
		
		self.assertEqual(resource.get_url(), "http://nytimes.com")

		resource.type = 'f'
		
		self.assertEqual(resource.get_url(), "/courses/%s/assignments/%s/resources/%d/" % (self.assignment.course.get_url(), self.assignment.url_safe_name, resource.id))


	def testGetLink(self):
		resource = self.resource
		
		self.assertEqual(resource.get_link(), "<a href='http://nytimes.com'>nytimes</a>")
		
		resource.type = 'f'
		
		self.assertEqual(resource.get_link(), "<a href='%s'>%s</a>" % (self.resource.get_url(), self.resource.name))
	
	
class AssignmentUtilsTest(TestCase):
	def testSaveFileToUploadDirectory(self):
		from django.conf import settings
		upload_dir = settings.UPLOAD_DIR
		
		self.assertTrue(os.access(upload_dir, os.W_OK)) #make sure upload dir can be written to
		
		#create a temporary file
		tempFilePath = os.getcwd() + "/assignments/tempFile.txt"
		with open(tempFilePath, "wr") as tmpFile:
			file = File(tmpFile)
			file.name = "tempFile.txt"
				
			self.assertEqual(upload_dir + file.__unicode__(), save_file_to_upload_dir(file))
		
			self.assertTrue(os.path.exists(upload_dir + file.__unicode__())) #file was written to upload directory
		
			self.assertEqual(upload_dir + file.__unicode__(), save_file_to_upload_dir(file)) #overwrite
			
			self.assertTrue(os.path.exists(upload_dir + file.__unicode__()))
			
			os.remove(upload_dir + file.__unicode__())
			self.assertFalse(os.path.exists(upload_dir + file.__unicode__()))
			
		os.remove(tempFilePath)
		self.assertFalse(os.path.exists(tempFilePath))
		
		
	def testGetUploadedFile(self):
		pass
		
	def fileIsSafe(self):
		self.assertTrue(file_is_safe("file.png"))
		self.assertTrue(file_is_safe("file.doc"))
		self.assertFalse(file_is_safe("file.exe"))
		self.assertFalse(file_is_safe("file.bat"))

	def testGetEndOfWeek(self):
		t = datetime.datetime(2010, 6, 9) #a wednesday
		self.assertEqual(datetime.datetime(2010, 6, 13, 23, 59), get_end_of_week(t))
		
		t = datetime.datetime(2010, 6, 13) #a sunday
		self.assertEqual(datetime.datetime(2010, 6, 13, 23, 59), get_end_of_week(t))
		
		t = datetime.datetime(2010, 6, 7) #a monday
		self.assertEqual(datetime.datetime(2010, 6, 13, 23, 59), get_end_of_week(t))

	def testGetEndOfNextWeek(self):
		t = datetime.datetime(2010, 6, 9)
		self.assertEqual(datetime.datetime(2010, 6, 20, 23, 59), get_end_of_next_week(t))
		
		t = datetime.datetime(2010, 6, 13)
		self.assertEqual(datetime.datetime(2010, 6, 20, 23, 59), get_end_of_next_week(t))

	def testGetEndOfNextThreeWeeks(self):
		t = datetime.datetime(2010, 6, 9)
		
		self.assertEqual(datetime.datetime(2010, 7, 4, 23, 59), get_end_of_next_three_weeks(t))
		

class AssignmentViewTest(TestCase):
	fixtures = ["auth_fixtures.json", "course_fixtures.json", "assignment_fixtures.json"]

	def testAssignments(self):
		self.assertTrue(Assignment.objects.filter(name="Homework 1").exists())

		
	def testAllAssignments(self):
		c = self.login('instructor', 'teacher')
		
		try:
			course = Course.objects.get(pk=1)
			
			response = c.get("/courses/%s/assignments/" % course.get_url())
			self.assertEqual(response.status_code, 200)
			
		except Course.DoesNotExist:
			self.fail("Could not find course")
	
	def testGetUpcoming(self):
		c = self.login('instructor', 'teacher')
		
		try:
			course = Course.objects.get(pk=1)
			
			url = "/courses/%s/assignments/" % course.get_url()
			
			response = c.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
			self.assertEqual(response.status_code, 200)
			
		except Course.DoesNotExist:
			self.fail("Could not find course")
		
	def testAverageGrades(self):
		c = self.login('instructor', 'teacher')
		
		try:
			course = Course.objects.get(pk=1)
			
			url = "/courses/%s/assignments/average/" % course.get_url()
			
			response = c.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
			self.assertEqual(response.status_code, 200)
			
			c.logout()
			
			c = self.login('student1', 'student')
			
			response = c.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
			self.assertEqual(response.status_code, 200)
			
		except Course.DoesNotExist:
			self.fail("Course not found")
	
	def testAddGroup(self):
		c = self.login('instructor', 'teacher')
		
		try:
			course = Course.objects.get(pk=1)
			
			response = c.get("/courses/%s/assignments/groups/add/" % course.get_url(), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
			self.assertEqual(response.status_code, 200)
			
			response = c.post("/courses/%s/assignments/groups/add/" % course.get_url(), {'name': "Group 2", 'weight': 40}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
			self.assertEqual(response.status_code, 200)
			json_response = json.loads(response.content)
			
			self.assertTrue(AssignmentGroup.objects.filter(id=json_response['group']['id']).exists())
			
			response = c.post("/courses/%s/assignments/groups/add/" % course.get_url(), {'name': "", 'weight': 40}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
			self.assertEqual(response.status_code, 200)
			json_response = json.loads(response.content)
			self.assertFalse(json_response['success'])
			
			response = c.post("/courses/%s/assignments/groups/add/" % course.get_url(), {'name': "Group 3"}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
			self.assertEqual(response.status_code, 200)
			json_response = json.loads(response.content)
			self.assertTrue(json_response['success'])
			self.assertTrue(AssignmentGroup.objects.filter(id=json_response['group']['id']).exists())
			
		except Course.DoesNotExist:
			self.fail("Could not find course")
			
	def testChangeGroupWeight(self):
		c = self.login('instructor', 'teacher')
		
		try:
			course = Course.objects.get(pk=1)
			
			group = course.groups.all()[0]
			
			response = c.get("/courses/%s/assignments/groups/%d/change/" % (course.get_url(), group.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
			self.assertEqual(response.status_code, 200)
			
			response = c.post("/courses/%s/assignments/groups/%d/change/" % (course.get_url(), group.id), {'weight': 10}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
			self.assertEqual(response.status_code, 200)
			json_response = json.loads(response.content)
			self.assertTrue(json_response['success'])
			self.assertEquals(json_response['weight'], 10)
			self.assertEquals(AssignmentGroup.objects.get(id=group.id).weight, 10)
			
			response = c.post("/courses/%s/assignments/groups/%d/change/" % (course.get_url(), group.id), {'weight': "30"}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
			self.assertEqual(response.status_code, 200)
			json_response = json.loads(response.content)
			self.assertEquals(json_response['weight'], 30)
			
			response = c.post("/courses/%s/assignments/groups/%d/change/" % (course.get_url(), group.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
			self.assertEqual(response.status_code, 200)
			json_response = json.loads(response.content)
			self.assertEquals(json_response['weight'], None)
			
		except Course.DoesNotExist:
			self.fail("Could not find course")
			
	def testDeleteGroup(self):
		c = self.login('instructor', 'teacher')
		
		try:
			course = Course.objects.get(pk=1)
			
			homework_group = course.groups.get(name="Homework")
			tests_group = course.groups.get(name="Tests")
			presentations_group = course.groups.get(name="Presentations")
			
			response = c.get("/courses/%s/assignments/groups/%d/delete/" % (course.get_url(), homework_group.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
			self.assertEqual(response.status_code, 200)
			
			self.assertTrue(homework_group.assignments.all().exists())
			self.assertEqual(tests_group.assignments.all().count(), 1)
			self.assertFalse(presentations_group.assignments.all().exists())
			response = c.post("/courses/%s/assignments/groups/%d/delete/" % (course.get_url(), homework_group.id), {'transfer_group': tests_group.id}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
			self.assertEqual(response.status_code, 200)
			json_response = json.loads(response.content)
			self.assertTrue(json_response['success'])
			self.assertEqual(json_response['transfer_id'], tests_group.id)
			self.assertFalse(AssignmentGroup.objects.filter(pk=homework_group.pk).exists())
			self.assertEqual(tests_group.assignments.all().count(), 4) #assignments were transfered
			
			response = c.post("/courses/%s/assignments/groups/%d/delete/" % (course.get_url(), tests_group.id), {'transfer_group': ""}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
			self.assertEqual(response.status_code, 200)
			json_response = json.loads(response.content)
			self.assertTrue(json_response['success'])
			self.assertFalse(AssignmentGroup.objects.filter(pk=tests_group.pk).exists())
			self.assertFalse(Assignment.objects.filter(group=tests_group).exists())
		
		except Course.DoesNotExist:
			self.fail("Could not find course")
			
	def testInstructorViewAssignment(self):
		c = self.login('instructor', 'teacher')
		
		try:
			course = Course.objects.get(pk=1)
			
			assignment = course.assignments.all()[0]
			
			url = "/courses/%s/assignments/%d/" % (course.get_url(), assignment.id)
			
			response = c.get(url)
			self.assertEqual(response.status_code, 200)
			
			response = c.post(url)
			self.assertEqual(response.status_code, 200)
			
			response = c.post(url, { 'submit_type': "assignment" })
			self.assertEqual(response.status_code, 200)
			
			response = c.post(url, { 'submit_type': "assignment", 'name': "Homework A", 'type': "c",
									 'due_date_0': "2010-09-30",
									 'due_date_1_hour': "01",
									 'due_date_1_minute': "01",
									 'due_date_1_second': "01",
									 'due_date_1_meridiem': "p.m.",
									 'viewable_date_0': "2010-11-30",
									 'viewable_date_1_hour': "01",
									 'viewable_date_1_minute': "01",
									 'viewable_date_1_second': "01",
									 'viewable_date_1_meridiem': "p.m.",
									 'viewable_date': "2010-11-30 12:12:12",
									 'possible_score': 15, 'description': "description", 'group_id': assignment.group_id })
			self.assertEqual(response.status_code, 200)
			assignment = course.assignments.all()[0]
			self.assertEqual(assignment.name, "Homework A")
			self.assertEqual(assignment.possible_score, 15)
			
			response = c.post(url, { 'submit_type': "resource" })
			self.assertEqual(response.status_code, 200)

			response = c.post(url, { 'submit_type': "resource", 'type': "u", 'name': "resource1", 'url': "nytimes.com" })
			self.assertEqual(response.status_code, 200)
			self.assertTrue(assignment.resources.filter(name="resource1", url="nytimes.com").exists())
			
		except Course.DoesNotExist:
			self.fail("Could not find course")
			
	def testAddAssignment(self):
		c = self.login('instructor', 'teacher')
		
		try:
			course = Course.objects.get(pk=1)
			group = course.groups.all()[0]
			
			url = "/courses/%s/assignments/add/" % course.get_url()
			
			response = c.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
			self.assertEqual(response.status_code, 200)
			
			response = c.post(url, { 'submit_type': "assignment", 'name': "Homework A", 'type': "c",
									 'due_date_0': "2010-09-30",
									 'due_date_1_hour': "01",
									 'due_date_1_minute': "01",
									 'due_date_1_second': "01",
									 'due_date_1_meridiem': "p.m.",
									 'viewable_date_0': "2010-11-30",
									 'viewable_date_1_hour': "01",
									 'viewable_date_1_minute': "01",
									 'viewable_date_1_second': "01",
									 'viewable_date_1_meridiem': "p.m.",
									 'viewable_date': "2010-11-30 12:12:12",
									 'possible_score': 15, 'description': "description",
									 'group_id': group.id })
			self.assertEqual(response.status_code, 200)
			json_response = json.loads(response.content)
			self.assertTrue(json_response['success'])
			self.assertTrue(course.assignments.filter(name="Homework A").exists())
			
			
			
		except Course.DoesNotExist:
			self.fail("Could not find course")
			
	def testTransferAssignment(self):
		c = self.login('instructor', 'teacher')
		
		try:
			course = Course.objects.get(pk=1)
			
			assignment = course.assignments.all()[0]
			group = course.groups.exclude(id=assignment.group_id)[0]
			
			url = "/courses/%s/assignments/%d/transfer/" % (course.get_url(), assignment.id)
			
			response = c.post(url, { 'transfer_id': group.id }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
			self.assertEqual(response.status_code, 200)
			json_response = json.loads(response.content)
			self.assertTrue(json_response['success'])
			self.assertTrue(group.assignments.filter(id=assignment.id).exists())
			
			response = c.post(url, { 'transfer_id': 2342342349 }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
			self.assertEqual(response.status_code, 200)
			json_response = json.loads(response.content)
			self.assertFalse(json_response['success'])
			
			response = c.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
			self.assertEqual(response.status_code, 200)
			json_response = json.loads(response.content)
			self.assertFalse(json_response['success'])
			
		except Course.DoesNotExist:
			self.fail("Could not find course")
			
	def testDeleteAssignment(self):
		c = self.login('instructor', 'teacher')
		
		try:
			course = Course.objects.get(pk=1)
			
			assignment = course.assignments.all()[0]
			
			response = c.get("/courses/%s/assignments/%d/delete/" % (course.get_url(), assignment.id), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
			self.assertEqual(response.status_code, 200)
			json_response = json.loads(response.content)
			self.assertTrue(json_response['success'])
			self.assertFalse(course.assignments.filter(pk=assignment.pk).exists())
			
		except Course.DoesNotExist:
			self.fail("Could not find course")
			
	def testGradeSubmission(self):
		c = self.login('instructor', 'teacher')
		
		try:
			course = Course.objects.get(pk=1)
			
			assignment = course.assignments.all()[0]
			submission = assignment.submissions.all()[0]
			
			url = "/courses/%s/assignments/%d/submissions/%d/grade/" % (course.get_url(), assignment.id, submission.id)
			response = c.post(url)
			self.assertTrue(response.status_code, 200)
			
			submission = AssignmentSubmission.objects.get(id=submission.id)
			self.assertEqual(submission.score, 20)
			
			response = c.post(url, { 'score': 25 })
			self.assertTrue(response.status_code, 200)
			submission = AssignmentSubmission.objects.get(id=submission.id)
			self.assertEqual(submission.score, 25)
			
			response = c.post(url, { 'score': None })
			self.assertTrue(response.status_code, 200)
			submission = AssignmentSubmission.objects.get(id=submission.id)
			self.assertEqual(submission.score, 25)
			
		except Course.DoesNotExist:
			self.fail("Course not found")
		
	def testResetSubmission(self):
		c = self.login('instructor', 'teacher')
		
		try:
			course = Course.objects.get(pk=1)
			
			assignment = course.assignments.all()[0]
			submission = assignment.submissions.all()[0]
			
			url = "/courses/%s/assignments/%d/submissions/%d/reset/" % (course.get_url(), assignment.id, submission.id)
			response = c.post(url)
			self.assertTrue(response.status_code, 200)
			self.assertFalse(AssignmentSubmission.objects.filter(id=submission.id).exists())
			
			response = c.post(url)
			self.assertTrue(response.status_code, 200)
			self.assertFalse(AssignmentSubmission.objects.filter(id=submission.id).exists())
			
			url = "/courses/%s/assignments/%d/submissions/%d/reset/" % (course.get_url(), assignment.id, 1232138)
			response = c.post(url)
			self.assertTrue(response.status_code, 200)
			json_response = json.loads(response.content)
			self.assertFalse(json_response['success'])
			
		except Course.DoesNotExist:
			self.fail("Course not found")
		
	def testResetAllSubmission(self):
		c = self.login('instructor', 'teacher')
		
		try:
			course = Course.objects.get(pk=1)
			
			assignment = course.assignments.all()[0]
			
			url = "/courses/%s/assignments/%d/submissions/reset/" % (course.get_url(), assignment.id)
						
			self.assertEqual(assignment.submissions.count(), 3)
			response = c.post(url)
			self.assertEqual(response.status_code, 302)
			self.assertEqual(assignment.submissions.count(), 0)
			
		except Course.DoesNotExist:
			self.fail("Course not found")
		
	def testDeleteResource(self):
		c = self.login('instructor', 'teacher')
		
		try:						
			course = Course.objects.get(pk=1)
			assignment = course.assignments.all()[0]
			resource = assignment.resources.create(name="resource", type="u", url="nytimes.com")
			
			url = "/courses/%s/assignments/%d/resources/%d/delete/" % (resource.assignment.course.get_url(), resource.assignment_id, resource.id)
			
			response = c.post(url)
			self.assertEqual(response.status_code, 200)
			json_response = json.loads(response.content)
			self.assertTrue(json_response['success'])
			self.assertFalse(AssignmentResource.objects.filter(id=resource.id).exists())
			
			url = "/courses/%s/assignments/%d/resources/1231230/delete/" % (course.get_url(), assignment.id)
			response = c.post(url)
			self.assertEqual(response.status_code, 200)
			json_response = json.loads(response.content)
			self.assertFalse(json_response['success'])
			
		except Course.DoesNotExist:
			self.fail("Course not found")
		
	def testStudentViewAssignment(self):
		c = self.login('student1', 'student')
		
		try:
			course = Course.objects.get(pk=1)
			
			assignment = course.assignments.all()[0]
			
			url = "/courses/%s/assignments/%s/" % (course.get_url(), assignment.url_safe_name)
			
			response = c.get(url)
			self.assertEqual(response.status_code, 200)
			
			response = c.post(url)
			self.assertEqual(response.status_code, 200)
			
			assignment = course.assignments.filter(type='o')[0]
			
			url = "/courses/%s/assignments/%s/" % (course.get_url(), assignment.url_safe_name)
			
			response = c.get(url)
			self.assertEqual(response.status_code, 200)
			
			response = c.post(url)
			self.assertEqual(response.status_code, 200)
			
			OnlineQuiz.objects.get(assignment=assignment).delete()
			self.assertFalse(OnlineQuiz.objects.filter(assignment=assignment).exists())
			
			response = c.get(url)
			self.assertEqual(response.status_code, 200)
			
		except Course.DoesNotExist:
			self.fail("Course not found")
		
	def testDeleteFileSubmission(self):
		pass
		
	def testGetResource(self):
		pass
			
			