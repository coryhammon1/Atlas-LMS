from django import template

register = template.Library()

@register.filter
def listreverse(value):
	if value:
		if isinstance(value, list):
			value.reverse()
			return value
			
	return None

@register.filter
def listoddelements(value):
	if value:
		if isinstance(value, list):
			return value[::2]
	return None
	
@register.filter
def listevenelements(value):
	if value:
		if isinstance(value, list):
			return value[1::2]
	return None
	


@register.filter
def evenlength(value):
	if value:
		if isinstance(value, list):
			length = len(value)
			if length % 2 == 0:
				return length
			else:
				return length + 1
	return None

@register.filter
def remove(value, item):
	if value:
		if isinstance(value, list):
			try:
				value.remove(item)
			except ValueError:
				pass
	
	return value 
				