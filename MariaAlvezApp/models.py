# MariaAlvezApp/models.py
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date, timedelta
import re

def validar_cpf(value):
    if not re.match(r'^\d{11}$', value):
        raise ValidationError('CPF inválido ou em formato incorreto.')

def validar_telefone(value):
    if not re.match(r'^\d{10,11}$', value):
        raise ValidationError('Telefone inválido ou em formato incorreto.')


# Classes principais

# Classe Veterinario (campos essenciais para ConsultaClinica)
class Veterinario(models.Model):
    nome = models.CharField(max_length=100, default="Nome Veterinário Padrão")
    telefone = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = "Veterinário"
        verbose_name_plural = "Veterinários"

    def __str__(self):
        return self.nome

# Classe Tutor (campos essenciais para ConsultaClinica)
class Tutor(models.Model):
    nome = models.CharField(max_length=100, default="Nome Tutor Padrão")

    class Meta:
        verbose_name = "Tutor"
        verbose_name_plural = "Tutores"

    def __str__(self):
        return self.nome

# Classe Animal (campos essenciais para sua ConsultaClinica)
class Animal(models.Model):
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='animais', null=True, blank=True, help_text="Tutor responsável pelo animal")
    nome = models.CharField(max_length=100, default="Nome Animal Padrão", help_text="Nome do animal")
    especie = models.CharField(max_length=50, default="Não Especificada", help_text="Espécie do animal (ex: Canina, Felina)")
    idade_anos = models.IntegerField(blank=True, null=True, help_text="Idade em anos")
    idade_meses = models.IntegerField(blank=True, null=True, help_text="Idade em meses")
    idade_dias = models.IntegerField(blank=True, null=True, help_text="Idade em dias")
    sexo = models.CharField(max_length=10, blank=True, null=True, help_text="Sexo do animal (ex: Macho, Fêmea)")
    peso = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Peso em quilogramas (Kg)")
    castrado = models.BooleanField(default=False, help_text="Indica se o animal é castrado")
    rfid = models.CharField(max_length=50, unique=True, blank=True, null=True, help_text="Número de identificação RFID (opcional)")

    class Meta:
        verbose_name = "Animal"
        verbose_name_plural = "Animais"

    def __str__(self):
        return f"{self.nome} ({self.especie}) - Tutor: {self.tutor.nome if self.tutor else 'N/A'}"

# Classe Exames (campos essenciais para ConsultaClinica)
class Exames(models.Model):
    nome = models.CharField(max_length=100, default="Exame Padrão")

    class Meta:
        verbose_name = "Exame"
        verbose_name_plural = "Exames"

    def __str__(self):
        return self.nome

# Classe Medicamentos (campos essenciais para ConsultaClinica)
class Medicamentos(models.Model):
    nome = models.CharField(max_length=100, default="Medicamento Padrão")

    class Meta:
        verbose_name = "Medicamento"
        verbose_name_plural = "Medicamentos"

    def __str__(self):
        return self.nome

# Modelo para Consulta Clínica
class ConsultaClinica(models.Model):
    data_atendimento = models.DateTimeField(default=timezone.now, help_text="Data e hora da consulta")
    tipo_atendimento = models.CharField(max_length=100, blank=True, null=True, help_text="Tipo de atendimento (ex: Rotina, Emergência)")
    vet_responsavel = models.ForeignKey(Veterinario, on_delete=models.SET_NULL, null=True, blank=True, related_name='consultas_clinicas', help_text="Veterinário responsável pela consulta")
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='consultas_clinicas', null=True, blank=True, help_text="Animal atendido na consulta")
    
    diagnostico = models.TextField(blank=True, null=True, help_text="Diagnóstico da consulta")
    observacoes = models.TextField(blank=True, null=True, help_text="Observações adicionais da consulta")
    
    frequencia_cardiaca = models.IntegerField(blank=True, null=True, help_text="Frequência cardíaca em batimentos por minuto (BPM)")
    frequencia_respiratoria = models.IntegerField(blank=True, null=True, help_text="Frequência respiratória em respirações por minuto (RPM)")
    
    temperatura = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True, help_text="Temperatura corporal em graus Celsius (°C)")
    peso = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Peso do animal em quilogramas (Kg)")
    
    avaliacao_mucosa = models.CharField(max_length=100, blank=True, null=True, help_text="Avaliação da mucosa (ex: Rósea, Pálida, Ictérica)")
    exames = models.ManyToManyField('Exames', blank=True, related_name='consultas_clinicas', help_text="Exames realizados durante ou após a consulta") 

    tempo_preenchimento_capilar = models.CharField(max_length=50, blank=True, null=True, help_text="Tempo de preenchimento capilar (ex: < 2 segundos, 3 segundos)")

    class Meta:
        verbose_name = "Consulta Clínica"
        verbose_name_plural = "Consultas Clínicas"
        ordering = ['-data_atendimento']

    def __str__(self):
        animal_nome = self.animal.nome if self.animal else 'N/A'
        return f"Consulta de {animal_nome} em {self.data_atendimento.strftime('%d/%m/%Y %H:%M')}"

    def clean(self):
        if not self.diagnostico:
            raise ValidationError({'diagnostico': 'O campo Diagnóstico não pode ser vazio.'})
        
        if not self.animal:
            raise ValidationError({'animal': 'É obrigatório selecionar um animal para a consulta.'})
        if not self.vet_responsavel:
            raise ValidationError({'vet_responsavel': 'É obrigatório selecionar um veterinário responsável.'})

        hoje = timezone.localdate()
        data_limite = hoje - timedelta(days=15)

        if self.data_atendimento and self.data_atendimento.date() < data_limite:
            raise ValidationError({'data_atendimento': 'A data da consulta não pode ser mais antiga que 15 dias.'})
        
        super().clean()


# Classes de procedimentos

# Classe AgendamentoConsultas (campos essenciais para ConsultaClinica)
class AgendamentoConsultas(models.Model):
    data_consulta = models.DateTimeField(default=timezone.now)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='agendamentos_tutor', null=True, blank=True)
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='agendamentos_animal', null=True, blank=True)

    class Meta:
        verbose_name = "Agendamento de Consulta"
        verbose_name_plural = "Agendamentos de Consultas"
        ordering = ['data_consulta']

    def __str__(self):
        animal_nome = self.animal.nome if self.animal else 'N/A'
        tutor_nome = self.tutor.nome if self.tutor else 'N/A'
        return f"Agendamento para {animal_nome} ({tutor_nome}) em {self.data_consulta.strftime('%d/%m/%Y %H:%M')}"


# Classe RegistroVacinacao (campos essenciais para ConsultaClinica)
class RegistroVacinacao(models.Model):
    class Meta:
        verbose_name = "Registro de Vacinação"
        verbose_name_plural = "Registros de Vacinações"

    def __str__(self):
        return f"Registro de Vacinação (placeholder)"

# Classe RegistroVermifugos (campos essenciais para ConsultaClinica)
class RegistroVermifugos(models.Model):
    class Meta:
        verbose_name = "Registro de Vermífugo"
        verbose_name_plural = "Registros de Vermífugos"

    def __str__(self):
        return f"Registro de Vermífugo (placeholder)"
