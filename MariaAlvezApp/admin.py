# MariaAlvezApp/admin.py
from django.contrib import admin
from .models import (
    Veterinario,
    Tutor,
    Animal,
    ConsultaClinica,
    AgendamentoConsultas,
    RegistroVacinacao,
    RegistroVermifugos,
    Exames,
    Medicamentos
)

#Veterinario (essenciais para ConsultaClinica)
@admin.register(Veterinario)
class VeterinarioAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

#Tutor (essenciais para ConsultaClinica)
@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

#Animal
@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('nome', 'especie', 'tutor')
    search_fields = ('nome', 'especie', 'rfid')
    autocomplete_fields = ('tutor',)

#Exames (essenciais para ConsultaClinica)
@admin.register(Exames)
class ExamesAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

#Medicamentos (essenciais para ConsultaClinica)
@admin.register(Medicamentos)
class MedicamentosAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)


# ConsultaClinica
@admin.register(ConsultaClinica)
class ConsultaClinicaAdmin(admin.ModelAdmin):
    autocomplete_fields = ('vet_responsavel', 'animal', 'exames')
    list_display = ('animal', 'data_atendimento', 'vet_responsavel', 'tipo_atendimento')
    search_fields = ('animal__nome', 'vet_responsavel__nome', 'diagnostico')

#AgendamentoConsultas (essenciais para ConsultaClinica)
@admin.register(AgendamentoConsultas)
class AgendamentoConsultasAdmin(admin.ModelAdmin):
    list_display = ('data_consulta', 'tutor', 'animal')
    search_fields = ('data_consulta', 'tutor__nome', 'animal__nome')

admin.site.register(RegistroVacinacao)
admin.site.register(RegistroVermifugos)