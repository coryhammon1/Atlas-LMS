import re

from django.contrib.auth.models import User
from django.db.models import Q

class DjangoUserBackend(object):
	"""
		Save given user in backend
	"""
	def save(self, user):
		user.save()
		return user
	
	"""
		Delete given user object from backend
	"""
	def delete(self, user):
		user.delete()
		return user
	
	def filter(self, *args, **kwargs):
		pass
	
	"""
		Search users whose last name starts with the search.
	"""
	def startingwith(self, search, type):
		if type == "administrators":
			type_param = Q(is_superuser=True)
		elif type == "instructors":
			type_param = Q(is_staff=True)
		else:
			type_param = Q(is_superuser=False, is_staff=False)
			
		return User.objects.filter(Q(last_name__istartswith=search), type_param)
	
	"""
		Search users containing the given letters in username, first_name, and last_name.
		
		Creates User objects for any matching user that doesn't have one.
	"""
	def containing(self, search):
		return User.objects.filter(Q(username__icontains=search) |
								   Q(first_name__icontains=search) |
								   Q(last_name__icontains=search))
	
	"""
		Get user from backend, creating a new user object if necessary
	"""
	def get(self, username):
		return User.objects.get(username=username)
		
class LdapUserBackend(object):
	def save(self, user):
		#save to ldap
		return
		
	def delete(self, user):
		#delete from ldap
		return
		
	def startingwith(self, search, type):
		#get from ldap, starting with search
		#(whatever=search*)|(whatever=SEARCH*)
		
		#get already stored from database
		
		#for each match
			#get_or_create user object from data
			#add user to list
		#return user list
		return
		
	def containing(self, search):
		#get from ldap
		#(|(username=*blah*)|(first_name=*blah*)...)
		
		#for each match
			#get_or_create from database
		return
		
		
		
		
		
		
		
		