from django.db import models

# Classes principais
class Veterinario(models.Model):
    nome = models.CharField(
        verbose_name="Nome Completo",
        max_length=100
    )
    telefone = models.CharField(
        verbose_name="Telefone",
        max_length=20,
        help_text="Ex: (49) 99999-8888"
    )
    crmv = models.CharField(
        verbose_name="CRMV",
        max_length=20,
        unique=True,
        help_text="Número de registro no Conselho Regional de Medicina Veterinária."
    )

    class Meta:
        verbose_name = "Veterinário"
        verbose_name_plural = "Veterinários"

    def __str__(self):
        return f"{self.nome} (CRMV: {self.crmv})"

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