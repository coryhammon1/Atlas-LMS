from __future__ import division

import re
import datetime

import django.utils.simplejson as json

from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db.models import Count, Sum, F
from django.db.models import signals
from django.core.cache import cache

from schoolmanager.utils import QueryList

COURSE_GRADE_LETTER_CHOICES = []
for char in "ABCDF":
	if char == "F":
		COURSE_GRADE_LETTER_CHOICES.append( (char, char) )
		break
	
	COURSE_GRADE_LETTER_CHOICES.append( (char + "+", char + "+") )
	COURSE_GRADE_LETTER_CHOICES.append( (char, char) )
	COURSE_GRADE_LETTER_CHOICES.append( (char + "-", char + "-") )


class Term(models.Model):
	name = models.CharField("Abbreviation", max_length=2, help_text="(e.g., FA, SP, MY)")
	
	start = models.DateField("Start Date")
	end = models.DateField("End Date")
	
	def __unicode__(self):
		return self.display()

	def save(self, *args, **kwargs):
		self.name = self.name.upper()
		super(Term, self).save(*args, **kwargs)

	def display(self):
		return "%s%d" % (self.name, self.start.year)

class Department(models.Model):
	name = models.CharField(max_length=4, help_text="(e.g., ART, MATH, CHEM)", unique=True)
	
	def __unicode__(self):
		return self.name
	
	def save(self, *args, **kwargs):
		self.name = self.name.upper()
		super(Department, self).save(*args, **kwargs)

	def to_dict(self):
		return { 'id': self.id, 'name': self.name }

class Course(models.Model):
	term = models.ForeignKey(Term, related_name="courses")
	department = models.ForeignKey(Department, related_name="courses")
	users = models.ManyToManyField(User, related_name="courses")
	
	name = models.CharField(max_length=50)
			
	number = models.IntegerField()
	section = models.SmallIntegerField(null=True, blank=True)

	def save(self, *args, **kwargs):
		super(Course, self).save(*args, **kwargs)
		
	def __unicode__(self):
		if self.section:
			return "%s (%d)" % (self.name, self.section)
		else:
			return self.name
		
	def shortname(self):
		name = self.department.name + str(self.number)
		if self.section:
			name += " (%d)" % self.section
		return name
		
	def get_url(self, course=None):
		if course == None:
			course = self
		
		section = ""
		if course.section:
			section = str(course.section)
		
		url = "%s%dS%s%s" % (course.department.name, course.number, section, course.term.__unicode__())
		
		return url
	
	def get_link(self):
		return "<a href='/courses/%s/'>%s</a>" % (self.get_url(), self.__unicode__())
	
	def get_grading_scheme(self):
		cache_key = "Course-GradingScheme-%d" % self.id
		scheme = cache.get(cache_key)
		if scheme is None:
			scheme, created = GradingScheme.objects.get_or_create(course=self)
			cache.add(cache_key, scheme)
		
		return scheme
	
	def get_groups(self):
		#get course's group id's
		group_ids_key = "Course-AssignmentGroupIds-%d" % self.id
		group_ids = cache.get(group_ids_key)
		if group_ids is None:
			group_ids = self.groups.values_list('id', flat=True).order_by('id')
			cache.add(group_ids_key, group_ids) #hold for five minutes
		"""
		#create a cache key for every group id
		group_keys = {}
		for group_id in group_ids:
			group_keys.update({ "AssignmentGroup-%d" % group_id: group_id })
		"""
		
		#create a cache key for every group id
		group_keys = dict([("AssignmentGroup-%d" % group_id, group_id) for group_id in group_ids])
		
		
		#get groups
		cached_groups = cache.get_many(group_keys.keys())
				
		#retrieve groups not in cache
		retrieved_groups = self.groups.exclude(id__in=cached_groups.keys())
		
		#put retrieved groups into cache
		retrieved_group_keys = dict([("AssignmentGroup-%d" % group.id, group) for group in retrieved_groups])
		"""
		retrieved_group_keys = {}
		for group in retrieved_groups:
			retrieved_group_keys.update({ "AssignmentGroup-%d" % group.id: group })
		"""
		cache.set_many(retrieved_group_keys)
		
		groups = cached_groups.values() + list(retrieved_groups)
		groups.sort(key=lambda group: group.id)
		
		return groups
				
	def get_students(self):
		return self.users.filter(is_staff=False, is_superuser=False)
	
	"""
		submissions is a QueryList of AssignmentSubmission.  groups is a QueryList of AssignmentGroup
	"""
	def get_grade(self, student, submissions=None, groups=None):
		grade = 0.0
			
		if submissions:
			submissions = submissions.filter(user_id=student.id)
		
		if groups is None:
			if not hasattr(self, '_cached_groups'):
				self._cached_groups = self.groups.all()
		
			groups = self._cached_groups
		
		weighted_grades = False
		for group in groups:
			if group.weight:
				weighted_grades = True
				break
		
		if weighted_grades:
			for group in groups:
				grade += group.get_weighted_grade(student, submissions)
		else:
			total_score = 0
			total_possible = 0
			for group in groups:
				score, possible = group.get_score_totals(student, submissions)
				
				total_score += score
				total_possible += possible
						
			try:
				grade = (total_score * 100)/total_possible
			except ZeroDivisionError:
				grade = 0.0
			
		return grade
		
		
	def get_submitted_grades(self):
		grades = list(self.grades.select_related("user").all())
		
		excluded_student_ids = None
		for grade in grades:
			if excluded_student_ids:
				excluded_student_ids.append(grade.user_id)
			else:
				excluded_student_ids = [grade.user_id,]
			
		
		if excluded_student_ids:
			students = self.get_students().exclude(id__in=excluded_student_ids)
		else:
			students = self.get_students()
			
		for student in students:
			grade, created = student.grades.get_or_create(course=self)
			grades.append(grade)
			
		grades.sort(key=lambda grade: grade.user.first_name)
		grades.sort(key=lambda grade: grade.user.last_name)
		
		return grades
			
	
class GradingScheme(models.Model):
	course = models.OneToOneField(Course, related_name="gradingscheme")
	
	a_plus = models.PositiveSmallIntegerField("A+", null=True, blank=True, default=None)
	a = models.PositiveSmallIntegerField("A", default=93)
	a_minus = models.PositiveSmallIntegerField("A-", null=True, blank=True, default=90)
	b_plus = models.PositiveSmallIntegerField("B+", null=True, blank=True, default=87)
	b = models.PositiveSmallIntegerField("B", default=83)
	b_minus = models.PositiveSmallIntegerField("B-", null=True, blank=True,default=80)
	c_plus = models.PositiveSmallIntegerField("C+", null=True, blank=True, default=77)
	c = models.PositiveSmallIntegerField("C", default=73)
	c_minus = models.PositiveSmallIntegerField("C-", null=True, blank=True, default=70)
	d_plus = models.PositiveSmallIntegerField("D+", null=True, blank=True, default=67)
	d = models.PositiveSmallIntegerField("D", default=63)
	d_minus = models.PositiveSmallIntegerField("D-", null=True, blank=True, default=60)
	
	
	def grade_for_percent(self, percent):
		if percent == None:
			return ""
	
		if self.a_plus:
			if percent >= self.a_plus:
				return "A+"
		
		if percent >= self.a:
			return "A"
			
		
		if percent >= self.a_minus:
			return "A-"
			

	
		if percent >= self.b_plus:
			return "B+"
				
		if percent >= self.b:
			return "B"
			
	
		if percent >= self.b_minus:
			return "B-"
			
			
	
		if percent >= self.c_plus:
			return "C+"
				
		if percent >= self.c:
			return "C"
			
		
		if percent >= self.c_minus:
			return "C-"
			
			
	
		if percent >= self.d_plus:
			return "D+"
			
		if percent >= self.d:
			return "D"
			
	
		if percent >= self.d_minus:
			return "D-"
			
		return "F"

def invalidate_cached_grading_scheme(sender=None, instance=None, **kwargs):
	cache_key = "Course-GradingScheme-%d" % instance.course.id
	cache.delete(cache_key)
	
signals.post_save.connect(invalidate_cached_grading_scheme, sender=GradingScheme)
signals.pre_delete.connect(invalidate_cached_grading_scheme, sender=GradingScheme)



class CourseGrades(models.Model):
	course = models.OneToOneField(Course, related_name="grades")
	
	grade_text = models.TextField()
	
	def _get_grades(self):
		if self.grade_text:
			""" Simple json doesn't created a dictionary when there are escape characters
				in the string.  Loading the first creates the string; the second creates the dict.
			"""
			
			grades = json.loads(self.grade_text)
			if grades.__class__ != dict: #if there were escape characters in grade_text
				grades = json.loads(grades)
			
			return grades
		else:
			return {}
		
	def _set_grades(self, grade_data):
		"""
			grade_data is in the form of { '<student_id>': <letter_grade> }
		"""
		self.grade_text = json.dumps(grade_data)
		
	grades = property(_get_grades, _set_grades)
	
	
	
	