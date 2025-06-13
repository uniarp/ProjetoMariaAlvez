from MariaAlvezApp import views

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('relatorio/consultas/', views.gerar_relatorio_consultas, name='relatorio_consultas'),
    path('relatorio/estoque/', views.relatorio_estoque, name='relatorio_estoque'),
    path('fila/castracao/', views.fila_castracao, name='fila_castracao'),
    path('relatorio/vacinacao/', views.relatorio_vacinacao, name='relatorio_vacinacao'),
    path('relatorio/vermifugo/', views.relatorio_vermifugo, name='relatorio_vermifugo'),
    
]
