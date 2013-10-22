from django.db import models
from django.contrib.auth.models import User
from decimal import *


class Merchant(models.Model):
	subdomain = models.CharField(max_length=50,primary_key=True)
	name = models.CharField(max_length=50, unique=True)


class Product(models.Model):
	name = models.CharField(max_length=50)
	price = models.DecimalField(max_digits=10, decimal_places=2)
	description = models.CharField(max_length=800)
	merchant = models.ForeignKey(Merchant)


class Order(models.Model):
	order_date = models.DateField()
	user = models.ForeignKey(User)
	products = models.ManyToManyField(Product, through='OrderItem')
	merchant = models.ForeignKey(Merchant)
	address1 = models.CharField(max_length=100, verbose_name="Street")
	address2 = models.CharField(max_length=100, verbose_name="City")
	address3 = models.CharField(max_length=100, verbose_name="Apt # / Suite")
	state = models.CharField(max_length=2, verbose_name="State")
	credit_card_name = models.CharField(max_length=100, verbose_name="Name on Card")
	credit_card_number = models.CharField(max_length=50, verbose_name="Card Number")
	credit_card_expiry = models.CharField(max_length=4, verbose_name="Card Expiration")
	total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(0.0))


class OrderItem(models.Model):
	order = models.ForeignKey(Order)
	product = models.ForeignKey(Product)
	quantity = models.PositiveIntegerField()

	class Meta:
		unique_together = (("order", "product"),)


class ShoppingCart(models.Model):
	user = models.ForeignKey(User)
	products = models.ManyToManyField(Product, through='CartItem')
	merchant = models.ForeignKey(Merchant)

	class Meta:
		unique_together = (("user", "merchant"),)


class CartItem(models.Model):
	shopping_cart = models.ForeignKey(ShoppingCart)
	product = models.ForeignKey(Product)
	quantity = models.PositiveIntegerField(default=1)

	class Meta:
		unique_together = (("shopping_cart", "product"),)


