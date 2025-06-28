from django.db import models

class TesteTerceiro(models.Model):
    nome_teste = models.CharField(max_length=50, verbose_name="Nome Teste")

    class Meta:
        verbose_name = "Teste"
        verbose_name_plural = "Teste"

    def __str__(self):
        return self.nome_teste