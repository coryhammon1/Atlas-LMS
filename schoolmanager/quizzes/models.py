from django.db import models
from django.db.models import signals
from django.contrib.auth.models import User
from django.core.cache import cache

from schoolmanager.assignments.models import Assignment, AssignmentSubmission

from schoolmanager.quizzes.utils import *

QUESTION_TYPE_CHOICES = (('m', "Multiple Choice"), ('s', "Select All"))

class OnlineQuiz(models.Model):
	assignment = models.OneToOneField(Assignment, related_name="quiz")
	
	time = models.PositiveIntegerField(null=True, blank=True, help_text="(in minutes, blank for unlimited)")
		
	max_attempts = models.PositiveSmallIntegerField(null=True, blank=True, help_text="(blank for unlimited)")
	
	def __unicode__(self):
		return self.assignment.name + " Quiz"
	
def invalidate_cached_quiz(sender=None, instance=None, **kwargs):
	cache_key = "Assignment-OnlineQuiz-%d" % instance.assignment.id
	cache.delete(cache_key)
	
signals.post_save.connect(invalidate_cached_quiz, sender=OnlineQuiz)
signals.pre_delete.connect(invalidate_cached_quiz, sender=OnlineQuiz)
	
	
class QuizQuestion(models.Model):
	quiz = models.ForeignKey(OnlineQuiz, related_name="questions")
	
	type = models.CharField(max_length=1, choices=QUESTION_TYPE_CHOICES, default='c')
	text = models.TextField("Question")
	points = models.PositiveIntegerField(default=5)
	
	def __unicode__(self):
		return self.text
		
def invalidate_quizquestion_cache(sender=None, instance=None, **kwargs):
	cache_key = "OnlineQuiz-Point-Sum-%d" % instance.quiz_id
	cache.delete(cache_key)
signals.post_save.connect(invalidate_quizquestion_cache, sender=QuizQuestion)
signals.pre_delete.connect(invalidate_quizquestion_cache, sender=QuizQuestion)

	
class QuestionChoice(models.Model):
	question = models.ForeignKey(QuizQuestion, related_name="choices")

	is_correct = models.BooleanField()
	text = models.TextField("Answer")
	
	def __unicode__(self):
		return self.text

class QuizSubmission(models.Model):
	quiz = models.ForeignKey(OnlineQuiz, related_name="quiz_submissions")
	submission = models.OneToOneField(AssignmentSubmission, related_name="quiz_submission")
	choices = models.ManyToManyField(QuestionChoice, related_name="quiz_submissions")
		
	submission_count = models.PositiveSmallIntegerField(default=0)
	
	current_time = models.PositiveIntegerField(null=True)
	
	def _get_can_take(self):
		quiz = self.get_quiz()
	
		max_attempts = quiz.max_attempts
		if max_attempts:
			return self.submission_count < quiz.max_attempts
		return True
	can_take = property(_get_can_take)
	
	def _get_attempts_remaining(self):
		quiz = self.get_quiz()
	
		max_attempts = quiz.max_attempts
		if max_attempts:
			return quiz.max_attempts - self.submission_count
		return None
	attempts_remaining = property(_get_attempts_remaining)
	
	def _set_cached_quiz(self, quiz):
		self._quiz = quiz
	
	def get_quiz(self):
		if hasattr(self, '_quiz'):
			return self._quiz
		else:
			return self.quiz
	
	def get_score(self):
		score = 0
		
		for question in self.quiz.questions.all():
			correct_answers = list(question.choices.filter(is_correct=True))
			answers = list(self.choices.filter(question=question))
			
			if correct_answers == answers:
				score += question.points
	
		return score
		
	def get_choices(self):
		chosen_choices = self.choices.select_related("question").filter(question__quiz=self.quiz)
		for choice in chosen_choices:
			choice.chosen = True
		
		not_chosen_choices = QuestionChoice.objects.select_related("question").filter(question__quiz=self.quiz).exclude(id__in=chosen_choices)
			
		return list(chosen_choices) + list(not_chosen_choices)
		
		
		
		
		
		
		
		
		