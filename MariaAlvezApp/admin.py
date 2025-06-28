# admin.py - Versão final com a solução simplificada

from django.contrib import admin
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.utils import timezone 
from django.utils.html import format_html
from django.utils import timezone 
from django import forms
import requests


from .models import (
    Veterinario, Tutor, Animal, ConsultaClinica,
    AgendamentoConsultas, RegistroVacinacao, RegistroVermifugos, 
    Exames, EstoqueMedicamento, MovimentoEstoqueMedicamento,
    RelatoriosGerais,
    MedicamentoConsulta 
)

# A CLASSE EstoqueStatusFilter FOI REMOVIDA

# Registros
admin.site.register(Veterinario)

class TutorAdminForm(forms.ModelForm):
    class Meta:
        model = Tutor
        fields = '__all__'

    def clean_cep(self):
        cep = self.cleaned_data.get('cep', '')
        cep = cep.replace('-', '').strip()

        if len(cep) != 8 or not cep.isdigit():
            raise forms.ValidationError("Digite um CEP válido com 8 números (ex: 89506538).")

        try:
            response = requests.get(f"https://viacep.com.br/ws/{cep}/json/", timeout=3)
            data = response.json()
        except requests.RequestException:
            raise forms.ValidationError("Erro ao consultar o CEP. Tente novamente.")

        if data.get("erro"):
            raise forms.ValidationError("CEP não encontrado.")

        self.cleaned_data['endereco'] = f"{data.get('logradouro', '')}, {data.get('bairro', '')}".strip(', ')
        self.cleaned_data['cidade'] = data.get('localidade', '')
        self.cleaned_data['estado'] = data.get('uf', '')

        return cep

class TutorAdmin(admin.ModelAdmin):
    form = TutorAdminForm

    class Media:
        js = ('js/cep_lookup.js',)
        css = {
            'all': ('admin/css/custom_admin.css',) # Adicione esta linha para carregar seu CSS
        }
admin.site.register(Tutor, TutorAdmin)

admin.site.register(Animal)
admin.site.register(AgendamentoConsultas)

@admin.register(RelatoriosGerais)
class RelatoriosGeraisAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        return super().changelist_view(request, extra_context=extra_context)
    change_list_template = "admin/relatorios_geral_changelist.html"
    def get_urls(self):
        urls = super().get_urls()
        return [path('', self.admin_site.admin_view(self.redirecionar_para_index_relatorios), name='relatorios_gerais_index')] + urls
    def redirecionar_para_index_relatorios(self, request):
        return HttpResponseRedirect(reverse('relatorios_index'))

# INLINES
class MedicamentoConsultaInline(admin.TabularInline):
    model = MedicamentoConsulta
    extra = 1 
    fields = ['medicamento_estoque', 'quantidade_aplicada']

class ExameInline(admin.TabularInline):
    model = Exames
    extra = 1
    fields = ('nome', 'tipo', 'anexo', 'descricao', 'data_exame')

# ModelAdmins
@admin.register(ConsultaClinica)
class ConsultaClinicaAdmin(admin.ModelAdmin):
    list_display = ('animal', 'data_atendimento', 'veterinario', 'tipo_atendimento', 'diagnostico', 'get_medicamentos_aplicados_display')
    search_fields = ('animal__nome', 'veterinario__nome', 'diagnostico') 
    fieldsets = (
        (None, {'fields': ('animal', 'veterinario', 'data_atendimento', 'tipo_atendimento', 'diagnostico', 'observacoes')}),
        ('Detalhes Físicos', {'fields': ('frequencia_cardiaca', 'frequencia_respiratoria', 'temperatura', 'peso', 'avaliacao_mucosa', 'tempo_preenchimento_capilar'), 'classes': ('collapse',)}),
    )
    inlines = [MedicamentoConsultaInline, ExameInline]
    @admin.display(description="Medicamentos na Consulta")
    def get_medicamentos_aplicados_display(self, obj):
        medicamentos_consulta = obj.medicamentoconsulta_set.all() 
        if medicamentos_consulta:
            return format_html("<br>".join([f"{mc.medicamento_estoque.medicamento} ({mc.quantidade_aplicada} un.)" for mc in medicamentos_consulta]))
        return "Nenhum"

# --- CLASSE ATUALIZADA COM A LÓGICA SIMPLES ---
@admin.register(EstoqueMedicamento)
class EstoqueMedicamentoAdmin(admin.ModelAdmin):
    list_display = ('medicamento', 'lote', 'quantidade', 'data_validade', 'destaque_validade')
    readonly_fields = ('data_cadastro',)

    def get_queryset(self, request):
        """
        Este método garante que a lista mostre APENAS os itens
        com quantidade maior que zero.
        """
        qs = super().get_queryset(request)
        return qs.filter(quantidade__gt=0)

@admin.register(MovimentoEstoqueMedicamento)
class MovimentoEstoqueMedicamentoAdmin(admin.ModelAdmin):
    list_display = ('estoque_item', 'tipo', 'quantidade', 'data', 'observacao')
    list_filter = ('tipo', 'data')
    search_fields = ('estoque_item__medicamento', 'estoque_item__lote', 'observacao') 
    def has_change_permission(self, request, obj=None): return False 
    def get_readonly_fields(self, request, obj=None):
        if obj is None: return ('data',)
        else: return ('estoque_item', 'tipo', 'quantidade', 'data', 'observacao')

@admin.register(RegistroVacinacao)
class RegistroVacinacaoAdmin(admin.ModelAdmin):
    list_display = ('animal', 'medicamento_aplicado_display', 'data_aplicacao', 'data_revacinacao', 'status_revacinacao_display')
    search_fields = ('animal__nome', 'medicamento_aplicado__medicamento', 'medicamento_aplicado__lote') 
    list_filter = ('data_aplicacao', 'data_revacinacao', 'medicamento_aplicado__medicamento') 
    ordering = ('-data_aplicacao',)
    fieldsets = ((None, {'fields': ('animal', 'medicamento_aplicado', 'data_aplicacao', 'data_revacinacao')}),)
    @admin.display(description="Medicamento Aplicado (Lote/Validade)")
    def medicamento_aplicado_display(self, obj):
        if obj.medicamento_aplicado:
            validade = obj.medicamento_aplicado.data_validade.strftime('%d/%m/%Y')
            return format_html(f"{obj.medicamento_aplicado.medicamento} (Lote: {obj.medicamento_aplicado.lote}) Val: {validade})")
        return "N/A"
    @admin.display(description="Status Revacinação", ordering='data_revacinacao')
    def status_revacinacao_display(self, obj):
        if not obj.data_revacinacao: return format_html('<span style="color: gray;">Não definida</span>')
        dias = (obj.data_revacinacao - timezone.now().date()).days
        if dias < 0: return format_html('<b style="color: red;">ATRASADA! ({} dias)</b>', abs(dias))
        elif dias <= 30: return format_html('<b style="color: orange;">Vence em {} dias</b>', dias)
        else: return format_html('<span style="color: green;">OK (Em {} dias)</span>', dias)

@admin.register(RegistroVermifugos)
class RegistroVermifugosAdmin(admin.ModelAdmin):
    list_display = ('animal', 'medicamento_administrado_display', 'data_administracao', 'data_readministracao', 'status_readministracao_display')
    search_fields = ('animal__nome', 'medicamento_administrado__medicamento', 'medicamento_administrado__lote') 
    list_filter = ('data_administracao', 'data_readministracao', 'medicamento_administrado__medicamento') 
    ordering = ('-data_administracao',)
    fieldsets = ((None, {'fields': ('animal', 'medicamento_administrado', 'data_administracao', 'data_readministracao')}),)
    @admin.display(description="Vermífugo Administrado (Lote/Validade)")
    def medicamento_administrado_display(self, obj):
        if obj.medicamento_administrado:
            validade = obj.medicamento_administrado.data_validade.strftime('%d/%m/%Y')
            return format_html(f"{obj.medicamento_administrado.medicamento} (Lote: {obj.medicamento_administrado.lote}) Val: {validade})")
        return "N/A"
    @admin.display(description="Status Readministração", ordering='data_readministracao')
    def status_readministracao_display(self, obj):
        if not obj.data_readministracao: return format_html('<span style="color: gray;">Não definida</span>')
        dias = (obj.data_readministracao - timezone.now().date()).days
        if dias < 0: return format_html('<b style="color: red;">ATRASADA! ({} dias)</b>', abs(dias))
        elif dias <= 30: return format_html('<b style="color: orange;">Readministrar em {} dias</b>', dias)
        else: return format_html('<span style="color: green;">OK (Em {} dias)</span>', dias)