from django.contrib import admin
from django import forms
from django.utils import timezone
from datetime import timedelta
from django.utils.html import format_html # Importe para usar tags HTML personalizadas

from .models import (
    Veterinario, Tutor, Animal, ConsultaClinica,
    AgendamentoConsultas, RegistroVacinacao,
    RegistroVermifugos, Exames, EstoqueMedicamento, MovimentoEstoqueMedicamento
)

# --- Registros Simples (sem alterações complexas) ---
admin.site.register(Veterinario)
admin.site.register(ConsultaClinica)
admin.site.register(Exames)

# --- Admin para Tutor ---
@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'telefone', 'data_nascimento', 'cidade', 'estado', 'cep')
    search_fields = ('nome', 'cpf')


# --- Admin para Animal ---
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

# --- Admin para AgendamentoConsultas ---
@admin.register(AgendamentoConsultas)
class AgendamentoConsultasAdmin(admin.ModelAdmin):
    list_display = ('data_consulta', 'animal', 'tutor')
    list_filter = ('data_consulta', 'tutor')
    search_fields = ('animal__nome', 'tutor__nome')
    fields = ('data_consulta', 'tutor', 'animal')

# --- Admin para RegistroVacinacao ---
@admin.register(RegistroVacinacao)
class RegistroVacinacaoAdmin(admin.ModelAdmin):
    list_display = (
        'animal',
        'medicamento_aplicado_display', # Novo método para exibir medicamento/lote
        'data_aplicacao',
        'data_revacinacao',
        'status_revacinacao', # Novo método para exibir status da revacinação
    )
    # Atualizado search_fields e list_filter para usar medicamento_aplicado__
    search_fields = ('animal__nome', 'medicamento_aplicado__medicamento', 'medicamento_aplicado__lote')
    list_filter = ('data_aplicacao', 'data_revacinacao', 'medicamento_aplicado__medicamento')
    ordering = ('-data_aplicacao',)

    # Certifique-se que medicamento_aplicado está nos fields/fieldsets
    fieldsets = (
        (None, {
            'fields': ('animal', 'medicamento_aplicado', 'data_aplicacao', 'data_revacinacao')
        }),
    )

    def medicamento_aplicado_display(self, obj):
        """
        Exibe o nome do medicamento, lote e data de validade de forma amigável.
        """
        if obj.medicamento_aplicado:
            validade = obj.medicamento_aplicado.data_validade.strftime('%d/%m/%Y')
            return format_html(
                f"{obj.medicamento_aplicado.medicamento} (Lote: {obj.medicamento_aplicado.lote}) Val: {validade})"
            )
        return "N/A"
    medicamento_aplicado_display.short_description = "Medicamento Aplicado (Lote/Validade)"
    medicamento_aplicado_display.admin_order_field = 'medicamento_aplicado__medicamento' # Permite ordenar por nome do medicamento

    def status_revacinacao(self, obj):
        """
        Retorna uma tag HTML com uma cor indicando o status da data de revacinação.
        """
        if not obj.data_revacinacao:
            return format_html('<span style="color: gray;">Não definida</span>')

        hoje = timezone.now().date()
        dias_para_revacinar = (obj.data_revacinacao - hoje).days

        if dias_para_revacinar < 0:
            dias_atraso = abs(dias_para_revacinar)
            return format_html('<b style="color: red;">ATRASADA! ({} dias)</b>', dias_atraso)
        elif dias_para_revacinar <= 30:
            return format_html('<b style="color: orange;">Vence em {} dias</b>', dias_para_revacinar)
        else:
            return format_html('<span style="color: green;">OK (Em {} dias)</span>', dias_para_revacinar)

    status_revacinacao.short_description = "Status Revacinação"
    status_revacinacao.admin_order_field = 'data_revacinacao'


# --- Admin para RegistroVermifugos ---
@admin.register(RegistroVermifugos)
class RegistroVermifugosAdmin(admin.ModelAdmin):
    list_display = (
        'animal',
        'medicamento_administrado_display',
        'data_administracao',
        'data_readministracao',
        'status_readministracao',
    )
    search_fields = ('animal__nome', 'medicamento_administrado__medicamento', 'medicamento_administrado__lote')
    list_filter = ('data_administracao', 'data_readministracao', 'medicamento_administrado__medicamento')
    ordering = ('-data_administracao',)

    fieldsets = (
        (None, {
            'fields': ('animal', 'medicamento_administrado', 'data_administracao', 'data_readministracao')
        }),
    )

    def medicamento_administrado_display(self, obj):
        """
        Exibe o nome do medicamento (vermífugo), lote e data de validade de forma amigável.
        """
        if obj.medicamento_administrado:
            validade = obj.medicamento_administrado.data_validade.strftime('%d/%m/%Y')
            return format_html(
                f"{obj.medicamento_administrado.medicamento} (Lote: {obj.medicamento_administrado.lote}) Val: {validade})"
            )
        return "N/A"
    medicamento_administrado_display.short_description = "Vermífugo Administrado (Lote/Validade)"
    medicamento_administrado_display.admin_order_field = 'medicamento_administrado__medicamento'

    def status_readministracao(self, obj):
        """
        Retorna uma tag HTML com uma cor indicando o status da data de readministração.
        """
        if not obj.data_readministracao:
            return format_html('<span style="color: gray;">Não definida</span>')

        hoje = timezone.now().date()
        dias_para_readministrar = (obj.data_readministracao - hoje).days

        if dias_para_readministrar < 0:
            dias_atraso = abs(dias_para_readministrar)
            return format_html('<b style="color: red;">ATRASADA! ({} dias)</b>', dias_atraso)
        elif dias_para_readministrar <= 30:
            return format_html('<b style="color: orange;">Readministrar em {} dias</b>', dias_para_readministrar)
        else:
            return format_html('<span style="color: green;">OK (Em {} dias)</span>', dias_para_readministrar)

    status_readministracao.short_description = "Status Readministração"
    status_readministracao.admin_order_field = 'data_readministracao'


# --- Admin para EstoqueMedicamento ---
@admin.register(EstoqueMedicamento)
class EstoqueMedicamentoAdmin(admin.ModelAdmin):
    list_display = ('medicamento', 'lote', 'quantidade', 'data_validade', 'destaque_validade')
    search_fields = ('medicamento', 'lote')
    list_filter = ('data_validade',)
    ordering = ['medicamento']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['medicamento', 'lote', 'quantidade', 'data_validade', 'data_cadastro', 'destaque_validade']
        return ['quantidade', 'data_cadastro', 'destaque_validade']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

# --- Admin para MovimentoEstoqueMedicamento ---
class MovimentoEstoqueMedicamentoForm(forms.ModelForm):
    saldo_lote = forms.CharField(
        label="Status do Lote",
        required=False,
        disabled=True,
        initial="Informe o código do lote para verificar."
    )

    class Meta:
        model = MovimentoEstoqueMedicamento
        fields = '__all__'


@admin.register(MovimentoEstoqueMedicamento)
class MovimentoEstoqueMedicamentoAdmin(admin.ModelAdmin):
    form = MovimentoEstoqueMedicamentoForm
    list_display = ('data', 'tipo', 'medicamento', 'lote', 'quantidade')
    search_fields = ('medicamento', 'lote')
    list_filter = ('tipo', 'data')
    list_per_page = 25

    fieldsets = (
        (None, {
            'fields': (
                'medicamento',
                'lote',
                'data_validade',
                'tipo',
                'quantidade',
                'observacao',
            )
        }),
    )

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

