import re

import time
import datetime

from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils import formats
from django.forms.extras.widgets import SelectDateWidget
from django.forms.util import ErrorList
from django.forms.models import BaseModelFormSet
from django.forms.formsets import BaseFormSet
from django.forms.forms import BoundField

from schoolmanager.utils import AjaxHelperForm
from schoolmanager.assignments.snippets import SelectTimeWidget, SplitSelectDateTimeWidget
from schoolmanager.assignments.models import *


class DateWidgetTimeSelectWidget(forms.MultiWidget):
	def __init__(self, attrs=None):
		widgets = (forms.DateInput(attrs={ 'class': "add-assignment-date-input" }),
				   SelectTimeWidget(minute_step=5, second_step=30, twelve_hr=True)
		)
		super(DateWidgetTimeSelectWidget, self).__init__(widgets, attrs)
	
	def decompress(self, value):
		if value:
			return [value.date(), value.time().replace(microsecond=0)]
		else:
			return [None, None]
			
	def format_output(self, rendered_widgets):
		rendered_widgets.insert(-1, "<br />")
		return u''.join(rendered_widgets)

class BetterDateTimeField(forms.Field):
	def __init__(self, input_formats=None, *args, **kwargs):
		super(BetterDateTimeField, self).__init__(*args, **kwargs)
		self.input_formats = input_formats
		
	def to_python(self, value):
		if value in validators.EMPTY_VALUES:
			return None
		if isinstance(value, datetime.datetime):
			return value
		if isinstance(value, datetime.date):
			return datetime.datetime(value.year, value.month, value.day)
		if isinstance(value, list):
			if len(value) != 2:
				raise ValidationError("Enter a valid date/time.")
			if value[0] in validators.EMPTY_VALUES and value[1] in validators.EMPTY_VALUES:
				return None
			value =	"%s %s" % tuple(value)
		for format in self.input_formats or formats.get_format("DATETIME_INPUT_FORMATS"):
			try:
				return datetime.datetime(*time.strptime(value, format)[:6])
			except ValueError:
				continue
				
		if value == ' 13:00:00':
			return datetime.datetime.now()
			
		raise ValidationError("Enter a valid date/time.")
		

class AssignmentForm(AjaxHelperForm):
	due_date = forms.DateTimeField(widget=DateWidgetTimeSelectWidget())
	viewable_date = forms.DateTimeField(label="Viewable by students after", widget=DateWidgetTimeSelectWidget(),
										initial=datetime.datetime.now())
	group_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
	
	def __init__(self, course, *args, **kwargs):
		super(AssignmentForm, self).__init__(*args, **kwargs)
		self.course = course
				
		instance = kwargs.get('instance', None)
		if instance:
			self.fields['group_id'].initial = instance.group_id
			self.fields['due_date'].initial = instance.due_date
				
	def clean_name(self):
		value = self.cleaned_data.get('name')
		
		if value and self.instance.name != value:
			
			if re.search(r'[^a-zA-Z0-9 ]+', value):
				raise forms.ValidationError("Name must contain only letters, numbers, and spaces.")
				
			if re.match(r'\d+', value):
				raise forms.ValidationError("Name cannot be a number.")
		
			if Assignment.objects.filter(name=value, course=self.course).exists():
				raise forms.ValidationError("Assignment '%s' already exists." % value)
		
		return value
	
	def clean_possible_score(self):
		value = self.cleaned_data.get('possible_score')
		type = self.cleaned_data.get('type')
		
		if value:
			if type == 'o':
				raise forms.ValidationError("Leave blank for assignments taken online.")
		else:
			if type != 'o':
				raise forms.ValidationError("This field is required.")
			
		return value
	
	class Meta:
		model = Assignment
		exclude = ("course", "group", "change_date", "name_url")
		
class AssignmentGroupForm(AjaxHelperForm):
	class Meta:
		model = AssignmentGroup
		exclude = ("course",)
	
class ChangeGroupWeightForm(forms.Form):
	def __init__(self, groups, *args, **kwargs):
		super(ChangeGroupWeightForm, self).__init__(*args, **kwargs)
		
		self.groups = groups
		
		for group in groups:
			self.fields.update({ group.name: forms.IntegerField(max_value=100, min_value=0, required=False) })
			
	def clean(self):
		total = 0
		blanks = 0
		for field, value in self.cleaned_data.items():
			if value:
				total += value
			else:
				blanks += 1
			
		if total < 100:
			if blanks != len(self.cleaned_data.keys()): #if not all fields are blank
				raise forms.ValidationError("Group weights must add up to 100%")
			
		return self.cleaned_data
		
	def save(self):
		for group in self.groups:
			group.weight = self.cleaned_data[group.name]
			group.save()
			
class ChangeWeightForm(forms.ModelForm):
	class Meta:
		model = AssignmentGroup
		fields = ("weight",)
						
class TransferGroupAssignmentsForm(forms.Form):
	transfer_group = forms.ModelChoiceField(queryset=None, label="Transfer assignments to", empty_label="None (Delete Assignments)", required=False)
		
	def __init__(self, group, course, *args, **kwargs):
		super(TransferGroupAssignmentsForm, self).__init__(*args, **kwargs)
		self.course = course
		
		self.fields['transfer_group'].queryset = course.groups.exclude(id=group.id)
		self.fields['transfer_group'].widget.attrs = { 'class': "transfer-id-input" }

class AssignmentGradeForm(forms.Form):
	def __init__(self, users, *args, **kwargs):
		super(AssignmentGradeForm, self).__init__(*args, **kwargs)
		
		for user in users:
			score_field = forms.IntegerField()
			score_field.user = user
			self.fields.update({ user.username: score_field })
			self.fields.update({ user.username + "-text": forms.CharField(label="Comment", widget=forms.Textarea()) })

	def __iter__(self):
		for name, field in self.fields.items():
			if name.endswith("-text"):
				continue
				
			score_field = BoundField(self, field, name)
			score_field.user = field.user
			comment_field = BoundField(self, self.fields[name + "-text"], name + "-text")
			
			yield (score_field, comment_field)

class AssignmentSubmissionForm(forms.ModelForm):
	class Meta:
		model = AssignmentSubmission
		fields = ("text",)		

class GradeAssignmentSubmissionForm(AjaxHelperForm):
	class Meta:
		model = AssignmentSubmission
		fields = ("score", "comments")

class ResourceForm(forms.ModelForm):
	file = forms.FileField(required=False)
	
	class Meta:
		model = AssignmentResource
		exclude = ("assignment", "content_type")
	
	def __init__(self, assignment, *args, **kwargs):
		super(ResourceForm, self).__init__(*args, **kwargs)
		
		self.assignment = assignment
	
	def clean_name(self):
		value = self.cleaned_data.get("name")
		
		if value and self.instance.name != value:
			if self.assignment.resources.filter(name=value).exists():
				raise forms.ValidationError("Resource with name '%s' already exists." % value)
				
		return value
	
	def clean(self):
		type = self.cleaned_data.get("type")
	
		if type == "f":
			file = self.cleaned_data.get("file")
			if not file:
				self._errors["file"] = ErrorList(["File is required."])
				del self.cleaned_data['file']
		elif type == "u":
			url = self.cleaned_data.get("url")
			if not url:
				self._errors["url"] = ErrorList(["Url is required."])
				del self.cleaned_data['url']
				
		return self.cleaned_data

	def save(self, username, commit=True):
		resource = super(ResourceForm, self).save(commit=False)
				
		if resource.type == "f":				
			file = self.files['file']
			relative_path = "%s/%d/" % (username, self.assignment.id)
			save_file_to_upload_dir(file, relative_path)
			
			resource.file = relative_path + file.__unicode__()
			
			resource.content_type = file.content_type
			
		resource.assignment = self.assignment	
		
		if commit:
			resource.save()
			
		return resource
		
		






		