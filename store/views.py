# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from store.models import *

def index(request):
	return HttpResponse("Hello, world.  You're at the store index")

# QA:
# 1. validate email, first/last name, password length
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
		#Create a shopping cart for this user
		shopping_cart = ShoppingCart(user=user)
		shopping_cart.save()

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

# QA:
# 1. handle adding non-existant products
@login_required(login_url='/store/login')
def add_to_cart(request, product_id, quantity):
	shopping_cart = ShoppingCart.objects.get(user=request.user)
	product = Product.objects.get(id=product_id)
	if int(quantity) <= 0:
		# Remove from cart
		ShoppingCartToProductRelation.objects.filter(shopping_cart=shopping_cart, product=product).delete()
		return HttpResponse("Yo, " + product.name + " was removed from the cart, bud")

	# Check if product exists already, if so, just update the quantity
	shopping_cart_to_product, created = ShoppingCartToProductRelation.objects.get_or_create(shopping_cart=shopping_cart, product=product)
	shopping_cart_to_product.quantity = quantity
	shopping_cart_to_product.save()
	if (not created):
		return HttpResponse("Yo, " + product.name + " quantity was updated to: " + shopping_cart_to_product.quantity)
	else:
		return HttpResponse("Yo, " + shopping_cart_to_product.quantity + " " + product.name + "(s) were added to " + shopping_cart.user.first_name + "'s cart!" )

'''
@login_required(login_url='/store/login')
def remove_from-cart(request, product_id, quantity)
	if quantity
'''