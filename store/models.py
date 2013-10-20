from django.db import models
from django.contrib.auth.models import User


class Merchant(models.Model):
	domain = models.URLField(max_length=50,primary_key=True)
	name = models.CharField(max_length=50)


class Product(models.Model):
	name = models.CharField(max_length=50)
	price = models.DecimalField(max_digits=10, decimal_places=2)


class Order(models.Model):
	order_date = models.DateField()
	user = models.ForeignKey(User)
	products = models.ManyToManyField(Product, through='OrderItem')


class OrderItem(models.Model):
	order = models.ForeignKey(Order)
	product = models.ForeignKey(Product)
	quantity = models.PositiveIntegerField()

	class Meta:
		unique_together = (("order", "product"),)


class ShoppingCart(models.Model):
	user = models.OneToOneField(User, primary_key=True)
	products = models.ManyToManyField(Product, through='CartItem')


class CartItem(models.Model):
	shopping_cart = models.ForeignKey(ShoppingCart)
	product = models.ForeignKey(Product)
	quantity = models.PositiveIntegerField(default=1)

	class Meta:
		unique_together = (("shopping_cart", "product"),)

