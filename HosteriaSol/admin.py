from django.contrib import admin
from .models import Servicio, Reserva, Habitacion, DetalleReserva, Pago, Empleado, Usuario
from django.utils.html import mark_safe


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'rol', 'correo', 'documento', 'foto', 'ver_foto', 'telefono','password']
    search_fields = ['nombre', 'correo']
    list_filter = ['rol']
    list_editable = ['rol']

    def ver_foto(self, obj):
        return mark_safe(f"<img src='{obj.foto.url}' width='40%'>")

@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'descripcion', 'capacidad', 'precio', 'foto', 'ver_foto', 'estado']

    def ver_foto(self, obj):
        return mark_safe(f"<img src='{obj.foto.url}' width='40%'>")


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'precio', 'descripcion', 'hora_inicio', 'hora_fin', 'estado', 'ver_foto']

    def ver_foto(self, obj):
        return mark_safe(f"<img src='{obj.foto.url}' width='40%'>")
    ver_foto.short_description = "Imagen"


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'apellido', 'correo','password', 'cargo', 'foto', 'ver_foto']
    
    def ver_foto(self, obj):
        return mark_safe(f"<img src='{obj.foto.url}' width='40%'>")


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'empleado', 'pago', 'adultos','ninos' , 'fecha_inicio', 'fecha_fin', 'estado']


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ['id', 'monto_total', 'fecha_pago', 'metodo_pago']


@admin.register(DetalleReserva)
class DetalleReservaAdmin(admin.ModelAdmin):
    list_display = ['id', 'reserva', 'habitacion', 'cantidad', 'precio_neto']




