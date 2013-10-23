djangoproject
=============

Simple store app

Requirements:
--------------
* django 1.5
* Python 2.7.3


Description
--------------
This is a simple store app written in Python/Django.  The app can be found in the 'store' directory.  

How to Use
--------------
You *must* setup routing on your local machine (e.g. editing /etc/hosts) to reroute cats.example.com, hats.example.com, and mats.example.com to localhost.  Those three URLs are the stores that this django project will be demoing. 

Then, it should be as simple as executing
```
python manage.py runserver
````
from the project root folder.  The database is already setup with some initial users for testing.  Then, just navigate to cats.example.com, mats.example.com, or hats.example.com

Users:
login: admin@example.com / pw: admin -- superuser

login: cat_cattington@example.com / pw: cat -- part of the 'cat' group, can edit all orders/items in the cat store

login: mat_mattington@example.com / pw: mat -- part of the 'mat' group, can edit all orders/items in the mat store

login: hat_hattington@example.com / pw: hat -- part of the 'hat' group, can edit all orders/items in the hat store

login: jon_doe@example.com / pw: jon -- part of the 'customer' group, has no admin access, but can login to any of the stores
