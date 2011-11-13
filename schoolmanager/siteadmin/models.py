from django.db import models
from django.contrib.auth.models import User

class ExtendedUser(User):
	class Meta:
		proxy = True
		
	def to_dict(self):
		return { 'id': self.id, 'username': self.username, 'first_name': self.first_name, 'last_name': self.last_name }

