# Generated by Django 5.2.2 on 2025-06-09 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MariaAlvezApp', '0006_tutor_sobrenome_alter_tutor_nome'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutor',
            name='nome',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='tutor',
            name='sobrenome',
            field=models.CharField(max_length=100),
        ),
    ]
