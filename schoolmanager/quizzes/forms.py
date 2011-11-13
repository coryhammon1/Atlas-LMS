from django import forms
from django.forms.forms import BoundField

from schoolmanager.utils import AjaxHelperForm, QueryList

from schoolmanager.quizzes.models import *

class QuizForm(forms.ModelForm):
	class Meta:
		model = OnlineQuiz
		exclude = ("assignment",)

class QuestionForm(AjaxHelperForm):
	class Meta:
		model = QuizQuestion
		exclude = ("quiz",)
		fields = ("type", "points", "text")

class ChoiceForm(AjaxHelperForm):
	class Meta:
		model = QuestionChoice
		exclude = ("question",)
		
class TakeQuizForm(forms.Form):
	def __init__(self, questions, *args, **kwargs):
		super(TakeQuizForm, self).__init__(*args, **kwargs)
		
		self.questions = questions
		
		question_ids = [question.id for question in self.questions]
			
		question_choices = QueryList(QuestionChoice.objects.filter(question__in=question_ids))
		
		for question in questions:
			label = question.text
			
			choices = []
			for choice in question_choices.filter(question_id=question.id):
				choices.append((str(choice.id), choice.text))
			
			field = None
			if question.type == 'm': #create a radiobutton input
				field = forms.ChoiceField(label=label, required=False, choices=choices, widget=forms.RadioSelect())
				field.points = question.points
						
			elif question.type == 's': #create a checkbox for each choice
				widget = forms.CheckboxSelectMultiple()
				field = forms.MultipleChoiceField(label=label, help_text="Check all that apply", required=False, choices=choices, widget=widget)
				field.points = question.points
				
			if field:
				self.fields.update({str(question.id): field})
	
	def __iter__(self):
		for name, field in self.fields.items():
			bound_field = BoundField(self, field, name)
			bound_field.points = field.points
			
			yield bound_field
		
		
		
		
		