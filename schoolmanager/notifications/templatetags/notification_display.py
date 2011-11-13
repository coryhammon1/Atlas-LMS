from django import template

register = template.Library()

@register.filter
def zero_not_displayed(value):
	if value == 0:
		return ""
	else:
		return value