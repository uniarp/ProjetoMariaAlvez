from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.db import models


# Classes principais
class Veterinario(models.Model):
    class Meta:
        verbose_name = "Veterinário"
        verbose_name_plural = "Veterinários"

class Tutor(models.Model):
    class Meta:
        verbose_name = "Tutor"
        verbose_name_plural = "Tutores"

class Animal(models.Model):
    class Meta:
        verbose_name = "Animal"
        verbose_name_plural = "Animais"

class ConsultaClinica(models.Model):
    class Meta:
        verbose_name = "Consulta Clínica"
        verbose_name_plural = "Consultas Clínicas"

class AgendamentoConsultas(models.Model):
    class Meta:
        verbose_name = "Agendamento de Consulta"
        verbose_name_plural = "Agendamentos de Consultas"

# Classes de procedimentos"
class RegistroVacinacao(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, blank=True, null=True)
    medicamento = models.ForeignKey('Medicamentos', on_delete=models.CASCADE,  blank=True, null=True)
    data_aplicacao = models.DateField( blank=True, null=True)
    data_revacinacao = models.DateField(verbose_name="Data Revacinação", blank=True, null=True, )

    class Meta:
        verbose_name = "Registro de Vacinação"
        verbose_name_plural = "Registros de Vacinação"

    def clean(self):
        hoje = timezone.now().date()
        limite = hoje - timedelta(days=15)

        if self.data_aplicacao < limite:
            raise ValidationError({'data_aplicacao': 'A data de aplicação não pode ser anterior a 15 dias.'})

        if self.data_revacinacao and self.data_revacinacao < limite:
            raise ValidationError({'data_revacinacao': 'A data de revacinação não pode ser anterior a 15 dias.'})

    def __str__(self):
        return f" {self.data_aplicacao}"

class RegistroVermifugos(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, blank=True, null=True)
    medicamento = models.ForeignKey('Medicamentos', on_delete=models.CASCADE,  blank=True, null=True)
    data_administracao = models.DateField( blank=True, null=True)
    data_readministracao = models.DateField(verbose_name="Data Readministração", blank=True, null=True, )

    class Meta:
        verbose_name = "Registro de Vermífugo"
        verbose_name_plural = "Registros de Vermífugos"

    def clean(self):
        hoje = timezone.now().date()
        limite = hoje - timedelta(days=15)

        if self.data_administracao < limite:
            raise ValidationError({'data_administracao': 'A data de administração não pode ser anterior a 15 dias.'})

        if self.data_readministracao and self.data_readministracao < limite:
            raise ValidationError({'data_readministracao': 'A data de readministração não pode ser anterior a 15 dias.'})

    def __str__(self):
        return f" {self.data_administracao}"

class Exames(models.Model):
    class Meta:
        verbose_name = "Exame"
        verbose_name_plural = "Exames"

# Classes de gestão
class Medicamentos(models.Model):
    class Meta:
        verbose_name = "Medicamento"
        verbose_name_plural = "Medicamentos"