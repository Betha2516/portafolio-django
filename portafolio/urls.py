from django.urls import path
from . import views

urlpatterns = [
        path("",views.home, name="home" ),
        path("login/",views.user_login, name="login"),
        path("logout/", views.logout_user, name="logout"),
        path("registrarse/",views.registrarse, name="registrarse"),
        path('proyectos/', views.proyectos_view, name='proyectos_view'),
        path('eliminar-proyecto/<int:proyecto_id>/', views.eliminar_proyecto, name='eliminar_proyecto'),
        path('buscar-proyectos/', views.buscar_proyectos, name='buscar_proyectos'), 
]
