from django.test import TestCase
from django.test.client import Client
from models import *
from django.core.urlresolvers import reverse

class ShoppingCartTestCase(TestCase):
	
	def setUp(self):
		u = User.objects.create_user(username="test@example.com", password="pass", first_name="Test", last_name="Testington", email="test@example.com")
		m = Merchant.objects.create(name="Test Store", subdomain="test")
		self.product = Product.objects.create(name="Test doodad", price=Decimal(12.32), description="Test item thingy", merchant=m)
		self.shopping_cart = ShoppingCart.objects.create(user=u, merchant=m)
		self.client = Client()
		# Login the client
		response = post_request(self.client, 'store.login', post_data={'email':u.username, 'password': 'pass'})

	def test_adding_item_to_cart(self):
		self.add_item_to_cart(self.product.pk, 1)
		product_quantity = self.shopping_cart.cartitem_set.get(product=self.product).quantity
		self.assertEqual(self.shopping_cart.cartitem_set.count(),1)
		self.assertEqual(product_quantity,1)

		self.add_item_to_cart(self.product.pk, 3)
		product_quantity = self.shopping_cart.cartitem_set.get(product=self.product).quantity
		self.assertEqual(product_quantity,4)

	def test_update_item_in_cart(self):
		self.add_item_to_cart(self.product.pk, 1)
		self.update_item_in_cart(self.product.pk, 3)
		product_quantity = self.shopping_cart.cartitem_set.get(product=self.product).quantity
		self.assertEqual(product_quantity, 3)

	def test_remove_item_from_cart(self):
		self.add_item_to_cart(self.product.pk, 2)
		self.remove_item_from_cart(self.product.pk)
		self.assertEqual(self.shopping_cart.cartitem_set.count(),0)

	def add_item_to_cart(self, pid, quantity):
		return post_request(self.client, 'store.cartadd', args=(pid,), post_data={'quantity':quantity})

	def update_item_in_cart(self, pid, quantity):
		return post_request(self.client, 'store.cartupdate', args=(pid,), post_data={'quantity':quantity})

	def remove_item_from_cart(self, pid):
		return get_request(self.client, 'store.cartremove', args=(pid,))


class LoginTestCase(TestCase):

	def setUp(self):
		self.user = User.objects.create_user(username="test@example.com", password="pass", first_name="Test", last_name="Testington", email="test@example.com")
		m = Merchant.objects.create(name="Test Store", subdomain="test")
		self.client = Client()

	def test_valid_login_works(self):
		response = post_request(self.client,'store.login', post_data={'email':self.user.username, 'password':'pass'})
		# Check that we got a cookie	
		self.assertEqual(len(response.client.cookies.items()),1)
		# And we get redirected to index
		self.assertTemplateUsed('test/index.html')

	def test_invalid_login_fails(self):
		response = post_request(self.client, 'store.login', post_data={'email':self.user.username, 'password':'wrongpass'})
		# Check that we don't get a cookie
		self.assertEqual(len(response.client.cookies.items()),0)

class CheckoutTestCase(TestCase):

	def setUp(self):
		self.user = User.objects.create_user(username="test@example.com", password="pass", first_name="Test", last_name="Testington", email="test@example.com")
		self.merchant = Merchant.objects.create(name="Test Store", subdomain="test")
		self.shopping_cart = ShoppingCart.objects.create(user=self.user, merchant=self.merchant)
		self.product = Product.objects.create(name="Test doodad", price=Decimal(12.32), description="Test item thingy", merchant=self.merchant)
		self.cart_item = CartItem.objects.create(shopping_cart=self.shopping_cart, product=self.product, quantity=2)
		self.client = Client()
		response = post_request(self.client, 'store.login', post_data={'email':self.user.username, 'password': 'pass'})

	def test_checkout_creates_order(self):
		self.assertEqual(Order.objects.all().count(), 0)
		response = post_request(self.client, 'store.checkout', post_data={'credit_card_name':self.user.first_name + ' ' + self.user.last_name,
															   'credit_card_number': '123456789012',
															   'credit_card_expiry': '0213',
															   'address1': '75 Test Drive',
															   'address2': 'Suite 211',
															   'address3': 'New York',
															   'state': 'NY'})
		order = Order.objects.get(user=self.user, credit_card_number='123456789012', merchant=self.merchant)
		order_items = order.orderitem_set.all()
		self.assertEqual(order_items.count(),1)
		self.assertTrue(order_items.filter(product=self.product).exists())
		self.assertTrue(order_items.filter(product=self.product).count(),2)
		# Assert that the shopping cart is now empty
		self.assertTrue(self.shopping_cart.cartitem_set.count(),0)


def post_request(client, view, post_data={}, subdomain="test", args=()):
	return client.post(reverse(view, args=args), post_data, HTTP_HOST=subdomain + ".example.com")

def get_request(client, view, get_params={}, subdomain="test", args=()):
	return client.get(reverse(view, args=args), get_params, HTTP_HOST=subdomain + ".example.com")