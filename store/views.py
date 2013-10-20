# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from store.models import *
from django.db import transaction
import datetime

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
# quantity of 0 will indicate we want to remove the item from the cart
@login_required(login_url='/store/login')
def add_to_cart(request, product_id, quantity):
	shopping_cart = ShoppingCart.objects.get(user=request.user)
	product = Product.objects.get(id=product_id)
	if int(quantity) <= 0:
		# Remove from cart
		CartItem.objects.filter(shopping_cart=shopping_cart, product=product).delete()
		return HttpResponse("Yo, " + product.name + " was removed from the cart, bud")

	# Check if product exists already, if so, just update the quantity
	cart_item, created = CartItem.objects.get_or_create(shopping_cart=shopping_cart, product=product)
	cart_item.quantity = quantity
	cart_item.save()
	if (not created):
		return HttpResponse("Yo, " + product.name + " quantity was updated to: " + cart_item.quantity)
	else:
		return HttpResponse("Yo, " + cart_item.quantity + " " + product.name + "(s) were added to " + shopping_cart.user.first_name + "'s cart!" )


# QA:
# 1. verify we have at least one product to checkout
@login_required(login_url='/store/login')
@transaction.commit_on_success
def checkout(request):
	DEBUG_empty_cart = True 
	shopping_cart = ShoppingCart.objects.get(user=request.user)
	cart_items = CartItem.objects.filter(shopping_cart=shopping_cart)

	# Create a new order
	order = Order(order_date=datetime.datetime.now(), user=request.user)
	order.save()

	order_items = []
	for product in shopping_cart.products.all():
		product_quantity = cart_items.get(product=product).quantity
		order_items.append(OrderItem(order=order, product=product, quantity=product_quantity))

	OrderItem.objects.bulk_create(order_items)

	# Empty the shopping cart
	if (DEBUG_empty_cart):
		cart_items.delete()

	return HttpResponse("Yo, you successfully placed an order!")




