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
        required=True
    )

    HORA_CHOICES = []
    # Lógica para popular HORA_CHOICES (horas de 08:00 a 18:00, a cada 15 minutos)
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
    )

    class Meta:
        model = AgendamentoConsultas
        fields = ['animal', 'data_consulta_date', 'hora_consulta', 'is_castracao']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        print(f"DEBUG FORM: Inicializando formulário para instance.pk: {self.instance.pk}")

        # Se estamos editando uma instância existente E ela tem data_consulta
        if self.instance.pk and self.instance.data_consulta:
            # --- AQUI ESTÁ A MUDANÇA CRUCIAL: USAR timezone.localtime() ---
            # Converte o datetime salvo (em UTC) para o fuso horário local do TIME_ZONE
            local_data_consulta = timezone.localtime(self.instance.data_consulta)
            print(f"DEBUG FORM: Instância data_consulta (original): {self.instance.data_consulta}")
            print(f"DEBUG FORM: Instância data_consulta (local): {local_data_consulta}")

            # Define o valor para o campo de data, formatando para 'YYYY-MM-DD'
            self.fields['data_consulta_date'].widget.attrs['value'] = local_data_consulta.strftime('%Y-%m-%d')
            print(f"DEBUG FORM: Set data_consulta_date value to: {self.fields['data_consulta_date'].widget.attrs['value']}")
            
            # Define o valor inicial para o campo de hora (ChoiceField)
            self.fields['hora_consulta'].initial = local_data_consulta.strftime("%H:%M")
            print(f"DEBUG FORM: Set hora_consulta initial to: {self.fields['hora_consulta'].initial}")

        else: # Se é um novo agendamento
            # Preenche a data com a data atual (padrão para novos formulários)
            self.fields['data_consulta_date'].initial = timezone.now().date()
            
            # Preenche a hora com a hora mais próxima das opções de HORA_CHOICES, considerando o tempo local atual
            now_local_time = timezone.localtime(timezone.now()).time() # Pega a hora local atual
            
            closest_time = self.HORA_CHOICES[0][0] # Default para a primeira opção (08:00)
            for choice_value, _ in self.HORA_CHOICES:
                choice_time = datetime.strptime(choice_value, "%H:%M").time()
                # Encontra a primeira hora de escolha que seja igual ou maior que a hora atual local
                if choice_time >= now_local_time:
                    closest_time = choice_value
                    break
            self.fields['hora_consulta'].initial = closest_time
            
    def clean(self):
        cleaned_data = super().clean()
        data_consulta_date = cleaned_data.get('data_consulta_date')
        hora_consulta_str = cleaned_data.get('hora_consulta')
        animal = cleaned_data.get('animal')

        # Combine date and time to form data_consulta
        combined_datetime = None
        
        # Validar se os campos não estão vazios antes de tentar combinar
        if not data_consulta_date:
            self.add_error('data_consulta_date', "Este campo é obrigatório.")
        if not hora_consulta_str:
            self.add_error('hora_consulta', "Este campo é obrigatório.")

        # Se houver erros no formulário até aqui (e não ValidationError geral), retorne.
        if self.errors:
            return cleaned_data
            
        try:
            hora_consulta_obj = datetime.strptime(hora_consulta_str, "%H:%M").time()
            combined_datetime = datetime.combine(data_consulta_date, hora_consulta_obj)
            # Torna a datetime aware (importante para DateTimeField)
            # make_aware() com o timezone padrão do projeto é a forma correta de salvar no DB
            combined_datetime = timezone.make_aware(combined_datetime, timezone.get_current_timezone())
        except ValueError:
            self.add_error('hora_consulta', "Formato de hora inválido.")
            return cleaned_data
        
        # Validações que dependem de combined_datetime
        if combined_datetime:
            # A data da consulta não pode estar no passado
            # Importante: compare o combined_datetime (aware) com timezone.now() (aware)
            if combined_datetime < timezone.now():
                self.add_error('data_consulta_date', "A data da consulta não pode estar no passado.")
            
            # Validação de agendamentos duplicados para o mesmo animal no mesmo horário
            if animal:
                # Remove segundos e microssegundos para a comparação (para coincidir com a precisão do ChoiceField)
                data_hora_comparacao = combined_datetime.replace(second=0, microsecond=0)
                
                qs = AgendamentoConsultas.objects.filter(
                    animal=animal,
                    data_consulta=data_hora_comparacao
                )
                if self.instance.pk: # Se estiver editando, exclui a própria instância da checagem
                    qs = qs.exclude(pk=self.instance.pk)
                
                if qs.exists():
                    self.add_error('hora_consulta', "Já existe uma consulta agendada para este animal nesse horário.")

        # Atribui combined_datetime a cleaned_data['data_consulta']
        # Isso garante que o valor combinado seja passado para o save() do ModelForm
        cleaned_data['data_consulta'] = combined_datetime 
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        # ATENÇÃO: LINHA CRUCIAL! Garante que a data_consulta da instância do modelo seja definida
        # com o valor combinado antes de ser salvo no banco de dados.
        instance.data_consulta = self.cleaned_data['data_consulta'] 

        if commit:
            instance.save()
        return instance
    
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