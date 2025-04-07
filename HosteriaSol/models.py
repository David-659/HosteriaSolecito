from django.db import models

# Modelo de Usuario


class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=254)

    TIPOS_DOCUMENTO = (
        (1, "Cedula de Ciudadania"),
        (2, "Tarjeta de Identidad"),
        (3, "Cedula de Extranjeria"),
        (4, "Pasaporte"),
    )
    tipo_documento = models.IntegerField(choices=TIPOS_DOCUMENTO, default=1)
    documento = models.CharField(max_length=20)
    foto = models.ImageField(upload_to="usuarios", default="usuarios/default.png", max_length=254)
    telefono = models.IntegerField(null=True)
    direccion = models.CharField(max_length=254)
    ROLES = (
        (1, "Administrador"),
        (2, "Empleado"),
        (3, "Cliente"),
    )
    rol = models.IntegerField(choices=ROLES, default=3)

    def __str__(self):
        return f"{self.nombre} - {self.tipo_documento} ROL: {self.rol}"

# Modelo de Servicio


class Servicio(models.Model):
    nombre = models.CharField(max_length=254)
    precio = models.DecimalField(max_digits=1000, decimal_places=0, default=0)  # ← Agregar default=0
    descripcion = models.TextField(blank=False, null=False)
    hora_inicio = models.TimeField(help_text="HH:mm")
    hora_fin = models.TimeField(help_text="HH:mm")
    ESTADOS = (
        (1, "Activo"),
        (2, "Inactivo"),
    )
    estado = models.IntegerField(choices=ESTADOS, default=1)
    def __str__(self):
        txt = '{0} - {1} - {2}'
        return txt.format(self.nombre, self.precio, self.estado)


# Modelo de Reserva
class Reserva(models.Model):
    cliente = models.ForeignKey("Usuario", on_delete=models.CASCADE, related_name="fk04_idCliente", null=False, blank=False)
    empleado = models.ForeignKey('Empleado', on_delete=models.SET_NULL, null=True, blank=True, related_name="fk05_idEmpleado")
    pago = models.ForeignKey('Pago', on_delete=models.SET_NULL, null=True, blank=True, related_name="fk06_idPago", default=1)
    num_per = models.IntegerField(null=True, blank=True)
    fecha_inicio = models.DateField(help_text="AAAA-MM-DD", null=True, blank=True)
    fecha_fin = models.DateField(help_text="AAAA-MM-DD", null=True, blank=True)
    ESTADOS = (
        ("A", "ACTIVA"),
        ("I", "INACTIVA"),
        ("C", "CANCELADA"),
        ("P", "PAGADA"),
    )
    estado = models.CharField(max_length=1, choices=ESTADOS, default="A")
    def __str__(self):
        txt = '{0} - {1} - {2}'
        return txt.format(self.cliente, self.empleado, self.estado)


class Pago(models.Model):
    monto_total = models.DecimalField(max_digits=1000, decimal_places=0)
    fecha_pago = models.DateTimeField(null=False)
    METODOS =(
        (1,"EFECTIVO"),
        (2,"TRANSFERENCIA"),
        (3,"DATAFONO")
    )
    metodo_pago = models.IntegerField(choices=METODOS,default=1)

    def __str__(self):
        return f" {self.metodo_pago} - ${self.monto_total} ({self.fecha_pago})"


class Empleado(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    CARGOS = (
        ("Recepcionista", "RECEPCIONISTA"),
        ("Auxiliar_Aseo", "AUXILIAR_ASEO"),
        ("Tecnico_Mantenimiento", "TECNICO_MANTENIMIENTO"),
        ("Cocinero", "COCINERO"),
        ("Mesero", "MESERO"),
    )
    cargo = models.CharField(max_length=50, choices=CARGOS,default="Recepcionista")

    def __str__(self):
        return f"{self.nombre} {self.apellido}  {self.email} - {self.cargo}"


class Habitacion(models.Model):
    nombre = models.CharField(max_length=254)
    descripcion = models.TextField(null=True)
    capacidad = models.IntegerField()
    precio = models.FloatField(default=0)
    foto = models.ImageField(upload_to="habitaciones", default="habitaciones/default.png", max_length=254)
    ESTADOS = (
        ("D", "DISPONIBLE"),
        ("R", "RESERVADA"),
        ("L", "LIMPIEZA"),
    )
    estado = models.CharField(max_length=1, choices=ESTADOS, default="D")

    def __str__(self):
        return f"{self.nombre} - Capacidad: {self.capacidad} - Estado: {self.estado}"


class DetalleReserva(models.Model):
    habitacion = models.ForeignKey('Habitacion', on_delete=models.CASCADE, related_name="fk02_idHabitacion")
    reserva = models.ForeignKey('Reserva', on_delete=models.CASCADE, related_name="fk01_idReserva")
    cantidad = models.IntegerField(null=True)
    precio_neto = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return f"Reserva {self.reserva.id} - Habitación {self.habitacion.id} - Cantidad: {self.cantidad}"


class DetalleServicio(models.Model):
    servicio = models.ForeignKey('Servicio', on_delete=models.CASCADE, related_name="fk03_idServicio")
    detalle_reserva = models.ForeignKey('DetalleReserva', on_delete=models.DO_NOTHING, related_name="fk07_idDetalleReserva")
    cantidad = models.IntegerField(null=True)

    def __str__(self):
        return f"Servicio: {self.servicio} - Cantidad: {self.cantidad}"