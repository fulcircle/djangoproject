from django.contrib import admin
from store.models import *

class OrderItemInline(admin.TabularInline):
	model = OrderItem 

# QA
# Change order total when quantity is updated from admin site
class OrderAdmin(admin.ModelAdmin):
	search_fields = ['products__name', 'id', 'user__email', 'user__first_name', 'user__last_name']
	list_display = ('id', 'user', 'order_date', 'merchant', 'total')
	readonly_fields = ['merchant']
	inlines=[OrderItemInline]

	def queryset(self, request):
		qs = super(OrderAdmin, self).queryset(request)
		return restricted_qs(request.user, qs)	


class ProductAdmin(admin.ModelAdmin):
	search_fields = ['name', 'merchant__name', 'price', 'description']
	list_display = ['name', 'merchant', 'price', 'description']
	readonly_fields = ['merchant']
	inlines=[OrderItemInline]

	def queryset(self, request):
		qs = super(ProductAdmin, self).queryset(request)
		return restricted_qs(request.user, qs)


def restricted_qs(user, qs):
		if user.is_superuser:
			return qs
		user_groups = user.groups.values_list('name', flat=True)
		# Get all the merchant objects that this user is a part of
		user_merchants = Merchant.objects.filter(subdomain__in=user_groups)
		if user_merchants:
			# This is a merchant, so show all the orders in merchants this user is a part of
			return qs.filter(merchant__in=user_merchants)
		else:
			return qs.none()

admin.site.register(Order, OrderAdmin)
admin.site.register(Product, ProductAdmin)