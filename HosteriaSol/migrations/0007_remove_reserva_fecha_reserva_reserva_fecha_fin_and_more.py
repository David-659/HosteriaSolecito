# Generated by Django 5.1.6 on 2025-03-26 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HosteriaSol', '0006_alter_usuario_tipo_documento'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reserva',
            name='fecha_reserva',
        ),
        migrations.AddField(
            model_name='reserva',
            name='fecha_fin',
            field=models.DateTimeField(blank=True, help_text='AAAA-MM-DD HH:mm', null=True),
        ),
        migrations.AddField(
            model_name='reserva',
            name='fecha_inicio',
            field=models.DateTimeField(blank=True, help_text='AAAA-MM-DD HH:mm', null=True),
        ),
    ]
