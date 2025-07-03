from django.urls import path
from .views import (
    relatorios_index, relatorio_consultas,
    relatorio_estoque, relatorio_vacinacao,
    relatorio_vermifugos, relatorio_servicos, #
    relatorio_consultas_pdf,
    relatorio_estoque_pdf,
    relatorio_vacinacao_pdf,
    relatorio_vermifugos_pdf,
    relatorio_servicos_pdf #
)
from . import views

urlpatterns = [
    path('relatorios/', relatorios_index, name='relatorios_index'),

    path('relatorios/consultas/', relatorio_consultas, name='relatorio_consultas'),
    path('relatorios/consultas/pdf/', relatorio_consultas_pdf, name='relatorio_consultas_pdf'),

    path('relatorios/estoque/', relatorio_estoque, name='relatorio_estoque'),
    path('relatorios/estoque/pdf/', relatorio_estoque_pdf, name='relatorio_estoque_pdf'),

    path('relatorios/vacinacao/', relatorio_vacinacao, name='relatorio_vacinacao'),
    path('relatorios/vacinacao/pdf/', relatorio_vacinacao_pdf, name='relatorio_vacinacao_pdf'),

    path('relatorios/vermifugos/', relatorio_vermifugos, name='relatorio_vermifugos'),
    path('relatorios/vermifugos/pdf/', relatorio_vermifugos_pdf, name='relatorio_vermifugos_pdf'),
    
    # NOVAS URLs PARA RELATÓRIO DE SERVIÇOS
    path('relatorios/servicos/', relatorio_servicos, name='relatorio_servicos'),
    path('relatorios/servicos/pdf/', relatorio_servicos_pdf, name='relatorio_servicos_pdf'),

    path('admin/painel-gerencial/', views.painel_gerencial, name='painel_gerencial'),
]