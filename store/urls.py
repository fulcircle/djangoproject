from django.conf.urls import patterns, url

from store import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='store.index'),
    url(r'^register$', views.register, name='store.register'),
    url(r'^login$', views.login, name='store.login'),
    url(r'^logout$', views.logout, name='store.logout'),
    url(r'^cart$', views.cart, name='store.cart'),
    url(r'^cart/add/(?P<product_id>\d+)/$', views.cartadd, name='store.cartadd'),
    url(r'^cart/update/(?P<product_id>\d+)/$', views.cartupdate, name='store.cartupdate'),
    url(r'^/cart/remove/(?P<product_id>\d+)/$', views.cartremove, name='store.cartremove'),
    url(r'^checkout$', views.checkout, name='store.checkout'),
)