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
    activo = models.BooleanField(default=False)
    ROLES = (
        (1, "Administrador"),
        (2, "Cliente"),
        (3, "Empleado"),
    )
    rol = models.IntegerField(choices=ROLES, default=2)

    def __str__(self):
        return f"{self.nombre} - {self.tipo_documento} ROL: {self.rol}"
    
    class Meta:
        ordering = ['-id']     
      

# Modelo de Servicio


class Servicio(models.Model):
    nombre = models.CharField(max_length=254)
    precio = models.DecimalField(max_digits=1000, decimal_places=0, default=0)
    descripcion = models.TextField(blank=False, null=False)
    hora_inicio = models.TimeField(help_text="HH:mm")
    hora_fin = models.TimeField(help_text="HH:mm")
    foto = models.ImageField(upload_to="servicios/", default="servicios/default.png", max_length=254)
    ESTADOS = (
        ("A", "Activo"),
        ("I", "Inactivo"),
    )
    estado = models.CharField(max_length=1, choices=ESTADOS, default="A")

    def __str__(self):
        return f"{self.nombre} - {self.precio} - {self.estado}"

    class Meta:
        ordering = ['-id'] 

# Modelo de Reserva
class Reserva(models.Model):
    cliente = models.ForeignKey("Usuario", on_delete=models.CASCADE, related_name="fk04_idCliente", null=False, blank=False)
    empleado = models.ForeignKey('Empleado', on_delete=models.SET_NULL, null=True, blank=True, related_name="fk05_idEmpleado")
    pago = models.ForeignKey('Pago', on_delete=models.SET_NULL, null=True, blank=True, related_name="fk06_idPago")
    adultos = models.IntegerField(null=True, blank=True)
    ninos = models.IntegerField(null=True, blank=True,default=0)
    fecha_inicio = models.DateField(help_text="AAAA-MM-DD", null=True, blank=True)
    fecha_fin = models.DateField(help_text="AAAA-MM-DD", null=True, blank=True)
    
    ESTADOS = (
        ("A", "ACTIVA"),
        ("I", "INACTIVA"),
        ("C", "CANCELADA"),
        ("P", "PAGADA"),
        ("V", "VENCIDA"),
    )
    estado = models.CharField(max_length=1, choices=ESTADOS, default="A")
    
    def __str__(self):
        txt = '{0} - {1} - {2}'
        return txt.format(self.cliente, self.empleado, self.estado)

    class Meta:
        ordering = ['-id']  
   


class Pago(models.Model):
    monto_total = models.DecimalField(max_digits=1000, decimal_places=0)
    fecha_pago = models.DateTimeField(null=True)
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
    correo = models.EmailField(max_length=100)
    password = models.CharField(max_length=100, null=True, blank=True)
    foto = models.ImageField(upload_to="empleados", default="empleados/default.png", max_length=254)
    CARGOS = (
        ("Recepcionista", "RECEPCIONISTA"),
        ("Auxiliar_Aseo", "AUXILIAR_ASEO"),
        ("Tecnico_Mantenimiento", "TECNICO_MANTENIMIENTO"),
        ("Cocinero", "COCINERO"),
        ("Mesero", "MESERO"),
    )
    cargo = models.CharField(max_length=50, choices=CARGOS,default="Recepcionista")

    def __str__(self):
        return f"{self.nombre} {self.apellido}  {self.correo}  - {self.cargo}"
    
    class Meta:
        ordering = ['-id'] 


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
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion, 
            'precio': self.precio,
            'capacidad': self.capacidad,
            'estado': self.get_estado_display(),
            'foto': self.foto.url,
        }
    
    class Meta:
        ordering = ['-id'] 


class DetalleReserva(models.Model):
    habitacion = models.ForeignKey('Habitacion', on_delete=models.CASCADE, related_name="fk02_idHabitacion")
    reserva = models.ForeignKey('Reserva', on_delete=models.CASCADE, related_name="fk01_idReserva")
    cantidad = models.IntegerField(null=True)
    precio_neto = models.DecimalField(max_digits=10, decimal_places=0)
    servicio = models.ForeignKey('Servicio', on_delete=models.CASCADE, related_name="fk03_idServicio",null=True, blank=True)

    def __str__(self):
        return f"Reserva {self.reserva.id} - Habitación {self.habitacion.id} - Cantidad: {self.cantidad}"


