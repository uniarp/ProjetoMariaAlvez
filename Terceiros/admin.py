from django.contrib import admin
from terceiros.models import EmpresaTerceirizada, RegistroServico

@admin.register(EmpresaTerceirizada)
class EmpresaTerceirizadaAdmin(admin.ModelAdmin):
    list_display = ('razao_social', 'cnpj', 'telefone')
    search_fields = ['razao_social', 'cnpj']

@admin.register(RegistroServico)
class RegistroServicoAdmin(admin.ModelAdmin):
    list_display = ('animal', 'empresa', 'data_hora_procedimento', 'valor_servico')
    list_filter = ('empresa', 'data_hora_procedimento')
    autocomplete_fields = ['animal', 'empresa']
    date_hierarchy = 'data_hora_procedimento'