from __future__ import division

import re
import os
import datetime

from django.conf import settings
from django.db import models
from django.db.models import Count
from django.contrib.auth.models import User
from django.utils.dateformat import DateFormat, format as date_format
from django.db.models import Q, Count, Sum
from django.db.models import signals
from django.core.cache import cache

from schoolmanager.courses.models import Course

from schoolmanager.assignments.utils import *

ASSIGNMENT_SUBMISSION_STATUS_CHOICES = ((0, "Submitted"), (1, "Graded"))
ASSIGNMENT_TYPE_CHOICES = (('c', "In Class"), ('s', "Submitted Online"), ('o', "Taken Online"))

RESOURCE_TYPE_CHOICES = (('f', "File"), ('u', "Url (Web Link)"))

class AssignmentGroup(models.Model):
	course = models.ForeignKey(Course, related_name="groups")
	
	name = models.CharField("Group Name", max_length=25, help_text="(Homework, Tests, etc.)")
	
	weight = models.PositiveSmallIntegerField(null=True, blank=True, help_text="(optional)")
	
	def __unicode__(self):
		return self.name
	
	def get_score_totals(self, student, submissions=None):
		if submissions:
			submissions = submissions.filter(assignment__group_id=self.id)
		else:
			submissions = student.submissions.select_related("assignment").filter(assignment__group=self)
		
		score_total = 0
		possible_total = 0
		for submission in submissions:
			if not submission.assignment.is_viewable:
				continue
		
			try:
				score_total += submission.score
			except TypeError:
				pass
			
			possible_total += submission.assignment.get_possible_score()

		return (score_total, possible_total)
	
	def get_weighted_grade(self, student, submissions=None):
		grade = 0.0
		
		score_total, possible_total = self.get_score_totals(student, submissions)
		
		weight = self.weight or 1
		
		try:
			grade = (score_total / possible_total) * self.weight
		except ZeroDivisionError:
			pass
			
		return grade

def invalidate_cached_group(sender=None, instance=None, **kwargs):
	group_cache_key = "AssignmentGroup-%d" % instance.id
	course_group_ids_cache_key = "Course-AssignmentGroupIds-%d" % instance.course.id
	cache.delete_many([course_group_ids_cache_key, group_cache_key])
	
signals.post_save.connect(invalidate_cached_group, sender=AssignmentGroup)
signals.pre_delete.connect(invalidate_cached_group, sender=AssignmentGroup)


class Assignment(models.Model):
	course = models.ForeignKey(Course, related_name="assignments")
	group = models.ForeignKey(AssignmentGroup, related_name="assignments")
	
	name = models.CharField(max_length=25)
	
	type = models.CharField(max_length=1, choices=ASSIGNMENT_TYPE_CHOICES, default="c")
	
	due_date = models.DateTimeField()
	change_date = models.DateTimeField(auto_now=True)
	viewable_date = models.DateTimeField(null=True, blank=True)
	
	possible_score = models.PositiveSmallIntegerField(null=True, blank=True)
	
	description = models.TextField(null=True, blank=True)
	
	class Meta:
		unique_together = ("course", "name")
	
	def _get_url_safe_name(self):
		return self.name.replace(" ", "_")
	url_safe_name = property(_get_url_safe_name)
	
	def _get_cache_key(self):
		return "Assignment-%d" % self.id
	cache_key = property(_get_cache_key)
	
	def _get_name_cache_key(self):
		return "Course-%d-Assignment-%s" % (self.course_id, self.url_safe_name)
	name_cache_key = property(_get_name_cache_key)
	
	def _get_is_viewable(self):
		if self.viewable_date:
			if self.viewable_date > datetime.datetime.now():
				return False
		return True
	is_viewable = property(_get_is_viewable)
	
	def __unicode__(self):
		return self.name
	
	def get_instructor_url(self):
		return "/courses/%s/assignments/%s/" % (self.course.get_url(), self.id)
	
	def get_instructor_link(self):
		return "<a href='%s'>%s</a>" % (self.get_instructor_url(), self.name)
	
	def get_url(self):
		return "/courses/%s/assignments/%s/" % (self.course.get_url(), self.url_safe_name)
	
	def get_link(self):
		"""links to student page"""
		return "<a href='%s'>%s</a>" % (self.get_url(), self.name)
	
	def get_possible_score(self):
		if self.type == 'o':
			""" Caches question point total for every request. (The only problem would be if
				questions are changed after point total has been calculated.  But this cannot
				happen, because point total is calculated on each request, and questions can
				only be changed in separate requests.)
			"""
			if not hasattr(self, '_question_point_total'):
				self._question_point_total = None
				try:
					cache_key = "Assignment-OnlineQuiz-%d" % self.id
					quiz = cache.get(cache_key)
					if quiz is None:
						quiz = self.quiz
						cache.add(cache_key, quiz)
					
					cache_key = "OnlineQuiz-Point-Sum-%d" % quiz.id
					self._question_point_total = cache.get(cache_key)
					if self._question_point_total is None:
						question_agg = quiz.questions.aggregate(point_sum=Sum("points"))
						self._question_point_total = question_agg['point_sum'] or 0
						cache.add(cache_key, self._question_point_total)
				except:
					self._question_point_total = 0
				
			return self._question_point_total
		else:
			return self.possible_score
	
	def due_date_time_category(self, now=datetime.datetime.now()):
		category = None
		if self.due_date < get_end_of_week(now):
			if self.due_date.weekday() == now.weekday():
				category = "Today"
			elif self.due_date.weekday() == (now + datetime.timedelta(days=1)).weekday():
				category = "Tomorrow"
			else:
				category = "This week"
		elif self.due_date < get_end_of_next_week(now):
			category = "Next week"
		elif self.due_date < get_end_of_next_three_weeks(now):
			category = "In a couple weeks"
		else:
			category = "In a while"
	
		return category
	
	def get_time_category_display(self, now=datetime.datetime.now()):
		category = self.due_date_time_category(now)
		format = None
		
		if category == "Today":
			format = "P"
		elif category == "Tomorrow":
			format = "P"
		elif category == "This week":
			format = "D, P"
		elif category == "Next week":
			format = "D, M j"
		elif category == "In a couple weeks":
			format = "D, M j"
		elif category == "In a while":
			format = "M j"
		
		return date_format(self.due_date, format)
	
	def get_submissions(self, request=None):
		course = None
		if request:
			course = request.course
		else:
			course = self.course
			
			
		#get already created submissions
		submissions = list(self.submissions.select_related("user").filter(user__is_superuser=False, user__is_staff=False))
		
		user_id_filter = None
		for submission in submissions:
			if user_id_filter:
				user_id_filter.append(submission.user_id)
			else:
				user_id_filter = [submission.user_id,]
		
		#get users who don't have a submission
		users = course.users.filter(is_superuser=False, is_staff=False)
		if user_id_filter:
			users = users.exclude(id__in=user_id_filter)
			
		#create submissions for users who don't have them
		for user in users:
			submission, created = user.submissions.get_or_create(assignment=self)
			submissions.append(submission)
			
		#sort submissions by first name
		submissions.sort(key=lambda submission: submission.user.first_name)
		#sort by last
		submissions.sort(key=lambda submission: submission.user.last_name)
		
		return submissions

	def create_submissions(self):
		submissions = self.submissions.all()
		
		user_id_filter = None
		for submission in submissions:
			if user_id_filter:
				user_id_filter.append(submission.user_id)
			else:
				user_id_filter = [submission.user_id,]
				
		if user_id_filter:
			users = course.users.get_students().exclude(id__in=user_id_filter)
		else:
			users = course.users.get_students()
			
		for user in users:
			user.submissions.create(assignment=self)
			
	def get_average_grade(self):
		submissions = self.submissions.filter(score__isnull=False)
		
		score_sum = 0
		submission_count = 0
		for submission in submissions:
			submission_count += 1
			
			score_sum += submission.score
			
		try:
			return score_sum/self.get_possible_score()/submission_count
		except ZeroDivisionError:
			return None

def invalidate_cached_assignment(sender, instance, **kwargs):
	cache.delete(instance.cache_key)

signals.post_save.connect(invalidate_cached_assignment, sender=Assignment)
signals.pre_delete.connect(invalidate_cached_assignment, sender=Assignment)


class AssignmentSubmission(models.Model):
	user = models.ForeignKey(User, related_name="submissions")
	assignment = models.ForeignKey(Assignment, related_name="submissions")
	
	date = models.DateTimeField(auto_now=True)
	status = models.SmallIntegerField(choices=ASSIGNMENT_SUBMISSION_STATUS_CHOICES, null=True)
	
	text = models.TextField()
	
	comments = models.TextField(blank=True)
	
	score = models.PositiveSmallIntegerField(null=True)

	def __unicode__(self):
		return "'%s' submission from %s" % (self.assignment, self.user.username)
	
	def get_grade(self):
		grade = None
		
		try:
			grade = self.score/self.assignment.get_possible_score()
		except ZeroDivisionError:
			pass
		except TypeError:
			pass
		
		return grade

class AssignmentFileSubmission(models.Model):
	assignment_submission = models.ForeignKey(AssignmentSubmission, related_name="files")
	
	file = models.FilePathField(unique=True)
	content_type = models.CharField(max_length=75, default="")
	
	def __unicode__(self):
		return os.path.basename(self.file)
		
	def delete(self, *args, **kwargs):
		super(AssignmentFileSubmission, self).delete(*args, **kwargs)
		
		try:
			os.remove(settings.UPLOAD_DIR + self.file)
		except os.error:
			pass
			
	def link(self):
		if hasattr(self, '_course'):
			course_name = self._course.get_url()
		else:
			course_name = self.assignment_submission.assignment.course.get_url()
		return "/courses/%s/assignments/files/%d/" % (course_name, self.id)

	def _set_cached_course(self, course):
		self._course = course


class AssignmentResource(models.Model):
	assignment = models.ForeignKey(Assignment, related_name="resources")
	
	name = models.CharField(max_length=30)
	type = models.CharField(max_length=1, default="f", choices=RESOURCE_TYPE_CHOICES)
	
	file = models.FilePathField(null=True, blank=True)
	content_type = models.CharField(max_length=75, null=True, blank=True)
	
	html = models.TextField(null=True, blank=True)

	url = models.CharField(max_length=200, null=True, blank=True)

	def __unicode__(self):
		return self.name

	def delete(self, *args, **kwargs):
		super(AssignmentResource, self).delete(*args, **kwargs)
		
		if self.file:
			try:
				os.remove(settings.UPLOAD_DIR + self.file)
			except os.error:
				pass
		
	def get_url(self):
		url = ""
		if self.type == 'f':
			if hasattr(self, '_course'):
				course = self._course
			else:
				course = self.assignment.course
			url = "/courses/%s/assignments/%s/resources/%d/" % (course.get_url(),
																self.assignment.url_safe_name, self.id)
		elif self.type == 'u':
			if not self.url.startswith("http://"):
				url = "http://" + self.url
			else:
				url = self.url
			
		return url
		
	def get_link(self):
		return "<a href='%s'>%s</a>" % (self.get_url(), self.name)

	def _set_cached_course(self, course):
		self._course = course

	def get_notification_count(self, user):
		return user.notifications.filter(resource=self, is_new=True).count()



