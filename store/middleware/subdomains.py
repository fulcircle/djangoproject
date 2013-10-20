from django.conf import settings
from django.core.urlresolvers import resolve, Resolver404
from django.shortcuts import redirect

from djangoproject import urls as frontend_urls
from store.models import Merchant

import sys

class MerchantSubdomainMiddleware(object):

    def process_request(self, request):
        path = request.path
        domain = request.META['HTTP_HOST']
        pieces = domain.split('.')
        redirect_path = "http://{0}{1}".format(
                settings.DEFAULT_SITE_DOMAIN, path)
        if domain == settings.DEFAULT_SITE_DOMAIN:
            return None
        try:
            resolve(path, frontend_urls)
        except Resolver404:
            # The slashes are not being appended before getting here
            resolve(u"{0}/".format(path), frontend_urls)
        try:
            merchant = Merchant.objects.get(subdomain=pieces[0])
        except Merchant.DoesNotExist:
            return redirect(redirect_path)
        request.Merchant = merchant
        return None