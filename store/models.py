from django.db import models
from django.contrib.auth.models import User
from decimal import *
from django.contrib.sites.models import get_current_site
from djangoproject import settings
import os

class Merchant(models.Model):
	subdomain = models.CharField(max_length=50,primary_key=True)
	name = models.CharField(max_length=50, unique=True)

	def __unicode__(self):
		current_domain = get_current_site(None).domain
		return self.name + " (" + self.subdomain + "." + current_domain + ")"


class Product(models.Model):
	name = models.CharField(max_length=50)
	image = models.FileField(upload_to=settings.MEDIA_ROOT)
	price = models.DecimalField(max_digits=10, decimal_places=2)
	description = models.CharField(max_length=800)
	merchant = models.ForeignKey(Merchant)

	def get_image_url(self):
		return settings.MEDIA_URL + os.path.basename(self.image.name) 

	def __unicode__(self):
		return self.name + " (" + str(self.id) + ")"


class Order(models.Model):
	order_date = models.DateField(verbose_name="Order Date")
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

	def __unicode__(self):
		return str(self.id)


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


