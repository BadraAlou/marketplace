from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('pricing/', views.pricing, name='pricing'),
    path('conseils/', views.conseils, name='conseils'),
    path('conseils/<int:pk>/', views.conseil_detail, name='conseil_detail'),
    path('contact/', views.contact, name='contact'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('product/create/', views.product_create, name='product_create'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('ajax/load-subcategories/', views.load_subcategories, name='ajax_load_subcategories'),
]