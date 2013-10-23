# Create your views here.
from decimal import *
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
from django.core.urlresolvers import reverse
import datetime
import sys


def index(request):

	product_list = Product.objects.filter(merchant=request.Merchant)
	return render(request, request.Merchant.subdomain + '/index.html',
							  {'product_list': product_list})

@transaction.commit_on_success
def register(request):

	if request.method == 'POST':
		form = RegisterForm(request.POST, error_class=DivErrorList)
		if form.is_valid():
			first_name = form.cleaned_data['first_name']
			last_name = form.cleaned_data['last_name']
			email = form.cleaned_data['email']
			password = form.cleaned_data['password']
			if (User.objects.filter(username=email).exists()):
				url = reverse('store.register')
				return redirect(url + '?user_exists=1', {'form':form})
			user = User.objects.create_user(email, email, password, first_name=first_name, last_name=last_name)
			customers_grp = Group.objects.get(name='customers')
			user.groups.add(customers_grp)
			user.save()
			url = reverse('store.register')
			return redirect(url + '?register_success=1')
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
			if user is not None and user.is_active:
				auth_login(request, user)
				if 'next' in request.GET and request.GET['next']:
					return redirect(request.GET['next'])
				else:
					return redirect('store.index')
			else:
				url = reverse('store.login')
				url = url + '?failed_login=1'
				return redirect(url)
		else:
			return render(request, request.Merchant.subdomain + '/login.html', {'form':form})
	else:
		form = LoginForm()
		if 'failed_login' in request.GET:
			form.failed_login = True
		return render(request, request.Merchant.subdomain + '/login.html', {'form':form})

def logout(request):
	auth_logout(request)
	return redirect('store.index')

@login_required(login_url='/store/login')
def cart(request):
	shopping_cart, created = ShoppingCart.objects.get_or_create(user=request.user, merchant=request.Merchant)
	# Loop through all the items in the shopping cart and display the item info and the (editable) quantity 
	cart_items = CartItem.objects.filter(shopping_cart=shopping_cart)
	cart_items.total = Decimal(0.0)
	for item in cart_items:
		qty_form = UpdateQuantityForm(initial={'quantity':item.quantity})
		item.qty_form = qty_form
		item.total_price = item.quantity * item.product.price
		cart_items.total += item.total_price
	return render(request, request.Merchant.subdomain + '/cart.html', {'cart_items':cart_items})

@login_required(login_url='/store/login')
def cartadd(request, product_id):
	quantity = int(request.POST.get('quantity', 1))
	shopping_cart, created = ShoppingCart.objects.get_or_create(user=request.user, merchant=request.Merchant)
	product = Product.objects.get(id=product_id, merchant=request.Merchant)

	# Check if product exists already, if so, just update the quantity
	cart_item, created = CartItem.objects.get_or_create(shopping_cart=shopping_cart, product=product)

	if (created):
		cart_item.quantity = quantity
	else:
		cart_item.quantity += quantity

	cart_item.save()

	return redirect('store.cart')	

@login_required(login_url='/store/login')
def cartupdate(request, product_id):
	quantity = int(request.POST.get('quantity', 1))
	product = Product.objects.get(id=product_id, merchant=request.Merchant)
	shopping_cart, created = ShoppingCart.objects.get_or_create(user=request.user, merchant=request.Merchant)
	cart_item = CartItem.objects.get(shopping_cart=shopping_cart, product=product)
	if quantity <= 0:
		# Remove from cart
		CartItem.objects.filter(shopping_cart=shopping_cart, product=product).delete()
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


@login_required(login_url='/store/login')
@transaction.commit_on_success
def checkout(request):
	if request.method == 'POST':
		order = Order(order_date=datetime.datetime.now(), user=request.user, merchant=request.Merchant)
		credit_card_form = CreditCardForm(request.POST, error_class=DivErrorList, instance=order)
		shipping_info_form = ShippingInfoForm(request.POST, error_class=DivErrorList, instance=order)

		if credit_card_form.is_valid() and shipping_info_form.is_valid():

			# Place the actual order
			order.save()
			shopping_cart = ShoppingCart.objects.get(user=request.user, merchant=request.Merchant)
			cart_items = CartItem.objects.filter(shopping_cart=shopping_cart)

			# If there are no items in the shopping cart, redirect to the index
			if cart_items.count() == 0:
				return redirect('store.index')
			# Add all the shopping cart items to the order
			order_items = []
			order_total = Decimal(0.0)
			for product in shopping_cart.products.all():
				product_quantity = cart_items.get(product=product).quantity
				product_price = cart_items.get(product=product).product.price
				order_total += product_quantity * product_price
				order_items.append(OrderItem(order=order, product=product, quantity=product_quantity))

			order.total = order_total
			order.save()
			OrderItem.objects.bulk_create(order_items)

			# Empty the shopping cart
			cart_items.delete()

			return render(request, request.Merchant.subdomain + '/orderplaced.html')

		else:
			return render(request, request.Merchant.subdomain + '/checkout.html', {'credit_card_form':credit_card_form, 'shipping_info_form':shipping_info_form})

	else:
		shopping_cart, created = ShoppingCart.objects.get_or_create(user=request.user, merchant=request.Merchant)
		if 'no_items' in request.GET or shopping_cart.products.count() != 0:
			credit_card_form = CreditCardForm()
			shipping_info_form = ShippingInfoForm()
			return render(request, request.Merchant.subdomain + '/checkout.html', {'credit_card_form':credit_card_form, 'shipping_info_form':shipping_info_form})
		# If there are no items to checkout
		else:
			return redirect(reverse('store.checkout') + "?no_items=1")


@login_required(login_url='/store/login')
def vieworders(request):
	orders = Order.objects.filter(user=request.user, merchant=request.Merchant)
	for order in orders:
		order_items = OrderItem.objects.filter(order=order)
		order.items = order_items
	return render(request, request.Merchant.subdomain + '/vieworders.html', {'orders':orders})

