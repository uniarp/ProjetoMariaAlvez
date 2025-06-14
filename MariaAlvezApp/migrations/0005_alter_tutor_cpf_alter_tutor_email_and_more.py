# Generated by Django 5.2.2 on 2025-06-09 13:07

import MariaAlvezApp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MariaAlvezApp', '0004_remove_tutor_estado_remove_tutor_sobrenome_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutor',
            name='cpf',
            field=models.CharField(max_length=14, unique=True, validators=[MariaAlvezApp.models.validar_cpf]),
        ),
        migrations.AlterField(
            model_name='tutor',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='tutor',
            name='endereco',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='tutor',
            name='telefone',
            field=models.CharField(max_length=15, validators=[MariaAlvezApp.models.validar_telefone]),
        ),
    ]
