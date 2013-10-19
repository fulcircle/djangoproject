# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.control.auth import authenticate

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
				return HttpResponse("User is authenticated")
			else:
				return HttpResponse("User is not authenticated")
		else:
			return HttpResponse("Username and password were incorrect.")

