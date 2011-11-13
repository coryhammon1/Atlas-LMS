import re
import traceback

import django.utils.simplejson as json

from django import forms
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

def normalized_float(dec):
	dec_string = "%.2f" % dec
	
	dec_string = dec_string.rstrip("0")
	
	if dec_string.endswith("."):
		dec_string = dec_string[:-1]
		
	return dec_string


def flatten(l):
	out = []
	for item in l:
		if isinstance(item, (list, tuple)):
			out.extend(flatten(item))
		else:
			out.append(item)
	return out


def remove_empty_values(l):
	out = []
	if isinstance(l, list):
		for item in l:
			if item:
				out.append(item)
	
	return out


def render_with_context(request, template, context={}):
	return render_to_response(template, context, context_instance=RequestContext(request))


def is_superuser_or_staff(user):
	return user.is_superuser or user.is_staff

def dict_map(func, iter):
	d = {}
	for item in iter:
		d.update({item: func(item)})
		
	return d
	
	
def chunk_list(l, size):
	for i in xrange(0, len(l), size):
		yield l[i:i+size]

"""
	gets the last integer that occurs in the string
"""
def parse_last_int(s):
	match = re.search(r'\d+$', s)
	if match:
		return int(match.group())
	else:
		return None


"""
	Does not span relationships ("assignment" is ok, "assignment__course" does not work)
"""
class QueryList(object):
	def __init__(self, queryset):
		self.objects = list(queryset)
		self.ordered = False
	
	def _matches(self, object, filters):
		matches = True
		for attribute, value in filters.items():
			attribute_components = attribute.split("__")
						
			comparator = object
			for component in attribute_components:
				if component != "isnull":
					comparator = comparator.__getattribute__(component)
					
			if "isnull" in attribute_components:
				is_null = comparator is None
				
				if value != is_null:
					matches = False
					break
			else:
				if comparator != value:
					matches = False
					break
				
		return matches
	
	def filter(self, *args, **kwargs):
		l = []
		for object in self.objects:
			if self._matches(object, kwargs):
				l.append(object)
				
		return QueryList(l)
	
	def exclude(self, *args, **kwargs):
		l = []
		for object in self.objects:
			if not self._matches(object, kwargs):
				l.append(object)
								
		return QueryList(l)
	
	def count(self, *args, **kwargs):
		c = 0
		for object in self.objects:
			if self._matches(object, kwargs):
				c += 1
			
		return c
	
	def order_by(self, *args, **kwargs):
		"""
			Order objects by the given arguments.  Cannot order by related models
			yet ("assignment__course" will NOT work)
		"""
		unsorted_objects = list(self.objects)
		for arg in args:
			arg = arg.replace("__", ".")
		
			reverse = False
			if arg.startswith("-"):
				reverse = True
				arg = arg[1:]
			unsorted_objects.sort(key=lambda object: object.__getattribute__(arg), reverse=reverse)
		
		sorted_list = QueryList(unsorted_objects)
		sorted_list.ordered = True
		
		return sorted_list
	
	def group_by(self, param):
		"""
			Group objects by a parameter (i.e., group courses by term)
		"""
		
		param_list = []
		for obj in self.objects:
			obj_param = obj.__getattribute__(param)
			
			try:
				index = param_list.index(obj_param)
				param_list[index]._object_list.append(obj)
			except ValueError:
				obj_param._object_list = [obj]
				param_list.append(obj_param)
				
		return param_list
		
	
	def __iter__(self):
		for object in self.objects:
			yield object
	
	def __len__(self):
		return len(self.objects)
		
	def __getitem__(self, key):
		return self.objects[key]
		
	def __setitem__(self, key, value):
		self.objects[key] = value
		
	def __delitem__(self, key):
		del self.objects[key]
		
	def __contains__(self, item):
		return item in self.objects
	
	def __str__(self):
		return str(self.objects)

"""
	Compiles errors into a dictionary for easy json compilation
"""
class AjaxHelperForm(forms.ModelForm):
	def compile_errors(self):
		compiled_errors = {}
		for field, error in self.errors.items():
			compiled_errors.update({ field: error.as_text() })
		compiled_errors = { 'success': False, 'errors': compiled_errors }
		return compiled_errors
		
class JsonResponse(HttpResponse):
	def __init__(self, content):
		super(JsonResponse, self).__init__(json.dumps(content), mimetype="json/text")
		
		
		