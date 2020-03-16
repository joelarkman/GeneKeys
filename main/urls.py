from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='main-home'),
    path('panels/<int:pk>/', views.panel_keys, name='panel_keys'),
    path('panels/<int:pk>/addkey/', views.add_key, name='add_key'),
    path('ajax/load-genes/', views.load_genes, name='ajax_load_genes'),

    path('panels/<int:pk>/pendingkeys/',
         views.pending_keys, name='pending_keys'),

    path('panels/<int:pk>/<int:key>/archive/',
         views.key_archive, name='key_archive'),

    path('panels/<int:pk>/<int:key>/comment/',
         views.key_comment, name='key_comment'),

    path('panels/<int:pk>/<int:panel_gene>/edit/',
         views.panel_gene_edit, name='panel_gene_edit')


]
