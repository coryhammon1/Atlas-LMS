import django.utils.simplejson as json

from django import forms
from django.forms.forms import BoundField

from schoolmanager.courses.models import *
from schoolmanager.utils import normalized_float, QueryList, AjaxHelperForm

from schoolmanager.assignments.models import AssignmentSubmission

class CourseForm(AjaxHelperForm):
	class Meta:
		model = Course
		exclude = ("users",)
	
	def clean(self):
		term = self.cleaned_data.get('term')
		department = self.cleaned_data.get('department')
		number = self.cleaned_data.get('number')
		section = self.cleaned_data.get('section')
		
		if Course.objects.filter(term=term, department=department, number=number, section=section).exists():
			raise forms.ValidationError("A course with this term, department, number, and section already exists.")
			
		return self.cleaned_data

class UpdateCourseForm(AjaxHelperForm):
	class Meta:
		model = Course
		exclude = ("users",)

class TermForm(AjaxHelperForm):
	name = forms.CharField(max_length=2, help_text="(FA, SP, MY)", label="Season")

	class Meta:
		model = Term
		
	def clean(self):
		name = self.cleaned_data.get('name')
		start = self.cleaned_data.get('start')
		
		if not name or not start:
			return self.cleaned_data
		
		if self.instance:
			if self.instance.name == name and self.instance.start.year == start.year:
				return self.cleaned_data
		
		if Term.objects.filter(name__iexact=name, start__year=start.year).exists():
			raise forms.ValidationError("A term already exists with this name and starting year.")
			
		end = self.cleaned_data['end']
		
		if start > end:
			raise forms.ValidationError("Starting date begins after ending date.")
			
		return self.cleaned_data
		
class DepartmentForm(AjaxHelperForm):
	class Meta:
		model = Department

class GradingSchemeForm(forms.ModelForm):
	class Meta:
		model = GradingScheme
		exclude = ("course",)


class GradingForm(forms.Form):
	def __init__(self, course, *args, **kwargs):
		super(GradingForm, self).__init__(*args, **kwargs)

		students = course.get_students().order_by("last_name", "first_name")
		
		scheme = course.get_grading_scheme()
		self.grades, created = CourseGrades.objects.get_or_create(course=course)
		
		submissions = QueryList(AssignmentSubmission.objects.select_related("assignment", "assignment__group").filter(assignment__course=course))
		
		for student in students:
			full_name = student.get_full_name()
			
			calculated_grade = course.get_grade(student, submissions)
			letter_grade = scheme.grade_for_percent(calculated_grade)
			
			try:
				initial_grade = self.grades.grades[str(student.id)]
			except KeyError:
				initial_grade = letter_grade
			
			grade_field = forms.ChoiceField(label=full_name, choices=COURSE_GRADE_LETTER_CHOICES, initial=initial_grade, help_text=letter_grade)
			grade_field.percent = normalized_float(calculated_grade)
			grade_field.student_name = full_name
			
			self.fields.update({ str(student.id): grade_field })
		
	def __iter__(self):
		for name, field in self.fields.items():
			bound_field = BoundField(self, field, name)
			bound_field.percent = field.percent
			bound_field.student_name = field.student_name
			
			yield bound_field
			
	def save(self):
		grades_data = json.dumps(self.cleaned_data)
		self.grades.grades = grades_data
		self.grades.save()