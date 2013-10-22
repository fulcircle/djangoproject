# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from store.models import *
from store.forms import *
from django.db import transaction
from django import forms
import datetime
import sys

def index(request):
	return render(request, request.Merchant.subdomain + '/index.html',
							  {'product_list': Product.objects.filter(merchant=request.Merchant)})

# QA:
# 1. validate email, first/last name, password length
# 2. handle issue with someone trying to register again
@transaction.commit_on_success
def register(request):

	if request.method == 'POST':
		form = RegisterForm(request.POST, error_class=DivErrorList)
		if form.is_valid():
			first_name = form.cleaned_data['first_name']
			last_name = form.cleaned_data['last_name']
			email = form.cleaned_data['email']
			password = form.cleaned_data['password']

			user = User.objects.create_user(email, email, password, first_name=first_name, last_name=last_name)
			customers_grp = Group.objects.get(name='customers')
			user.groups.add(customers_grp)
			user.save()
			return HttpResponse("Successfully registered, wahoo!")
		else:
			return render(request, request.Merchant.subdomain + '/register.html', {'form': form})
	else:
		form = RegisterForm()
		return render(request, request.Merchant.subdomain + '/register.html', {'form':form})


def login(request):

	if request.method == 'POST':
		form = LoginForm(request.POST, error_class=DivErrorList)
		if form.is_valid():
			email = form.cleaned_data['email']
			password = form.cleaned_data['password']

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
		else:
			return render(request, request.Merchant.subdomain + '/login.html', {'form':form})
	else:
		form = LoginForm()
		return render(request, request.Merchant.subdomain + '/login.html', {'form':form})

def logout(request):
	auth_logout(request)
	return HttpResponse("You logged out brah!")

@login_required(login_url='/store/login')
def cart(request):
	shopping_cart, created = ShoppingCart.objects.get_or_create(user=request.user, merchant=request.Merchant)
	# Loop through all the items in the shopping cart and display the item info and the (editable) quantity 
	cart_items = CartItem.objects.filter(shopping_cart=shopping_cart)
	for item in cart_items:
		qty_form = UpdateQuantityForm(initial={'quantity':item.quantity})
		item.qty_form = qty_form
	return render(request, request.Merchant.subdomain + '/cart.html', {'cart_items':cart_items})

# QA:
# 1. handle adding non-existant products
# quantity of 0 will indicate we want to remove the item from the cart
@login_required(login_url='/store/login')
def cartadd(request, product_id):
	quantity = int(request.POST.get('quantity', 1))
	shopping_cart, created = ShoppingCart.objects.get_or_create(user=request.user, merchant=request.Merchant)
	product = Product.objects.get(id=product_id, merchant=request.Merchant)

	# Check if product exists already, if so, just update the quantity
	cart_item, created = CartItem.objects.get_or_create(shopping_cart=shopping_cart, product=product)

	if (created):
		cart_item.quantity = quantity
		cart_item.save()
		return redirect('store.cart')
	else:
		cart_item.quantity += quantity
		cart_item.save()
		return HttpResponse("Yo, I added " + str(quantity) + " more " + product.name + "(s) to your cart to make " + str(cart_item.quantity))

@login_required(login_url='/store/login')
def cartupdate(request, product_id):
	quantity = int(request.POST.get('quantity', 1))
	product = Product.objects.get(id=product_id, merchant=request.Merchant)
	shopping_cart, created = ShoppingCart.objects.get_or_create(user=request.user, merchant=request.Merchant)
	cart_item = CartItem.objects.get(shopping_cart=shopping_cart, product=product)
	if quantity <= 0:
		# Remove from cart
		CartItem.objects.filter(shopping_cart=shopping_cart, product=product).delete()
		return redirect('store.cart')
	else:
		cart_item.quantity = quantity
		cart_item.save() 
		return redirect('store.cart')

@login_required(login_url='/store/login')
def cartremove(request, product_id):
	shopping_cart = ShoppingCart.objects.get(user=request.user, merchant=request.Merchant)
	product = Product.objects.get(id=product_id)
	cart_items = CartItem.objects.filter(shopping_cart=shopping_cart, product=product).delete()
	return redirect('store.cart')


# QA:
# 1. verify we have at least one product to checkout
@login_required(login_url='/store/login')
@transaction.commit_on_success
def checkout(request):
	DEBUG_empty_cart = True 
	shopping_cart = ShoppingCart.objects.get(user=request.user, merchant=request.Merchant)
	cart_items = CartItem.objects.filter(shopping_cart=shopping_cart)

	# Create a new order
	order = Order(order_date=datetime.datetime.now(), user=request.user, merchant=request.Merchant)
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

