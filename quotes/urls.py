from django.urls import path
from . import views

urlpatterns = [
    path('', views.random_quote, name='random_quote'),
    path('add-quote/', views.add_quote, name='add_quote'),
    path('add-source/', views.add_source, name='add_source'),
    path('popular/', views.popular_quotes, name='popular_quotes'),
    path('like/<int:quote_id>/', views.like_quote, name='like_quote'),
]