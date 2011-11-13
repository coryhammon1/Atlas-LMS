from django import template

register = template.Library()

@register.inclusion_tag('choices_form.html')
def display_choices_form(formset):
	return { 'choice_formset': formset }