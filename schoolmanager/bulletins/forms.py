from django import forms

from schoolmanager.utils import AjaxHelperForm
from schoolmanager.bulletins.models import *

class CommentForm(AjaxHelperForm):
	class Meta:
		model = BulletinComment
		fields = ("text",)
		
class BulletinForm(AjaxHelperForm):
	class Meta:
		model = Bulletin
		fields = ("text", "title")