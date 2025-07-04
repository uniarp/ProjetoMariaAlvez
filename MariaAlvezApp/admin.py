# MariaAlvezApp/admin.py

from django.contrib import admin
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.utils import timezone 
from django.utils.html import format_html
from django import forms
from datetime import datetime # Necessário para datetime e strftime
from django.db import models # Necessário para isinstance(db_field, models.DateField)
import requests # Necessário para clean_cep no TutorAdminForm

# Importe o NOVO formulário de agendamento (já estava aqui)
from .forms import AgendamentoConsultasForm 

# Importe todos os seus modelos
from .models import (
    Veterinario, Tutor, Animal, ConsultaClinica,
    AgendamentoConsultas, RegistroVacinacao, RegistroVermifugos, 
    Exames, EstoqueMedicamento, MovimentoEstoqueMedicamento,
    RelatoriosGerais,
    MedicamentoConsulta 
)

# Registra o Veterinário (já estava aqui)
admin.site.register(Veterinario)

# --- CLASSE TUTORADMINFORM ATUALIZADA ---
class TutorAdminForm(forms.ModelForm):
    class Meta:
        model = Tutor
        fields = '__all__' # Inclui todos os campos do modelo Tutor
        # O widget para data_nascimento será definido na TutorAdmin.formfield_for_dbfield
        # para maior controle e para evitar conflitos. Remova-o daqui.
        # widgets = {
        #     'data_nascimento': forms.DateInput(attrs={'type': 'date'})
        # }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Se estamos editando uma instância existente e ela tem data_nascimento
        if self.instance.pk and self.instance.data_nascimento:
            # DEBUG: Imprime o valor original e o que será atribuído
            print(f"DEBUG FORM TUTOR: Instância data_nascimento (original): {self.instance.data_nascimento}")
            
            # --- LINHA CRUCIAL: Formata a data para YYYY-MM-DD para o input type="date" ---
            # O .date() é importante porque self.instance.data_nascimento já é um objeto date (models.DateField)
            # Então, usamos strftime diretamente no objeto date.
            self.fields['data_nascimento'].widget.attrs['value'] = self.instance.data_nascimento.strftime('%Y-%m-%d')
            print(f"DEBUG FORM TUTOR: Set data_nascimento value to: {self.fields['data_nascimento'].widget.attrs['value']}")
        else:
            # Opcional: Para novos formulários, pré-preencher com a data atual como um valor inicial
            # Remova esta parte se não quiser que novos tutores tenham a data atual preenchida.
            self.fields['data_nascimento'].initial = timezone.now().date()
            print(f"DEBUG FORM TUTOR: Novo formulário, data_nascimento initial set to: {self.fields['data_nascimento'].initial}")

    def clean_cep(self):
        cep = self.cleaned_data.get('cep', '')
        cep = cep.replace('-', '').strip()

        if len(cep) != 8 or not cep.isdigit():
            raise forms.ValidationError("Digite um CEP válido com 8 números (ex: 89506538).")

        url = f"https://viacep.com.br/ws/{cep}/json/"
        try:
            response = requests.get(url, timeout=3)
            response.raise_for_status() # Levanta um erro para status de resposta HTTP ruins
            data = response.json()
        except requests.RequestException as e:
            raise forms.ValidationError(f"Erro ao consultar o CEP: {e}. Tente novamente.")
        except ValueError: # Para erros de JSON, se a resposta não for JSON válida
            raise forms.ValidationError("Resposta inválida da API de CEP.")

        if data.get("erro"):
            raise forms.ValidationError("CEP não encontrado.")

        # Estes campos são preenchidos no clean() do MODELO Tutor.
        # Aqui no form, apenas garantimos que os dados estão no cleaned_data.
        # O modelo Tutor, em seu método clean(), usará esses dados para buscar e preencher.
        self.cleaned_data['endereco'] = f"{data.get('logradouro', '')}, {data.get('bairro', '')}".strip(', ')
        self.cleaned_data['cidade'] = data.get('localidade', '')
        self.cleaned_data['estado'] = data.get('uf', '')

        return cep

# --- CLASSE TUTORADMIN ATUALIZADA ---
@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    form = TutorAdminForm # Usa o formulário personalizado

    list_display = ('nome', 'cpf', 'telefone', 'data_nascimento', 'cidade') # Exemplo de list_display
    search_fields = ('nome', 'cpf', 'telefone', 'cidade', 'estado')
    list_filter = ('cidade', 'estado')

    class Media:
        js = ('js/cep_lookup.js',) # Assumindo que este é o caminho correto para seu JS de CEP
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
    
    # --- MÉTODO CRUCIAL PARA FORÇAR O WIDGET type="date" E EVITAR INJEÇÃO JS DO ADMIN ---
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        # Verifica se o campo é o data_nascimento do modelo Tutor
        if db_field.name == 'data_nascimento' and isinstance(db_field, models.DateField):
            # Define o widget como forms.DateInput com type='date'.
            # Isso impede que o Django Admin ou Jazzmin injetem seus próprios pickers JS.
            kwargs['widget'] = forms.DateInput(attrs={'type': 'date'})
        return super().formfield_for_dbfield(db_field, request, **kwargs)


# Registra o Animal (já estava aqui)
@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('nome', 'especie')
    search_fields = ['nome', 'especie']

# Registra AgendamentoConsultas (já estava aqui)
@admin.register(AgendamentoConsultas)
class AgendamentoConsultasAdmin(admin.ModelAdmin):
    # Usa o formulário personalizado aqui
    form = AgendamentoConsultasForm 
    list_display = ('animal', 'get_tutor_display', 'data_consulta', 'consulta_associada_link')
    list_filter = ('data_consulta', 'animal__tutor', 'animal')
    search_fields = ('animal__nome', 'animal__tutor__nome')
    date_hierarchy = 'data_consulta'

    @admin.display(description="Tutor")
    def get_tutor_display(self, obj):
        return obj.animal.tutor.nome if obj.animal and obj.animal.tutor else "N/A"
    get_tutor_display.admin_order_field = 'animal__tutor__nome' 

    @admin.display(description="Consulta Associada")
    def consulta_associada_link(self, obj):
        if hasattr(obj, 'consulta_gerada') and obj.consulta_gerada is not None:
            url = reverse('admin:%s_%s_change' % (obj.consulta_gerada._meta.app_label, obj.consulta_gerada._meta.model_name), args=[obj.consulta_gerada.pk])
            return format_html('<a href="{}">Ver Consulta</a>', url)
        return format_html('<span style="color: gray;">Não gerada</span>')
    consulta_associada_link.allow_tags = True

# Registra RelatoriosGerais (já estava aqui)
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

# Inlines (já estavam aqui)
class MedicamentoConsultaInline(admin.TabularInline):
    model = MedicamentoConsulta
    extra = 0
    fields = ['medicamento_estoque', 'quantidade_aplicada']

class ExameInline(admin.TabularInline):
    model = Exames
    extra = 0
    fields = ('nome', 'tipo', 'anexo', 'descricao', 'data_exame')

# Registra ConsultaClinica (já estava aqui)
@admin.register(ConsultaClinica)
class ConsultaClinicaAdmin(admin.ModelAdmin):
    list_display = ('animal', 'data_atendimento', 'veterinario', 'tipo_atendimento', 'diagnostico', 'get_medicamentos_aplicados_display', 'agendamento_origem_display')
    search_fields = ('animal__nome', 'veterinario__nome', 'diagnostico') 
    fieldsets = (
        ("Geral", {'fields': ('animal', 'veterinario', 'data_atendimento', 'tipo_atendimento', 'agendamento_origem', 'diagnostico', 'observacoes')}),
        ('Detalhes Físicos', {'fields': ('frequencia_cardiaca', 'frequencia_respiratoria', 'temperatura', 'peso', 'avaliacao_mucosa', 'tempo_preenchimento_capilar'), 'classes': ('collapse',)}),
    )
    inlines = [MedicamentoConsultaInline, ExameInline]
    
    date_hierarchy = 'data_atendimento'

    @admin.display(description="Medicamentos na Consulta")
    def get_medicamentos_aplicados_display(self, obj):
        medicamentos_consulta = obj.medicamentoconsulta_set.all() 
        if medicamentos_consulta:
            return format_html("<br>".join([f"{mc.medicamento_estoque.medicamento} ({mc.quantidade_aplicada} un.)" for mc in medicamentos_consulta]))
        return "Nenhum"

    @admin.display(description="Agendamento de Origem")
    def agendamento_origem_display(self, obj):
        if obj.agendamento_origem:
            return f"ID: {obj.agendamento_origem.pk} ({obj.agendamento_origem.data_consulta.strftime('%d/%m/%Y %H:%M')})"
        return "N/A"
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.agendamento_origem:
            return self.readonly_fields + ('agendamento_origem', 'animal', 'data_atendimento')
        return self.readonly_fields

# Registra EstoqueMedicamento (já estava aqui)
@admin.register(EstoqueMedicamento)
class EstoqueMedicamentoAdmin(admin.ModelAdmin):
    list_display = ('medicamento', 'lote', 'quantidade', 'data_validade_formatada', 'destaque_validade')
    readonly_fields = ('data_cadastro',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(quantidade__gt=0)
    
    def data_validade_formatada(self, obj):
        return obj.data_validade.strftime('%d/%m/%Y')
    data_validade_formatada.short_description = 'Validade'

# Registra MovimentoEstoqueMedicamento (já estava aqui)
@admin.register(MovimentoEstoqueMedicamento)
class MovimentoEstoqueMedicamentoAdmin(admin.ModelAdmin):
    list_display = ('estoque_item', 'tipo', 'quantidade', 'data', 'observacao')
    list_filter = ('tipo', 'data')
    search_fields = ('estoque_item__medicamento', 'estoque_item__lote', 'observacao') 
    
    def has_change_permission(self, request, obj=None): return False 
    def get_readonly_fields(self, request, obj=None):
        if obj is None: return ('data',)
        else: return ('estoque_item', 'tipo', 'quantidade', 'data', 'observacao')

# Registra RegistroVacinacao (já estava aqui)
@admin.register(RegistroVacinacao)
class RegistroVacinacaoAdmin(admin.ModelAdmin):
    list_display = ('animal', 'medicamento_aplicado_display', 'data_aplicacao', 'data_revacinacao', 'status_revacacao_display')
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
    def status_revacacao_display(self, obj):
        if not obj.data_revacinacao: return format_html('<span style="color: gray;">Não definida</span>')
        dias = (obj.data_revacinacao - timezone.now().date()).days
        if dias < 0: return format_html('<b style="color: red;">ATRASADA! ({} dias)</b>', abs(dias))
        elif dias <= 30: return format_html('<b style="color: orange;">Vence em {} dias</b>', dias)
        else: return format_html('<span style="color: green;">OK (Em {} dias)</b>', dias)

# Registra RegistroVermifugos (já estava aqui)
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
        else: return format_html('<span style="color: green;">OK (Em {} dias)</b>', dias)