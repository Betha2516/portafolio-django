from django.urls import path
from . import views

urlpatterns = [
       path("",views.home, name="home" ),
        path("login/",views.user_login, name="login"),
        path("logout/", views.logout_user, name="logout"),
        path("registrarse/",views.registrarse, name="registrarse")
]
