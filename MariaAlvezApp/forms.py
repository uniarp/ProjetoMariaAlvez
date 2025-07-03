from django import forms
from .models import Tutor, Animal, EstoqueMedicamento, AgendamentoConsultas
from Terceiros.models import EmpresaTerceirizada, RegistroServico #
from django.utils import timezone
from datetime import time, datetime, timedelta

class FiltroConsultaForm(forms.Form):
    data_inicio = forms.DateField(label="De", required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    data_fim = forms.DateField(label="Até", required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    tutor = forms.ModelChoiceField(queryset=Tutor.objects.all(), required=False, label="Tutor")
    animal = forms.ModelChoiceField(queryset=Animal.objects.all(), required=False, label="Animal")

class FiltroEstoqueForm(forms.Form):
    medicamento = forms.CharField(label="Nome do Medicamento", required=False, max_length=255)
    lote = forms.CharField(label="Lote", required=False, max_length=100)
    data_validade_inicio = forms.DateField(label="Validade De", required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    data_validade_fim = forms.DateField(label="Validade Até", required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    STATUS_CHOICES = [
        ('', 'Todos'),
        ('com_estoque', 'Com Estoque (> 0)'),
        ('sem_estoque', 'Sem Estoque (0)'),
        ('vencidos', 'Vencidos'),
        ('vencendo', 'Vencendo (Próximos 30 dias)'),
    ]
    status_estoque = forms.ChoiceField(choices=STATUS_CHOICES, required=False, label="Status do Estoque")

class FiltroVacinacaoForm(forms.Form):
    animal = forms.ModelChoiceField(queryset=Animal.objects.all(), required=False, label="Animal")
    data_aplicacao_inicio = forms.DateField(label="Aplicação De", required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    data_aplicacao_fim = forms.DateField(label="Aplicação Até", required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    STATUS_REVACINACAO_CHOICES = [
        ('', 'Todos'),
        ('ok', 'Revacinação OK'),
        ('vencendo', 'Revacinação Vencendo (Próximos 30 dias)'),
        ('atrasada', 'Revacinação Atrasada'),
        ('nao_definida', 'Não Definida'),
    ]
    status_revacinacao = forms.ChoiceField(choices=STATUS_REVACINACAO_CHOICES, required=False, label="Status Revacinação")
    medicamento = forms.ModelChoiceField(
        queryset=EstoqueMedicamento.objects.all(),
        required=False,
        label="Medicamento/Lote"
    )

class FiltroVermifugosForm(forms.Form):
    animal = forms.ModelChoiceField(queryset=Animal.objects.all(), required=False, label="Animal")
    data_administracao_inicio = forms.DateField(label="Administração De", required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    data_administracao_fim = forms.DateField(label="Administração Até", required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    STATUS_READMIN_CHOICES = [
        ('', 'Todos'),
        ('ok', 'Readministração OK'),
        ('vencendo', 'Readministração Vencendo (Próximos 30 dias)'),
        ('atrasada', 'Readministração Atrasada'),
        ('nao_definida', 'Não Definida'),
    ]
    status_readministracao = forms.ChoiceField(choices=STATUS_READMIN_CHOICES, required=False, label="Status Readministração")
    medicamento = forms.ModelChoiceField(
        queryset=EstoqueMedicamento.objects.all(),
        required=False,
        label="Medicamento/Lote"
    )

class EstoqueMedicamentoForm(forms.ModelForm):
    class Meta:
        model = EstoqueMedicamento
        fields = '__all__'

    def clean_lote(self):
        lote = self.cleaned_data['lote']
        qs = EstoqueMedicamento.objects.filter(lote=lote)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Este lote já está cadastrado para outro medicamento.")
        return lote

class AgendamentoConsultasForm(forms.ModelForm):
    data_consulta_date = forms.DateField(
        label="Data da Consulta",
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date(),
        required=True
    )

    HORA_CHOICES = []
    start_time = datetime.strptime("08:00", "%H:%M").time()
    end_time = datetime.strptime("18:00", "%H:%M").time() 
    current_time = start_time

    while current_time <= end_time:
        HORA_CHOICES.append((current_time.strftime("%H:%M"), current_time.strftime("%H:%M")))
        current_datetime = datetime.combine(datetime.min, current_time) + timedelta(minutes=15)
        current_time = current_datetime.time()

    hora_consulta = forms.ChoiceField(
        label="Hora da Consulta",
        choices=HORA_CHOICES,
        required=True,
        initial=timezone.now().strftime("%H:%M") if start_time <= timezone.now().time() <= end_time else HORA_CHOICES[0][0]
    )

    class Meta:
        model = AgendamentoConsultas
        fields = ['animal', 'data_consulta_date', 'hora_consulta', 'is_castracao']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['data_consulta_date'].initial = self.instance.data_consulta.date()
            self.fields['hora_consulta'].initial = self.instance.data_consulta.time().strftime("%H:%M")
        else:
            self.fields['animal'].initial = None

    def clean(self):
        cleaned_data = super().clean()
        data_consulta_date = cleaned_data.get('data_consulta_date')
        hora_consulta_str = cleaned_data.get('hora_consulta')
        animal = cleaned_data.get('animal')

        combined_datetime = None 
        errors = {} 

        if not data_consulta_date:
            errors['data_consulta_date'] = "Este campo é obrigatório."
        if not hora_consulta_str:
            errors['hora_consulta'] = "Este campo é obrigatório."

        if data_consulta_date and hora_consulta_str:
            try:
                hora_consulta_obj = datetime.strptime(hora_consulta_str, "%H:%M").time()
                combined_datetime = datetime.combine(data_consulta_date, hora_consulta_obj)
                combined_datetime = timezone.make_aware(combined_datetime, timezone.get_current_timezone())
                # Aqui definimos o combined_datetime, mas ainda não o atribuímos a cleaned_data['data_consulta']
                # explicitamente para que o ModelForm não tente validar isso antes do tempo.
            except ValueError:
                errors['hora_consulta'] = "Formato de hora inválido."
        
        if errors:
            for field, msg in errors.items():
                self.add_error(field, msg)
            raise forms.ValidationError("Corrija os erros do formulário.") 

        # Validações que dependem de combined_datetime
        if combined_datetime:
            if combined_datetime < timezone.now():
                self.add_error('data_consulta_date', "A data da consulta não pode estar no passado.")
            
            if animal:
                data_hora_comparacao = combined_datetime.replace(second=0, microsecond=0)
                qs = AgendamentoConsultas.objects.filter(
                    animal=animal,
                    data_consulta=data_hora_comparacao
                )
                if self.instance.pk:
                    qs = qs.exclude(pk=self.instance.pk)
                
                if qs.exists():
                    self.add_error('hora_consulta', "Já existe uma consulta agendada para este animal nesse horário.")

        # FINALMENTE, atribui combined_datetime a cleaned_data['data_consulta'] aqui
        # para que o método save() do ModelForm possa acessar o valor correto.
        cleaned_data['data_consulta'] = combined_datetime 
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        # ATENÇÃO: LINHA CRUCIAL ADICIONADA/CORRIGIDA AQUI!
        # Garante que a data_consulta da instância do modelo seja definida com o valor combinado
        # ANTES de ser salvo no banco de dados.
        instance.data_consulta = self.cleaned_data['data_consulta'] 

        if commit:
            instance.save()
        return instance

# NOVO FORMULÁRIO PARA FILTRO DE REGISTRO DE SERVIÇO
class FiltroRegistroServicoForm(forms.Form):
    animal = forms.ModelChoiceField(queryset=Animal.objects.all(), required=False, label="Animal Atendido")
    empresa = forms.ModelChoiceField(queryset=EmpresaTerceirizada.objects.all(), required=False, label="Empresa Prestadora")
    data_inicio = forms.DateField(label="Data Início", required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    data_fim = forms.DateField(label="Data Fim", required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    busca_texto = forms.CharField(label="Buscar em Descrição/Medicamentos", required=False, max_length=255)

class FiltroFilaCastracaoForm(forms.Form):
    animal = forms.ModelChoiceField(queryset=Animal.objects.all(), required=False, label="Animal")
    tutor = forms.ModelChoiceField(queryset=Tutor.objects.all(), required=False, label="Tutor")
    data_inicio = forms.DateField(label="Agendamento De", required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    data_fim = forms.DateField(label="Agendamento Até", required=False, widget=forms.DateInput(attrs={'type': 'date'}))