from django.contrib import admin
from .models import (
    Veterinario, Tutor, Animal, ConsultaClinica,
    AgendamentoConsultas, RegistroVacinacao,
    RegistroVermifugos, Exames, Medicamentos
)

# Register your models here.
admin.site.register(Veterinario)

@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'telefone', 'data_nascimento', 'cidade', 'estado', 'cep')
    search_fields = ('nome', 'cpf')

# Mantenha APENAS esta forma de registro para Animal, usando o decorador
@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('nome', 'especie', 'get_idade_display', 'tutor') # Adicionei 'get_idade_display' e 'tutor' aqui, como sugeri na resposta anterior
    list_filter = ('especie', 'sexo')
    search_fields = ('nome', 'rfid', 'tutor__nome', 'tutor__cpf')
    fieldsets = (
        (None, {
            'fields': ('nome', 'especie', 'sexo', 'peso', 'rfid', 'tutor'),
        }),
        ('Informações de Idade', {
            'fields': (
                'data_nascimento_exata',
                'data_nascimento_aproximada',
                ('idade_anos', 'idade_meses', 'idade_dias'),
            ),
            'description': "Preencha APENAS UMA das opções de idade: Data Exata, Data Aproximada, ou Anos/Meses/Dias."
        }),
    )

@admin.register(AgendamentoConsultas)
class AgendamentoConsultasAdmin(admin.ModelAdmin):
    list_display = ('id_agendamento', 'animal', 'tutor', 'data_consulta')
    list_filter = ('data_consulta',)
    search_fields = ('animal__nome', 'tutor__nome') # Ajustado para 'tutor__nome' para pesquisa de FK
    ordering = ('-data_consulta',)


admin.site.register(ConsultaClinica)
admin.site.register(RegistroVacinacao)
admin.site.register(RegistroVermifugos)
admin.site.register(Exames)
admin.site.register(Medicamentos)