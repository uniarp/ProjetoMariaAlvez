# Generated by Django 5.2.3 on 2025-06-12 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MariaAlvezApp', '0005_alter_animal_peso'),
    ]

    operations = [
        migrations.AlterField(
            model_name='animal',
            name='peso',
            field=models.DecimalField(decimal_places=3, default=0, help_text='Peso em quilogramas', max_digits=10),
        ),
    ]
