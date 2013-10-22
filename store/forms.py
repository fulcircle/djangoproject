from django import forms
from django.forms.util import ErrorList

class DivErrorList(ErrorList):
	def __unicode__(self):
		return self.as_divs()
	def as_divs(self):
		if not self: return u''
		return u'<div class="errorlist">%s</div>' % ''.join([u'<div class="error">%s</div>' % e for e in self])

class LoginForm(forms.Form):
	email = forms.EmailField()
	password = forms.CharField(widget=forms.PasswordInput())

class RegisterForm(forms.Form):
	first_name = forms.CharField(max_length=50)
	last_name = forms.CharField(max_length=50)
	email = forms.EmailField()
	password = forms.CharField(widget=forms.PasswordInput())

class UpdateQuantityForm(forms.Form):
	quantity = forms.IntegerField(min_value=0, max_value=99, widget=forms.TextInput(attrs={'size':'2'}))

