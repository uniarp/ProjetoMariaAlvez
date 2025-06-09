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

admin.site.register(Animal)
admin.site.register(ConsultaClinica)
admin.site.register(AgendamentoConsultas)
admin.site.register(RegistroVacinacao)
admin.site.register(RegistroVermifugos)
admin.site.register(Exames)
admin.site.register(Medicamentos)

