from django import template
from django.template.loader import get_template

register = template.Library()

def get_merchant_template(merchant, template_name):
	try:
		template_path = merchant.subdomain + '/' + template_name
		get_template(template_path)
		return template_path
	except template.TemplateDoesNotExist:
		template_path = 'default/' + template_name
		return template_path


