from django import template
from djangoproject import settings
from django.contrib.staticfiles import finders
import sys

register = template.Library()

@register.simple_tag(takes_context=True)
def merchant_static_file(context, file_name):
	merchant = context['request'].Merchant
	static_merchant_path = settings.STATIC_URL + merchant.subdomain + '/' + file_name
	if finders.find(merchant.subdomain + '/' + file_name):
		return static_merchant_path
	else:
		return settings.STATIC_URL + 'default/' + file_name
