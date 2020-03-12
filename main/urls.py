from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='main-home'),
    path('panels/<int:pk>/', views.panel_keys, name='panel_keys'),
    path('panels/<int:pk>/addkey/', views.add_key, name='add_key')
]
