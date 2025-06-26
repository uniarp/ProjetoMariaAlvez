from django.urls import path
from .views import (
    relatorios_index, relatorio_consultas,
    relatorio_estoque, relatorio_vacinacao,
    relatorio_vermifugos
)
from . import views

urlpatterns = [
    path('relatorios/', relatorios_index, name='relatorios_index'),
    path('relatorios/consultas/', relatorio_consultas, name='relatorio_consultas'),
    path('relatorios/estoque/', relatorio_estoque, name='relatorio_estoque'),
    path('relatorios/vacinacao/', relatorio_vacinacao, name='relatorio_vacinacao'),
    path('relatorios/vermifugos/', relatorio_vermifugos, name='relatorio_vermifugos'),
    path('admin/painel-gerencial/', views.painel_gerencial, name='painel_gerencial'),
]