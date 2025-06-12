from django.db import models
from django.utils import timezone
from django.utils.timezone import localtime
from django.core.exceptions import ValidationError

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
    data_consulta = models.DateTimeField(
        verbose_name="Data da Consulta",
        default=timezone.now,
        blank=False,
        null=False,
        
    )
    tutor = models.ForeignKey(
        'Tutor',
        on_delete=models.CASCADE,
        related_name='agendamentos',
        verbose_name="Tutor",
        blank=False,
        null=False,
        
    )
    animal = models.ForeignKey(
        'Animal',
        on_delete=models.CASCADE,
        related_name='agendamentos_consultas',
        verbose_name="Animal",
        blank=False,
        null=False,
        
    )
    def clean(self):
        super().clean()
        if self.data_consulta < timezone.now():
            raise ValidationError({'data_consulta': "A data da consulta não pode estar no passado."})
        if AgendamentoConsultas.objects.filter(animal=self.animal, data_consulta=self.data_consulta).exclude(pk=self.pk).exists():
            raise ValidationError({'data_consulta': "Já existe uma consulta agendada para este animal nesse horário."})

    class Meta:
        verbose_name = "Agendamento de Consulta"
        verbose_name_plural = "Agendamentos de Consultas"
        indexes = [models.Index(fields=['data_consulta'])]

    def __str__(self):
        if self.animal and self.tutor and self.data_consulta:
            data_local = localtime(self.data_consulta)
            return f"- {data_local.strftime('%d/%m/%Y %H:%M')}"
        return "Consulta sem dados completos"

    class Meta:
        verbose_name = "Agendamento de Consulta"
        verbose_name_plural = "Agendamentos de Consultas"

# Classes de procedimentos"
class RegistroVacinacao(models.Model):
    class Meta:
        verbose_name = "Registro de Vacinacão"
        verbose_name_plural = "Registros de Vacinações"

class RegistroVermifugos(models.Model):
    class Meta:
        verbose_name = "Registro de Vermífugo"
        verbose_name_plural = "Registros de Vermífugos"

class Exames(models.Model):
    class Meta:
        verbose_name = "Exame"
        verbose_name_plural = "Exames"

# Classes de gestão
class Medicamentos(models.Model):
    class Meta:
        verbose_name = "Medicamento"
        verbose_name_plural = "Medicamentos"