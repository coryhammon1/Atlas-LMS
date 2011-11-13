import datetime

import django.utils.simplejson as json

from django.test.client import Client

from django.contrib.auth.models import User

from schoolmanager.tests.utils import TestCase

from schoolmanager.courses.models import Course
from schoolmanager.assignments.models import Assignment
from schoolmanager.quizzes.models import *
from schoolmanager.quizzes.utils import *

class QuizSubmissionModelTest(TestCase):
	fixtures = ["auth_fixtures.json", "course_fixtures.json", "assignment_fixtures.json"]
	
	def setUp(self):
		self.assignment = Assignment.objects.all()[0]
		self.quiz = OnlineQuiz.objects.create(assignment=self.assignment)
		
		self.user = User.objects.all()[0]
		
		self.submission = self.assignment.submissions.create(user=self.user)
		
		self.quiz_submission = self.quiz.quiz_submissions.create(submission=self.submission)
		
	def testGetScore(self):
		
		self.assertEqual(self.quiz_submission.get_score(), 0)
		
		multiple_choice = self.quiz.questions.create(text="First")
		select_all = self.quiz.questions.create(text="Second", type='s')
		
		first = multiple_choice.choices.create(text="First Choice", is_correct=False)
		second = multiple_choice.choices.create(text="Second Choice", is_correct=True)
		
		third = select_all.choices.create(text="Third Choice", is_correct=True)
		fourth = select_all.choices.create(text="Fourth Choice", is_correct=True)
		fifth = select_all.choices.create(text="Fifth Choice", is_correct=False)
		
		self.quiz_submission.choices.add(second, third, fourth) #both questions answered correctly
		self.assertEqual(self.quiz_submission.get_score(), 10)
		self.quiz_submission.choices.clear()
		
		#first question wrong, second right
		self.quiz_submission.choices.add(first, third, fourth)
		self.assertEqual(self.quiz_submission.get_score(), 5)
		self.quiz_submission.choices.clear()
		
		#no answer for first question, second right
		self.quiz_submission.choices.add(third, fourth)
		self.assertEqual(self.quiz_submission.get_score(), 5)
		self.quiz_submission.choices.clear()
		
		#first question right, second no right answer
		self.quiz_submission.choices.add(second, fifth)
		self.assertEqual(self.quiz_submission.get_score(), 5)
		self.quiz_submission.choices.clear()
		
		#first question right, second one right answer
		self.quiz_submission.choices.add(second, fourth, fifth)
		self.assertEqual(self.quiz_submission.get_score(), 5)
		self.quiz_submission.choices.clear()
		
		#first question right, second no answer
		self.quiz_submission.choices.add(second)
		self.assertEqual(self.quiz_submission.get_score(), 5)
		self.quiz_submission.choices.clear()

	def testGetChoices(self):
		pass

class QuizViewsTest(TestCase):
	fixtures = ["auth_fixtures.json", "course_fixtures.json", "assignment_fixtures.json"]
	
	def setUp(self):
		self.course = Course.objects.get(pk=1)
		self.assignment = self.course.assignments.all()[0]
	
	def testViewQuiz(self):
	
		url = "%squiz/" % self.assignment.get_instructor_url()

		#test deny access to student
		student = User.objects.filter(is_superuser=False, is_staff=False)[0]
		c = self.login(student.username, "student")
		response = c.get(url)
		self.assertEqual(response.status_code, 302)
		
		c = self.login("instructor", "teacher")
		response = c.get(url)
		self.assertEqual(response.status_code, 200)
		
		quiz = self.assignment.quiz
		self.assertEqual(quiz.time, None)
		
		response = c.post(url, { 'time': 20 })
		self.assertEqual(response.status_code, 200)
		
		quiz = self.assignment.quiz
		
		response = c.post(url, { 'time': "abc" })
		self.assertEqual(response.status_code, 200)
		
		self.assertFormError(response, 'form', 'time', [u'Enter a whole number.'])
		
	def testAddQuestion(self):
		url = "%squiz/questions/add/" % self.assignment.get_instructor_url()
		
		student = User.objects.filter(is_superuser=False, is_staff=False)[0]
		c = self.login(student.username, "student")
		response = c.get(url)
		self.assertEqual(response.status_code, 302)
	
		c = self.login("instructor", "teacher")
		response = c.get(url)
		self.assertEqual(response.status_code, 200)
		
		quiz, created = OnlineQuiz.objects.get_or_create(assignment=self.assignment)
		
		self.assertFalse(quiz.questions.all().exists()) #no questions exist
		
		response = c.post(url, {'text': "New Question", 'type': 'm', 'points': 5})
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertTrue(json_response['success'])
		question_data = json_response['question']
		self.assertTrue(QuizQuestion.objects.filter(id=question_data['id']).exists())
		
		response = c.post(url, {'text': ""})
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertFalse(json_response['success'])
		
	def testUpdateQuestion(self):
		quiz, created = OnlineQuiz.objects.get_or_create(assignment=self.assignment)
		question = quiz.questions.create(text="Question", type='m')
		
		url = "%squiz/questions/%d/update/" % (self.assignment.get_instructor_url(), question.id)
		
		student = User.objects.filter(is_superuser=False, is_staff=False)[0]
		
		c = self.login(student.username, "student")
		response = c.get(url)
		self.assertEqual(response.status_code, 302)
	
		c = self.login("instructor", "teacher")
		response = c.get(url)
		self.assertEqual(response.status_code, 200)
		
		response = c.post(url, {'text': "Updated Question", 'type': 's', 'points': 5})
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertTrue(json_response['success'])
		question = quiz.questions.get(id=question.id)
		self.assertEqual(question.text, "Updated Question")
		self.assertEqual(question.type, 's')
		
		response = c.post(url)
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertFalse(json_response['success'])
		
		response = c.post(url, {'text': "Updated Question 2", 'type': 'o'})
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertFalse(json_response['success'])
		
	def testDeleteQuestion(self):
		student = User.objects.filter(is_superuser=False, is_staff=False)[0]
		c = self.login(student.username, "student")
		
		quiz, created = OnlineQuiz.objects.get_or_create(assignment=self.assignment)
		question = quiz.questions.create(text="Question", type='m')
		
		url = "%squiz/questions/%d/delete/" % (self.assignment.get_instructor_url(), question.id)
		
		response = c.get(url)
		self.assertEqual(response.status_code, 302)
		self.assertTrue(QuizQuestion.objects.filter(id=question.id).exists())
		
		c = self.login("instructor", "teacher")
		
		response = c.get(url)
		self.assertEqual(response.status_code, 200)
		json_response = json.loads(response.content)
		self.assertTrue(json_response['success'])
		self.assertFalse(QuizQuestion.objects.filter(id=question.id).exists())
		
		
	def testUpdateChoices(self):
		quiz, created = OnlineQuiz.objects.get_or_create(assignment=self.assignment)
		question = quiz.questions.create(text="Question", type='m')
		
		url = "%squiz/questions/%d/choices/update/" % (self.assignment.get_instructor_url(), question.id)
		
		student = User.objects.filter(is_superuser=False, is_staff=False)[0]
		c = self.login(student.username, "student")
		response = c.get(url)
		self.assertEqual(response.status_code, 302)
		
		c = self.login("instructor", "teacher")
		response = c.get(url)
		self.assertEqual(response.status_code, 200)		
		
		
	def testTakeQuiz(self):
		self.assignment.due_date = datetime.datetime.now() + datetime.timedelta(weeks=2)
		self.assignment.save()
		
		quiz, created = OnlineQuiz.objects.get_or_create(assignment=self.assignment)
		
		url = "%squiz/" % self.assignment.get_url()
		
		student = User.objects.filter(is_superuser=False, is_staff=False)[0]
		c = self.login(student.username, "student")
		response = c.get(url)
		self.assertEqual(response.status_code, 200)
		
		
	def testStudentViewResults(self):
		student = User.objects.filter(is_staff=False, is_superuser=False)[0]
		
		assignment = Assignment.objects.filter(course__department__name="ART", name="Homework 1")[0]
		
		
class QuizUtilsTest(TestCase):
	fixtures = ["auth_fixtures.json", "course_fixtures.json", "assignment_fixtures.json"]

	def setUp(self):
		self.assignment = Assignment.objects.all()[0]
		self.quiz = OnlineQuiz.objects.create(assignment=self.assignment)

	def testGroupChoicesByQuestion(self):
		self.assertEqual(group_choices_by_question([]), [])
		
		question1 = self.quiz.questions.create(text="First")
		choice1 = question1.choices.create(text="Blah")
		choice2 = question1.choices.create(text="Blah2")
		
		question2 = self.quiz.questions.create(text="Second")
		choice3 = question2.choices.create(text="Blah3")
		
		choices = [choice1, choice2, choice3]
		correct_grouped_list = [{'id': question1.id, 'text': question1.text, 'points': question1.points, 'choices': [choice1, choice2]}, {'id': question2.id, 'text': question2.text, 'points': question2.points, 'choices': [choice3,]}]
		
		self.assertEqual(group_choices_by_question(choices), correct_grouped_list)
		
		
		
		
		
		