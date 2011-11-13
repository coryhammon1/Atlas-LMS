from django.db import models
from django.contrib.auth.models import User

from schoolmanager.courses.models import Course

DATE_FORMAT = "%a. %b %d, %Y at %I:%M %p"

class BulletinBoard(models.Model):
	course = models.OneToOneField(Course, related_name="bulletin_board")
	
	def to_json(self):
		bulletin_list = [] #all bulletins for bulletin board
		
		bulletins = self.bulletins.select_related("user").all().order_by("-date")
		for bulletin in bulletins:
			bulletin_list.append(bulletin.get_data_with_comments())
		
		bulletin_board_data = {'pk': self.pk, 'bulletins': bulletin_list}
		
		return bulletin_board_data
	
class Bulletin(models.Model):
	board = models.ForeignKey(BulletinBoard, related_name="bulletins")
	user = models.ForeignKey(User)
	
	title = models.CharField(max_length=50, blank=True)
	text = models.TextField()
	
	date = models.DateTimeField(auto_now_add=True)
	
	def delete(self, *args, **kwargs):
		self.notifications.all().delete() #delete notifications
		super(Bulletin, self).delete(*args, **kwargs)
	
	def get_data(self):
		return {'id': self.id, 'text': self.text, 'user': self.user.get_full_name(), 
				'title': self.title, 'date': self.date.strftime(DATE_FORMAT)}
				
	def get_data_with_comments(self):
		data = self.get_data()
		
		comment_list = []
		for comment in self.comments.select_related("user").all().order_by("date"):
			comment_list.append(comment.get_data())
			
		data.update({'comments': comment_list})
		
		return data
	
class BulletinComment(models.Model):
	bulletin = models.ForeignKey(Bulletin, related_name="comments")
	user = models.ForeignKey(User)
	
	text = models.TextField()
	
	date = models.DateTimeField(auto_now_add=True)
	
	def delete(self, *args, **kwargs):
		self.notifications.all().delete()
		super(BulletinComment, self).delete(*args, **kwargs)
		
	def get_data(self):
		return {'id': self.id, 'user': self.user.get_full_name(), 'text': self.text, 
					'date': self.date.strftime(DATE_FORMAT)}
	