from django.urls import path
from .import views
urlpatterns=[
    path("crud",views.crud,name="crud"),
    path("home",views.home,name="home"),
    path("read",views.read,name="read"),
    path("write",views.write,name="write"),
    path("delete",views.delete,name="delete"),
    path("create",views.create,name="create"),
    path("logverify",views.loginverify,name="loginverify"),
    path("",views.loginverify,name="loginverify"),
    path("register",views.register,name="register"),
]