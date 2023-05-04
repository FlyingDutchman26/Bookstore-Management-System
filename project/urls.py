"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app01 import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.user_login),
    path('book/list/', views.book_list),
    path('book/add/', views.book_add),
    path('book/<int:nid>/edit/', views.book_edit),
    path('book/<int:nid>/delete/', views.book_delete),
    path('book/<int:nid>/sale/',views.book_sale),
    path('user_login/',views.user_login),
    path('user_logout/',views.user_login),
    path('profile/',views.profile),
    path('create_user/',views.create_user),
    path('edit_user/<int:user_pk>/', views.edit_user, name='edit_user'),
    path('edit_password/<int:user_pk>/', views.edit_password, name='edit_password'),
    path('delete_user/<int:user_pk>/', views.delete_user, name='delete_user'),
]
