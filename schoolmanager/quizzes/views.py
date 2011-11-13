import datetime
import itertools
import traceback

import django.utils.simplejson as json

from django.shortcuts import get_object_or_404, render_to_response
from django.forms.models import inlineformset_factory
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404
from django.template import loader, Context

from schoolmanager.utils import *

from schoolmanager.assignments.models import *

from schoolmanager.quizzes.models import *
from schoolmanager.quizzes.forms import *
from schoolmanager.quizzes.utils import *

@user_passes_test(is_superuser_or_staff)
def instructor_view_quiz(request, course_name, assignment_id):
	try:
		assignment = request.assignment
	except AttributeError:
		assignment = get_object_or_404(Assignment, id=assignment_id)
	
	cache_key = "Assignment-OnlineQuiz-%d" % assignment.id
	quiz = cache.get(cache_key)
	if quiz is None:
		quiz, created = OnlineQuiz.objects.get_or_create(assignment=assignment)
		cache.add(cache_key, quiz)

	questions = quiz.questions.all()
	
	ChoiceFormSet = inlineformset_factory(QuizQuestion, QuestionChoice, fk_name="question",
										  fields=("text", "is_correct"), max_num=4, extra=4)
	
	choices = QueryList(QuestionChoice.objects.select_related("question").filter(question__quiz=quiz))
	
	for question in questions:
		question.choice_formset = ChoiceFormSet(instance=question, queryset=choices.filter(question_id=question.id))

	blank_choice_formset = ChoiceFormSet()

	form = None
	if request.method == "POST":
		form = QuizForm(instance=quiz, data=request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, "Quiz was updated successfully.")
	else:
		form = QuizForm(instance=quiz)
	
	question_form = QuestionForm()
	
	return render_with_context(request, "assignments/instructor/view_quiz.html", { 'assignment': assignment,
																				   'quiz': quiz,
																				   'form': form,
																				   'question_form': question_form, 
																				   'questions': questions, 
																		'blank_choice_formset': blank_choice_formset })

@user_passes_test(is_superuser_or_staff)
def instructor_view_results(request, course_name, assignment_id, student_id):
	try:
		student = request.course.users.get(id=student_id, is_staff=False, is_superuser=False)
	except User.DoesNotExist:
		raise Http404()
	
	quiz_submission = None
	try:
		quiz_submission = QuizSubmission.objects.select_related("submission", "submission__assignment", "quiz") \
												.get(submission__assignment=request.assignment,
													 submission__user=student)
	except QuizSubmission.DoesNotExist:
		raise Http404
	
	choices = quiz_submission.get_choices()
	
	questions = group_choices_by_question(choices)
		
	return render_with_context(request, "assignments/view_results.html", { 'questions': questions, 
																		   'quiz_submission': quiz_submission,
																		   'student': student })
	
	
@user_passes_test(is_superuser_or_staff)
def instructor_add_question(request, course_name, assignment_id):
	try:
		assignment = request.assignment
	except AttributeError:
		assignment = get_object_or_404(Assignment, id=assignment_id)
	
	cache_key = "Assignment-OnlineQuiz-%d" % assignment.id
	quiz = cache.get(cache_key)
	if quiz is None:
		quiz, created = OnlineQuiz.objects.get_or_create(assignment=assignment)
		cache.add(cache_key, quiz)

	form = None
	if request.method == "POST":
		form = QuestionForm(data=request.POST)
		if form.is_valid():
			new_question = form.save(commit=False)
			new_question.quiz = quiz
			new_question.save()
			
			question_data = { 'text': new_question.text, 'id': new_question.id,
							  'type': new_question.type, 'points': new_question.points }
			response_data = { 'success': True, 'question': question_data }
			return HttpResponse(json.dumps(response_data), mimetype="json/text")
		else:
			return HttpResponse(json.dumps(form.compile_errors()), mimetype="json/text")
	else:
		form = QuestionForm()

	return render_to_response("assignments/add_question.html", { 'form': form })

@user_passes_test(is_superuser_or_staff)
def instructor_update_question(request, course_name, assignment_id, question_id):
	question = get_object_or_404(QuizQuestion, id=question_id)
	
	form = None
	if request.method == "POST":
		form = QuestionForm(instance=question, data=request.POST)
		if form.is_valid():
			form.save()
			return JsonResponse({ 'success': True, 'question': form.cleaned_data })
		else:
			return JsonResponse(form.compile_errors())
	return HttpResponse("Update Question")

@user_passes_test(is_superuser_or_staff)
def instructor_delete_question(request, course_name, assignment_id, question_id):
	deleted = True
	try:
		question = QuizQuestion.objects.get(id=question_id)
		question.delete()
	except QuizQuestion.DoesNotExist:
		question = None
		deleted = False
	
	return JsonResponse({ 'success': deleted })

@user_passes_test(is_superuser_or_staff)
def instructor_update_choices(request, course_name, assignment_id, question_id):
	question = get_object_or_404(QuizQuestion, id=question_id)
	
	initial_choice_ids = list(question.choices.values_list('id', flat=True))
	
	ChoiceFormSet = inlineformset_factory(QuizQuestion, QuestionChoice, fk_name="question",
										  fields=("text", "is_correct"), max_num=4, extra=4)

	formset = None
	if request.method == "POST":
		formset = ChoiceFormSet(instance=question, data=request.POST)
		
		if formset.is_valid():
			instances = formset.save()
			
			updated_form = ChoiceFormSet(instance=question)
			
			t = loader.get_template("choices_form.html")
			rendered_form = t.render(Context({ 'choice_formset': updated_form }))
			
			return JsonResponse({ 'success': True, 'rendered_form': rendered_form })
		else:
			return JsonResponse({ 'success': False, 'errorlist': formset.errors })
	else:
		formset = ChoiceFormSet(instance=question)
		
	return render_to_response("assignments/update_choices.html", { 'form': formset })
	
	
def student_take_quiz(request, course_name, assignment_name):
	try:
		assignment = request.assignment
	except AttributeError:
		assignment_name = assignment_name.replace("_", " ")
		assignment = get_object_or_404(Assignment, name=assignment_name, course=request.course)

	if assignment.due_date < datetime.datetime.now():
		return HttpResponseRedirect("../")

	submission, created = request.user.submissions.get_or_create(assignment=assignment)

	cache_key = "Assignment-OnlineQuiz-%d" % assignment.id
	quiz = cache.get(cache_key)
	if quiz is None:
		quiz, created = OnlineQuiz.objects.get_or_create(assignment=assignment)
		cache.add(cache_key, quiz)
	
	quiz_submission, created = QuizSubmission.objects.get_or_create(quiz=quiz, submission=submission)
	quiz_submission._set_cached_quiz(quiz) #for performance
	
	
	if not quiz_submission.can_take:
		""" message here """
		return HttpResponseRedirect("../")
	else:
		if quiz.max_attempts and request.method == "POST":
			quiz_submission.submission_count += 1
			quiz_submission.save()
	
	questions = quiz.questions.all()
	
	form = None
	if request.method == "POST":	
		form = TakeQuizForm(questions, data=request.POST)
		if form.is_valid():
			choices = flatten(form.cleaned_data.values())
			choices = remove_empty_values(choices)
			
			quiz_submission.choices = choices
			quiz_submission.is_submitted = True
			quiz_submission.save()
			
			quiz_submission.submission.score = quiz_submission.get_score()
			quiz_submission.submission.save()
			
			return HttpResponseRedirect("../")
	else:
		form = TakeQuizForm(questions)

	return render_with_context(request, "assignments/student/view_quiz.html", { 'assignment': assignment, 'quiz': quiz,
																				'questions': questions, 'form': form, 
																				'quiz_submission': quiz_submission })


def student_view_results(request, course_name, assignment_name):
	assignment_name = assignment_name.replace("_", " ")

	quiz_submission = None
	try:
		quiz_submission = QuizSubmission.objects.select_related("submission", "quiz", "submission__assignment") \
												.get(submission__assignment__name=assignment_name,
													 submission__assignment__course=request.course,
													 submission__user=request.user)
	except QuizSubmission.DoesNotExist:
		raise Http404
	
	#students cannot see results, if they can take the quiz again, or if the assignment has not expired.
	assignment_expired = quiz_submission.submission.assignment.due_date < datetime.datetime.now()
	
	if quiz_submission.can_take and not assignment_expired:
		return HttpResponseRedirect("../../")
	
	choices = quiz_submission.get_choices()
	questions = group_choices_by_question(choices)
	
	return render_with_context(request, "assignments/view_results.html", { 'questions': questions,
																		   'quiz_submission': quiz_submission })
		
		
		
		
		
		
	