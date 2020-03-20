from django.urls import path
from . import views

urlpatterns = [
    # Core views
    path('', views.home, name='main-home'),
    path('panels/<int:pk>/', views.panel_keys, name='panel_keys'),
    path('panels/<int:pk>/addkey/', views.add_key, name='add_key'),
    path('panels/<int:pk>/generate_output/',
         views.generate_output, name='generate_output'),
    path('panels/<int:pk>/pending_keys/',
         views.pending_keys, name='pending_keys'),

    # Response path to generate excel files for export.
    path('export/<int:pk>', views.generate_excel, name='generate_excel'),

    # AJAX path to load panel specific genes in Add Key form.
    path('ajax/load-genes/', views.load_genes, name='ajax_load_genes'),

    # AJAX paths to facilitate CRUD modals.
    path('panels/<int:pk>/<int:key>/archive/',
         views.key_archive, name='key_archive'),
    path('panels/<int:pk>/<int:key>/comment/',
         views.key_comment, name='key_comment'),
    path('panels/<int:pk>/<int:panel_gene>/edit/',
         views.panel_gene_edit, name='panel_gene_edit'),
    path('panels/<int:pk>/pendingkeys/<int:key>/accept',
         views.key_accept, name='key_accept'),
]
