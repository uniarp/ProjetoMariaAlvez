from django.contrib import admin
from .models import (
    Veterinario, Tutor, Animal, ConsultaClinica,
    AgendamentoConsultas, RegistroVacinacao,
    RegistroVermifugos, Exames, Medicamentos
)
@admin.register(RegistroVacinacao)
class RegistroVacinacao(admin.ModelAdmin):
    list_display = ('animal', 'medicamento', 'data_aplicacao', 'data_revacinacao')
    search_fields = ('animal__nome', 'medicamento__nome')  # Assumindo que Animal e Medicamentos têm campo 'nome'
    list_filter = ('data_aplicacao', 'data_revacinacao')
    ordering = ('-data_aplicacao',)

@admin.register(RegistroVermifugos)
class RegistroVermifugos(admin.ModelAdmin):
    list_display = ('animal', 'medicamento', 'data_administracao', 'data_readministracao')
    search_fields = ('animal__nome', 'medicamento__nome')  # Assumindo que Animal e Medicamentos têm campo 'nome'
    list_filter = ('data_administracao', 'data_readministracao')
    ordering = ('-data_administracao',)
# Register your models here.
admin.site.register(Veterinario)
admin.site.register(Tutor)
admin.site.register(Animal)
admin.site.register(ConsultaClinica)
admin.site.register(AgendamentoConsultas)
admin.site.register(Exames)
admin.site.register(Medicamentos)

