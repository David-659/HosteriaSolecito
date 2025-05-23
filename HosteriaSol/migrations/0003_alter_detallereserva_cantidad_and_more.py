# Generated by Django 4.0.1 on 2025-03-13 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HosteriaSol', '0002_remove_detallereserva_precio_unitario_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detallereserva',
            name='cantidad',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='detalleservicio',
            name='cantidad',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='pago',
            name='hora',
            field=models.TimeField(null=True),
        ),
        migrations.AlterField(
            model_name='servicio',
            name='precio',
            field=models.FloatField(default=0, null=True),
        ),
    ]
