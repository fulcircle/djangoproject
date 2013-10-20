from django.conf.urls import patterns, url

from store import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='store.index'),
    url(r'^register$', views.register, name='store.register'),
    url(r'^login$', views.login, name='store.login'),
    url(r'^logout$', views.logout, name='store.logout'),
    url(r'^add_to_cart/(?P<product_id>\d+)/(?P<quantity>\d+)$', views.add_to_cart, name='add_to_cart'),
    url(r'^checkout$', views.checkout, name='store.checkout'),
)