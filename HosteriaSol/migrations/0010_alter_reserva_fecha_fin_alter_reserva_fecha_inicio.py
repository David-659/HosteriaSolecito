# Generated by Django 5.1.6 on 2025-03-26 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HosteriaSol', '0009_alter_reserva_fecha_fin_alter_reserva_fecha_inicio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reserva',
            name='fecha_fin',
            field=models.DateField(blank=True, help_text='AAAA-MM-DD', null=True),
        ),
        migrations.AlterField(
            model_name='reserva',
            name='fecha_inicio',
            field=models.DateField(blank=True, help_text='AAAA-MM-DD', null=True),
        ),
    ]
