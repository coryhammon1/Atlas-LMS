from django.db import models
from django.contrib.auth.models import User

from schoolmanager.courses.models import Course
from schoolmanager.assignments.models import Assignment, AssignmentResource
from schoolmanager.bulletins.models import Bulletin, BulletinComment

class NotificationManager(models.Manager):
	def create_for_users(self, users, **kwargs):
		notification = self.model(**kwargs)
		notification.save()
		
		for user in users:
			notification.users.add(user)
		
		return notification
		
class Notification(models.Model):
	course = models.ForeignKey(Course, related_name="notifications")
	users = models.ManyToManyField(User, related_name="notifications")
	
	assignment = models.ForeignKey(Assignment, null=True, related_name="notifications", default=None)
	resource = models.ForeignKey(AssignmentResource, null=True, related_name="notifications", default=None)
	
	bulletin = models.ForeignKey(Bulletin, null=True, related_name="notifications", default=None)
	comment = models.ForeignKey(BulletinComment, null=True, related_name="notifications", default=None)
	
	text = models.CharField(max_length=200)
	date = models.DateTimeField(auto_now_add=True)
	is_new = models.BooleanField(default=True)
	
	objects = NotificationManager()
	
	def __unicode__(self):
		return "Notification: %s" % self.text
		
	def save(self, *args, **kwargs):
		duplicates = Notification.objects.filter(text=self.text, assignment=self.assignment, resource=self.resource, bulletin=self.bulletin, comment=self.comment)
		duplicates.delete()
		
		super(Notification, self).save(*args, **kwargs)
		
	def create_added_assignment_student_notification(course, assignment):
		text = "Assignment %s was added to %s" % (assignment.get_link(), course.get_link())
		return Notification.objects.create_for_users(course.get_students(), course=course, assignment=assignment, text=text)
	create_added_assignment_student_notification = staticmethod(create_added_assignment_student_notification)
	
	def create_added_assignment_instructor_notification(course, instructor, assignment):
		text = "Assignment %s was added to %s" % (assignment.get_instructor_link(), course.get_link())
		other_instructors = course.users.exclude(is_staff=False, is_superuser=False).exclude(pk=instructor.pk)
		return Notification.objects.create_for_users(other_instructors, course=course, assignment=assignment, text=text)
	create_added_assignment_instructor_notification = staticmethod(create_added_assignment_instructor_notification)
	
	def create_graded_assignments_notification(course, assignment, submissions):
		text = "Assignment %s was graded" % assignment.get_link()
		graded_students = []
		for submission in submissions:
			if submission.score != None:
				graded_students.append(submission.user)
		return Notification.objects.create_for_users(graded_students, course=course, assignment=assignment, text=text)
	create_graded_assignments_notification = staticmethod(create_graded_assignments_notification)
	
	def create_graded_submission_notification(course, assignment, student):
		text = "Assignment %s was graded" % assignment.get_link()
		return Notification.objects.create_for_users([student,], course=course, assignment=assignment, text=text)
	create_graded_submission_notification = staticmethod(create_graded_submission_notification)
	
	def create_added_resource_notification(course, assignment, resource):
		text = "Resource %s was added to %s" % (resource.get_link(), assignment.get_link())
		return Notification.objects.create_for_users(course.get_students(), course=course, assignment=assignment, resource=resource, text=text)
	create_added_resource_notification = staticmethod(create_added_resource_notification)	
	
	def create_submitted_assignment_notification(course, user, assignment):
		text = "%s submitted %s" % (user.get_full_name(), assignment.get_instructor_link())
		instructors = course.users.exclude(is_staff=False, is_superuser=False)
		return Notification.objects.create_for_users(instructors, course=course, assignment=assignment, text=text)
	create_submitted_assignment_notification = staticmethod(create_submitted_assignment_notification)
		
	def create_added_bulletin_notification(course, bulletin):
		return Notification.objects.create_for_users(course.users.exclude(pk=bulletin.user.pk), course=course, bulletin=bulletin)
	create_added_bulletin_notification = staticmethod(create_added_bulletin_notification)
		
	def create_added_comment_notification(course, bulletin, comment):
		return Notification.objects.create_for_users(course.users.exclude(pk=comment.user.pk), course=course, bulletin=bulletin, comment=comment)
	create_added_comment_notification = staticmethod(create_added_comment_notification)
	