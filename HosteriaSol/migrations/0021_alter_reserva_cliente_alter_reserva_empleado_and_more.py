# Generated by Django 5.1.6 on 2025-04-01 23:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HosteriaSol', '0020_usuario_foto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reserva',
            name='cliente',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fk04_idCliente', to='HosteriaSol.usuario'),
        ),
        migrations.AlterField(
            model_name='reserva',
            name='empleado',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fk05_idEmpleado', to='HosteriaSol.empleado'),
        ),
        migrations.AlterField(
            model_name='reserva',
            name='pago',
            field=models.ForeignKey(blank=True, default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fk06_idPago', to='HosteriaSol.pago'),
        ),
    ]
