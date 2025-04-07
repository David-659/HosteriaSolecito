from django.contrib import admin
from .models import Servicio, Reserva, Habitacion, DetalleReserva, DetalleServicio, Pago, Empleado, Usuario
from django.utils.html import mark_safe

# Register your models here.
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display= ['id','nombre','rol','correo','documento','foto','ver_foto','telefono']
    search_fields = ['nombre','correo']
    list_filter = ['rol']
    list_editable = ['rol']

    def ver_foto(self, obj):
        return mark_safe(f"<img src='{obj.foto.url}' width='40%'>")

@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    list_display= ['id','nombre','descripcion','capacidad','precio','foto','ver_foto','estado']

    def ver_foto(self, obj):
        return mark_safe(f"<img src='{obj.foto.url}' width='40%'>")

admin.site.register(Servicio)
admin.site.register(Reserva)
admin.site.register(DetalleReserva)
admin.site.register(DetalleServicio)
admin.site.register(Pago)
admin.site.register(Empleado)

