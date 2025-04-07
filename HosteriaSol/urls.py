from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("Galeria/", views.galeria, name="Galeria"),
    path("Nosotros/", views.nosotros, name="Nosotros"),
    path("Habitaciones/", views.habitaciones, name="Habitaciones"),
    path("contactar/", views.contactar, name="contactar"),
    path("administrador/", views.administrador, name="Administrador"),
    path('menu/', views.menu, name='menu'),
    path('logout/', views.logout, name='logout'),
    path("pago/<int:reserva_id>/", views.pago, name="pago"),
    path("terminos/", views.terminos, name="terminos"),
    
    #habitaciones
    path("habitacion/", views.habitacion, name="habitacion"),
    path("editar_habitacion/<int:id_habitacion>/", views.editar_habitacion, name="editar_habitacion"),
    path("agregar_habitacion/", views.agregar_habitacion, name="agregar_habitacion"),
    path("eliminar_habitacion/<int:id_habitacion>/",views.eliminar_habitacion, name="eliminar_habitacion"),

    #listar
    path("listar_habitaciones/", views.listar_habitaciones, name="listar_habitaciones"),
    path("listar_clientes/", views.listar_clientes, name="listar_clientes"),


    # clave
    path("cambiar_clave/", views.cambiar_clave, name="cambiar_clave"),
    path("Recuperar_clave/", views.Recuperar_clave, name="Recuperar_clave"),
    path("restablecer_contraseña/<str:correo>/", views.restablecer_contraseña, name="restablecer_contraseña"),


    # registros
    path("Register/", views.register, name="Register"),
    path("registros/", views.usuarios, name="Registros"),
    path("agregar_registro/", views.agregar_usuario, name="agregar_registro"),
    path("eliminar_usuario/<int:id_usuario>/",views.eliminar_usuario, name="eliminar_usuario"),
    path("editar_registro/<int:id_usuario>/", views.editar_registro, name="editar_registro"),
    path("usuarios/", views.usuarios, name="usuarios"),


    # CRUD reservas
    path("Reservas/", views.Reservas, name="Reservas"),
    path("agregar_reservas", views.agregar_reservas, name="agregar_reservas"),
    path("eliminar_reserva/<int:id_reserva>/",views.eliminar_reserva, name="eliminar_reserva"),
    path("editar_reserva/<int:id_reserva>/", views.editar_reserva, name="editar_reserva"),
]
