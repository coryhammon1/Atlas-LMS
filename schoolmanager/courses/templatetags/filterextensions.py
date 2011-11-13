from django import template

register = template.Library()

@register.filter
def truncatecharacters(value, amount):
	if value:
		if isinstance(value, str):
			s = value
		else:
			s = value.__unicode__()
			
		if len(s) > amount:
			return s[:amount] + "..."
		else:
			return s