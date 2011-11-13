from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from schoolmanager.utils import AjaxHelperForm
from schoolmanager.courses.models import *

class TermForm(forms.ModelForm):
	class Meta:
		model = Term
		
class ChangeUserForm(forms.ModelForm):
	is_superuser = forms.BooleanField(label="Administrator", required=False)
	is_staff = forms.BooleanField(label="Instructor", required=False)

	password1 = forms.CharField(label="New Password", widget=forms.PasswordInput, required=False)
	password2 = forms.CharField(label="New Password confirmation", widget=forms.PasswordInput,
		help_text = "Enter the same password as above, for verification.", required=False)

	class Meta:
		model = User
		fields = ("username", "first_name", "last_name", "email", "is_superuser", "is_staff")
	
	def clean_password2(self):
		password1 = self.cleaned_data.get("password1", "")
		password2 = self.cleaned_data["password2"]
		if password1 != password2:
			raise forms.ValidationError(_("The two password fields didn't match."))
		return password2
		
	def save(self, commit=True):
		user = super(ChangeUserForm, self).save(commit=False)
		
		if self.cleaned_data["password1"]:
			user.set_password(self.cleaned_data["password1"])
		
		if commit:
			user.save()
		return user
	
class UserCreationForm(AjaxHelperForm):
	"""
	A form that creates a user, with no privileges, from the given username and password.
	"""
	username = forms.RegexField(label="Username", max_length=30, regex=r'^[\w.@+-]+$',
		help_text = "Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.",
		error_messages = { 'invalid': "This value may contain only letters, numbers and @/./+/-/_ characters." })
	password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
	password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput,
		help_text = "Enter the same password as above, for verification.")

	email = forms.EmailField(label="Email")

	user_type = forms.CharField(widget=forms.HiddenInput)

	class Meta:
		model = User
		fields = ("username", "first_name", "last_name", "email")

	def clean_username(self):
		username = self.cleaned_data["username"]
		try:
			User.objects.get(username=username)
		except User.DoesNotExist:
			return username
		raise forms.ValidationError(_("A user with that username already exists."))

	def clean_password2(self):
		password1 = self.cleaned_data.get("password1", "")
		password2 = self.cleaned_data["password2"]
		if password1 != password2:
			raise forms.ValidationError(_("The two password fields didn't match."))
		return password2

	def save(self, commit=True):
		user = super(UserCreationForm, self).save(commit=False)
		user.set_password(self.cleaned_data["password1"])

		type = self.cleaned_data["user_type"]

		if type == "administrator":
			is_staff = False
			is_superuser = True
		elif type == "instructor":
			is_staff = True
			is_superuser = False
		else:
			is_staff = False
			is_superuser = False

		user.is_staff = is_staff
		user.is_superuser = is_superuser

		if commit:
			user.save()
		return user
