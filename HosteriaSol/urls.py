from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("Galeria/", views.galeria, name="Galeria"),
    path("Nosotros/", views.nosotros, name="Nosotros"),
    path("Servicio/", views.servicios, name="Servicios"),
    path("Habitaciones/", views.habitaciones, name="Habitaciones"),
    path("contactar/", views.contactar, name="contactar"),
    path("administrador/", views.administrador, name="Administrador"),
    path('menu/', views.menu, name='menu'),
    path('logout/', views.logout, name='logout'),
    path("pago/<int:reserva_id>/<int:id_habitacion>/<int:servicio_id>/", views.pago, name="pago"),
    path("pago/<int:reserva_id>/<int:id_habitacion>/", views.pago, name="pago_sin_servicio"),
    path("confirmar_pago/", views.confirmar_pago, name="confirmar_pago"),
    path("terminos/", views.terminos, name="terminos"),

    
    #habitaciones
    path("habitacion/", views.habitacion, name="habitacion"),
    path("editar_habitacion/<int:id_habitacion>/", views.editar_habitacion, name="editar_habitacion"),
    path("agregar_habitacion/", views.agregar_habitacion, name="agregar_habitacion"),
    path("eliminar_habitacion/<int:id_habitacion>/",views.eliminar_habitacion, name="eliminar_habitacion"),
    path("seleccion_habitacion/<int:id_habitacion>/<int:reserva_id>/",views.seleccion_habitacion, name="seleccion_habitacion"),
    path("seleccion_habitacion_servicio/<int:id_habitacion>/<int:reserva_id>/<int:servicio_id>/", views.seleccion_habitacion, name="seleccion_habitacion_servicio"),
    path("eliminar_seleccion/<int:id_habitacion>/<int:reserva_id>/",views.eliminar_seleccion, name="eliminar_seleccion"),
    path("eliminar_seleccion_servicio/<int:id_habitacion>/<int:reserva_id>/<int:servicio_id>/",views.eliminar_seleccion, name="eliminar_seleccion_servicio"),
    
    
    #listar
    path("listar_habitaciones/", views.listar_habitaciones, name="listar_habitaciones"),
    path("listar_clientes/", views.listar_clientes, name="listar_clientes"),
    path("listar_servicios/", views.listar_servicios, name="listar_servicios"),
    path("listar_empleados/", views.listar_empleados, name="listar_empleados"),


    #empleados
    path("empleados/", views.empleados, name="empleados"),
    path("agregar_empleados/", views.agregar_empleados, name="agregar_empleados"),
    path("editar_empleados/<int:id_empleado>/", views.editar_empleados, name="editar_empleados"),
    path("eliminar_empleados/<int:id_empleado>/",views.eliminar_empleados, name="eliminar_empleados"),
    path("empleados/<int:id_empleado>/", views.empleados, name="empleados_id"),
    path("empleados/<int:id_empleado>/<int:reserva_id>/", views.empleados, name="empleados_id_reserva"),

    #Servicios
    path("agregar_servicio/", views.agregar_servicio, name="agregar_servicio"),
    path("editar_servicio/<int:id_servicio>/", views.editar_servicio, name="editar_servicio"),
    path("eliminar_servicio/<int:id_servicio>/",views.eliminar_servicio, name="eliminar_servicio"),     

    # clave
    path("cambiar_clave/", views.cambiar_clave, name="cambiar_clave"),
    path("Recuperar_clave/", views.Recuperar_clave, name="Recuperar_clave"),
    path("restablecer_contraseña/<str:correo>/", views.restablecer_contraseña, name="restablecer_contraseña"),


    # registros
    path("Register/", views.Register, name="Register"),
    path("registros/", views.usuarios, name="Registros"),
    path("agregar_registro/", views.agregar_usuario, name="agregar_registro"),
    path("eliminar_usuario/<int:id_usuario>/",views.eliminar_usuario, name="eliminar_usuario"),
    path("editar_registro/<int:id_usuario>/", views.editar_registro, name="editar_registro"),
    path("usuarios/", views.usuarios, name="usuarios"),


    # CRUD reservas
    path("Reservas2/<int:reserva_id>/<int:servicio_id>/", views.Reservas2, name="Reservas2"),
    path('Reservas2/<int:reserva_id>/', views.Reservas2, name='Reservas2_sin_servicio'),
    path("agregar_reservas", views.agregar_reservas, name="agregar_reservas"),
    path("eliminar_reserva/<int:id_reserva>/",views.eliminar_reserva, name="eliminar_reserva"),
    path('editar_reserva/<int:id_reserva>/<int:id_habitacion>/', views.editar_reserva, name='editar_reserva_hab'),
    path('editar_reserva/<int:id_reserva>/', views.editar_reserva, name='editar_reserva'),
    path("cancelar_reserva/<int:id_reserva>/",views.cancelar_reserva, name="cancelar_reserva"),
    path("detalle/<int:reserva_id>/<int:id_habitacion>/<int:servicio_id>/", views.detalles, name="detalles"),
    path("detalle/<int:reserva_id>/<int:id_habitacion>/", views.detalles, name="detalles_sin_servicio"),
    
]

