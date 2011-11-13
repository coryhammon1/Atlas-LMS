"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""
import datetime

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from schoolmanager.courses.models import *
from schoolmanager.bulletins.models import *
from schoolmanager.notifications.models import Notification

class NotificationManagerTestCase(TestCase):
	fixtures = ["auth_fixtures.json", "course_fixtures.json", "assignment_fixtures.json", "quiz_fixtures.json"]
	
	def setUp(self):
		self.course = Course.objects.all()[0]
		self.user = self.course.users.all()[0]
	
	def testCreateForUsers(self):
		self.assertFalse(Notification.objects.all().exists())
		
		Notification.objects.create_for_users(User.objects.all(), course=self.course)
		self.assertTrue(Notification.objects.filter(course=self.course).exists())
		self.assertTrue(self.user.notifications.filter(course=self.course).exists())
		

class NotificationTestCase(TestCase):
	fixtures = ["auth_fixtures.json", "course_fixtures.json", "assignment_fixtures.json", "quiz_fixtures.json"]
	
	def setUp(self):
	
		self.students = User.objects.filter(is_staff=False, is_superuser=False)
		self.student1 = self.students[0]
		self.student2 = self.students[1]
		
		self.admin = User.objects.filter(is_superuser=True)[0]
		self.instructor = User.objects.filter(is_staff=True)[1]
		
		self.course = self.student1.courses.all()[0]
		self.assignment = self.course.assignments.all()[0]
		
		self.bulletin_board, created = BulletinBoard.objects.get_or_create(course=self.course)
		self.bulletin = self.bulletin_board.bulletins.create(title="bulletin", user=self.instructor)
		self.comment = self.bulletin.comments.create(user=self.student2)
	
	def testCreateAddedAssignmentStudentNotification(self):
		notification = Notification.create_added_assignment_student_notification(self.course, self.assignment)
		self.assertTrue(self.student1.notifications.filter(pk=notification.pk).exists())
		
	def testCreateAddedAssignmentInstructorNotification(self):
		notification = Notification.create_added_assignment_instructor_notification(self.course, self.admin, self.assignment)
		self.assertTrue(self.instructor.notifications.filter(pk=notification.pk).exists())
		
	def testCreateGradedAssignmentsNotification(self):
		notification = Notification.create_graded_assignments_notification(self.course, self.assignment, self.assignment.submissions.all())
		self.assertTrue(self.student1.notifications.filter(pk=notification.pk).exists())
		
		no_grade_student = self.assignment.submissions.filter(score__isnull=True)[0].user
		self.assertFalse(no_grade_student.notifications.filter(pk=notification.pk).exists())
	
	def testCreateGradedSubmissionNotification(self):
		notification = Notification.create_graded_submission_notification(self.course, self.assignment, self.student1)
		self.assertTrue(self.student1.notifications.filter(pk=notification.pk).exists())
	
	def testCreateAddedResourceNotification(self):
		resource = self.assignment.resources.create(name="resource")
		notification = Notification.create_added_resource_notification(self.course, self.assignment, resource)
		self.assertTrue(self.student1.notifications.filter(resource=resource).exists())
		self.assertTrue(notification.text, "Resource %s was added to %s" % (resource.get_link(), self.assignment.get_link()))
		
	def testCreateSubmittedAssignmentNotification(self):
		notification = Notification.create_submitted_assignment_notification(self.course, self.student1, self.assignment)
		self.assertTrue(self.instructor.notifications.filter(pk=notification.pk).exists())
	
	def testCreateAddedBulletinNotification(self):
		notification = Notification.create_added_bulletin_notification(self.course, self.bulletin)
		self.assertTrue(self.student1.notifications.filter(pk=notification.pk).exists())
		
	def testCreateAddedCommentNotification(self):
		notification = Notification.create_added_comment_notification(self.course, self.bulletin, self.comment)
		self.assertTrue(self.student1.notifications.filter(pk=notification.pk).exists())
		
		
		