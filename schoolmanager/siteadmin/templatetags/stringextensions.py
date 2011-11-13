from django import template

register = template.Library()

@register.filter
def startswith(value, f):
	if value:
		if isinstance(value, unicode) or isinstance(value, str):
			return value.startswith(f)
	return False