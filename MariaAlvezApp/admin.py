from django.contrib import admin
from .models import (
    Veterinario, Tutor, Animal, ConsultaClinica,
    AgendamentoConsultas, RegistroVacinacao,
    RegistroVermifugos, Exames, Medicamentos
)
admin.site.register(Veterinario)
admin.site.register(ConsultaClinica)

@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'telefone', 'data_nascimento', 'cidade', 'estado', 'cep')
    search_fields = ('nome', 'cpf')


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('nome', 'especie', 'get_idade', 'sexo', 'peso', 'rfid')
    list_filter = ('especie', 'sexo')
    search_fields = ('nome', 'rfid')

    def get_idade(self, obj):
        return f"{obj.idade_anos}a {obj.idade_meses}m {obj.idade_dias}d"
    get_idade.short_description = "Idade"

    fieldsets = (
        (None, {
            'fields': ('nome', 'especie', 'sexo', 'peso', 'rfid'),
        }),
        ('Informações de Idade', {
            'fields': (('idade_anos', 'idade_meses', 'idade_dias'),),
            'description': "Preencha a idade usando Anos, Meses e Dias."
        }),
    )
@admin.register(AgendamentoConsultas)
class AgendamentoConsultasAdmin(admin.ModelAdmin):
    list_display = ('data_consulta', 'animal', 'tutor')
    list_filter = ('data_consulta', 'tutor')
    search_fields = ('animal__nome', 'tutor__nome')
    fields = ('data_consulta', 'tutor', 'animal') 
    
@admin.register(RegistroVacinacao)
class RegistroVacinacaoAdmin(admin.ModelAdmin):
    list_display = ('animal', 'medicamento', 'data_aplicacao', 'data_revacinacao')
    search_fields = ('animal__nome', 'medicamento__nome')  # Assumindo que Animal e Medicamentos têm campo 'nome'
    list_filter = ('data_aplicacao', 'data_revacinacao')
    ordering = ('-data_aplicacao',)
    
@admin.register(RegistroVermifugos)
class RegistroVermifugosAdmin(admin.ModelAdmin):
    list_display = ('animal', 'medicamento', 'data_administracao', 'data_readministracao')
    search_fields = ('animal__nome', 'medicamento__nome')  # Assumindo que Animal e Medicamentos têm campo 'nome'
    list_filter = ('data_administracao', 'data_readministracao')
    ordering = ('-data_administracao',)
    
admin.site.register(Exames)
admin.site.register(Medicamentos)