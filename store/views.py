# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

def index(request):
	return HttpResponse("Hello, world.  You're at the store index")

def register(request):
	if request.method == 'GET':
		return render(request, 'store/register.html')	

	elif request.method == 'POST':
		first_name = request.POST['first_name']
		last_name = request.POST['last_name']
		email = request.POST['email']
		password = request.POST['password']

		user = User.objects.create_user(email, email, password, first_name=first_name, last_name=last_name)
		user.save()

		return HttpResponse("Successfully registered, wahoo!")

def login(request):
	if request.method == 'GET':
		return render(request, 'store/login.html')

	if request.method == 'POST':
		email = request.POST['email']
		password = request.POST['password']

		user = authenticate(username=email, password=password)
		if user is not None:
			if user.is_active:
				auth_login(request, user)
				if request.GET['next']:
					return redirect(request.GET['next'])
				else:
					return HttpResponse("User is authenticated")
			else:
				return HttpResponse("User is not authenticated")
		else:
			return HttpResponse("Username and password were incorrect.")

def logout(request):
	auth_logout(request)
	return HttpResponse("You logged out brah!")

@login_required(login_url='/store/login')
def test(request):
	return HttpResponse("You are logged in brah!")	