from django import forms
from .models import Tutor, Animal, EstoqueMedicamento
from django.utils import timezone

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