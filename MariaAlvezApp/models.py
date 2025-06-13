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
    class Meta:
        verbose_name = "Registro de Vacinacão"
        verbose_name_plural = "Registros de Vacinações"

class RegistroVermifugos(models.Model):
    class Meta:
        verbose_name = "Registro de Vermífugo"
        verbose_name_plural = "Registros de Vermífugos"

class Exames(models.Model):
    id_exame = models.BigAutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    tipo = models.CharField(max_length=50, choices=[
        ('Imagem', 'Imagem'),
        ('Laboratorial', 'Laboratorial'),
        ('Clínico', 'Clínico'),
    ])
    anexo = models.FileField(upload_to='exames/', blank=True, null=True)  # Os arquivos serão salvos em /media/exames/
    data_envio = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Exame"
        verbose_name_plural = "Exames"

    def __str__(self):
        return self.nome
    
# Classes de gestão
class Medicamentos(models.Model):
    class Meta:
        verbose_name = "Medicamento"
        verbose_name_plural = "Medicamentos"