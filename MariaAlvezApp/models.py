from django.db import models, transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.html import format_html

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
    class Meta:
        verbose_name = "Exame"
        verbose_name_plural = "Exames"

# Classes de gestão
# MariaAlvezApp/models.py



class EstoqueMedicamento(models.Model):
    medicamento = models.CharField("Medicamento", max_length=255)
    lote = models.CharField("Lote", max_length=100)
    data_validade = models.DateField("Data de Validade")
    quantidade = models.PositiveIntegerField("Quantidade em Estoque", default=0, editable=False)
    data_cadastro = models.DateField("Data de Entrada", default=timezone.now, editable=False)

    class Meta:
        # Garante que não haja lotes duplicados para o mesmo medicamento.
        unique_together = ('lote',)
        verbose_name = 'Lote de Medicamento'
        verbose_name_plural = 'Estoque de Medicamentos'

    def __str__(self):
        validade = self.data_validade.strftime('%d/%m/%Y')
        return f"{self.medicamento} - Lote: {self.lote} (Val: {validade}) | {self.quantidade} un."

    def destaque_validade(self):
        """
        Retorna uma tag HTML com uma cor indicando o status da data de validade.
        Útil para visualização rápida no painel de administração.
        """
        if not self.data_validade:
            return format_html('<span style="color: gray;">Sem validade</span>')
        
        dias_para_vencer = (self.data_validade - timezone.now().date()).days
        
        if dias_para_vencer < 0:
            return format_html('<b style="color: red;">VENCIDO</b>')
        elif dias_para_vencer <= 30:
            return format_html('<b style="color: orange;">Vence em {} dias</b>', dias_para_vencer)
        else:
            return format_html('<span style="color: green;">OK</span>')
    
    destaque_validade.short_description = "Status da Validade"


class MovimentoEstoqueMedicamento(models.Model):
    ENTRADA = 'entrada'
    SAIDA = 'saida'
    TIPOS_MOVIMENTO = [
        (ENTRADA, 'Entrada'),
        (SAIDA, 'Saída'),
    ]

    medicamento = models.CharField("Medicamento", max_length=255)
    lote = models.CharField("Código do Lote", max_length=100)
    data_validade = models.DateField("Data de Validade")
    tipo = models.CharField("Tipo de Movimento", max_length=10, choices=TIPOS_MOVIMENTO)
    quantidade = models.PositiveIntegerField("Quantidade Movimentada")
    data = models.DateTimeField("Data do Movimento", auto_now_add=True)
    observacao = models.TextField("Observação", blank=True, null=True)

    class Meta:
        verbose_name = "Movimento de Estoque"
        verbose_name_plural = "Movimentos de Estoque"

    def __str__(self):
        return f"{self.get_tipo_display()} de {self.quantidade} un. de {self.medicamento} (Lote: {self.lote})"

    def clean(self):
        super().clean()

        # Verifica se a quantidade foi preenchida e é positiva
        if self.quantidade is not None and self.quantidade <= 0:
            raise ValidationError({'quantidade': "A quantidade movimentada deve ser maior que zero."})

        # Verifica se a data de validade está preenchida e é válida
        if self.data_validade and self.data_validade < timezone.now().date():
            raise ValidationError({'data_validade': "A data de validade não pode ser anterior a hoje."})

        # Validação específica para saída de estoque
        if self.tipo == self.SAIDA:
            if self.medicamento and self.lote:
                try:
                    estoque = EstoqueMedicamento.objects.get(
                        medicamento=self.medicamento,
                        lote=self.lote
                    )
                except EstoqueMedicamento.DoesNotExist:
                    raise ValidationError("Não é possível dar saída de um lote que não existe no estoque.")

                if self.quantidade is not None and estoque.quantidade < self.quantidade:
                    raise ValidationError(
                        f"Saldo insuficiente para este lote. Disponível: {estoque.quantidade}, Saída: {self.quantidade}."
                    )

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.tipo == self.ENTRADA:
                estoque, created = EstoqueMedicamento.objects.get_or_create(
                    medicamento=self.medicamento,
                    lote=self.lote,
                    defaults={'data_validade': self.data_validade, 'quantidade': self.quantidade}
                )
                if not created:
                    estoque.quantidade += self.quantidade
                    # Garante que a data de validade seja a mesma na entrada
                    estoque.data_validade = self.data_validade
                    estoque.save()
            
            elif self.tipo == self.SAIDA:
                # O método `clean` já validou a existência e o saldo do lote.
                estoque = EstoqueMedicamento.objects.get(medicamento=self.medicamento, lote=self.lote)
                estoque.quantidade -= self.quantidade
                estoque.save()
            
            # Salva o registro do movimento em si
            super().save(*args, **kwargs)