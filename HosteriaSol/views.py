from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect,  get_object_or_404
from .models import Usuario, Reserva, Empleado, Pago, Habitacion,DetalleReserva

from django.db.utils import IntegrityError
from django.contrib import messages

from decimal import Decimal
from django.core.mail import send_mail
from django.conf import settings
import random
from .utils import *


def index(request):
    return render(request, 'index.html')


def login(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        contrasena = request.POST.get('contrasena')
        try:
            q = Usuario.objects.get(correo=usuario)
            if verify_password(contrasena, q.password):
                request.session["auth"] = {
                    "id": q.id,
                    "nombre": q.nombre,
                    "correo": q.correo,
                    "foto": q.foto.url,
                    "rol": q.get_rol_display(),
                }
                return redirect("index")
            else:
                raise Usuario.DoesNotExist()
        except Usuario.DoesNotExist:
            messages.warning(request, "Usuario o contraseña no válidos..")
            request.session["auth"] = None
        except Exception as e:
            messages.error(request, f"Error: {e}")
            request.session["auth"] = None
        return redirect("login")
    else:
        verificar = request.session.get("auth", False)
        if verificar:
            return redirect("index")
        else:
            return render(request, "login.html")


def logout(request):
    try:
        del request.session["auth"]
        return redirect("login")
    except:
        messages.info(request, "No se pudo cerrar sesión, intente de nuevo")
        return redirect("index")


def galeria(request):
    return render(request, 'Galeria.html')


def nosotros(request):
    return render(request, 'Nosotros.html')


def habitaciones(request):
    q = Habitacion.objects.all()
    contexto = {
        "datos": q
    }
    return render(request, 'Habitaciones.html',contexto)

def pago(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    if request.method == "POST":
        monto_total = request.POST.get("monto_total")
        fecha_pago = request.POST.get("fecha_pago")
        metodo_pago_str = request.POST.get("metodo_pago")  

       
        METODO_MAP = {
            "EFECTIVO": 1,
            "TRANSFERENCIA": 2,
            "DATAFONO": 3
        }

        metodo_pago = METODO_MAP.get(metodo_pago_str)  

        if metodo_pago is None: 
            messages.error(request, "Método de pago no válido.")
            return redirect("pago", reserva_id=reserva_id)
        elif monto_total < 0:
            messages.error(request, "El monto total no puede ser negativo.")
            return redirect("pago", reserva_id=reserva_id)

        try:
            q = Pago(
                monto_total=monto_total,
                fecha_pago=fecha_pago,
                metodo_pago=metodo_pago,
            )
            q.save()

            reserva.pago = q
            reserva.estado = "P" 
            reserva.save()

            detalles = f"""
            - Cliente: {reserva.cliente.nombre}
            - Habitación asignada por: {reserva.empleado.nombre}
            - Fecha de entrada: {reserva.fecha_inicio}
            - Fecha de salida: {reserva.fecha_fin}
            - Número de personas: {reserva.num_per}
            - Estado: {reserva.get_estado_display()}
            - Monto total: {monto_total}
            - Método de pago: {q.get_metodo_pago_display()}  
            """

            enviar_correo_reserva(reserva.cliente.correo, reserva.cliente.nombre, detalles)

            messages.success(request, "Pago realizado con éxito. Se ha enviado un correo de confirmación.")
            return redirect("Reservas")
        except Exception as e:
            messages.error(request, f"Error al procesar el pago: {e}")

    return render(request, 'funcionalidades/pago.html', {"reserva": reserva})




def menu(request):
    return render(request, 'menu.html')


def administrador(request):
    verificar = request.session.get("auth", False)
    if verificar:
        if verificar["rol"] == "Administrador":
            q = Reserva.objects.all()
            contexto = {
                "data": q
            }
            return render(request, "admin.html", contexto)
        else:
            messages.error(
                request, "Usted no tiene permisos para éste módulo...")
        return render(request, "index.html")
    else:
        messages.info(request, "Debe loguearse primero...")
        return redirect("login")

def Reservas(request):
    verificar = request.session.get("auth", False)
    if verificar:
        c = Usuario.objects.filter(rol=3)
        e = Empleado.objects.all()
        p = Pago.objects.all()
        h = Habitacion.objects.all()
        dis = Habitacion.objects.filter(estado="D")
        usuario_id = request.session["auth"]["id"]
        reserva = Reserva.objects.filter(cliente_id=usuario_id)
        contexto = {
            "clientes": c,
            "empleados": e,
            "pagos": p,
            "disponibles": dis,
            "reserva": reserva,
            "habitaciones": h
        }
        return render(request, 'Reservas.html', contexto)
    else:
        messages.warning(request, "Debe loguearse primero...")
        return redirect("login")

def listar_habitaciones(request):
    verificar = request.session.get("auth", False)
    if verificar:
        if verificar["rol"] == "Administrador":
            q = Habitacion.objects.all()
            contexto = {
                "data": q
            }
            return render(request,"listar/listar_habitaciones.html",contexto)
        else:
            messages.error(
                request, "Usted no tiene permisos para éste módulo...")
        return render(request, "index.html")
    else:
        messages.info(request, "Debe loguearse primero...")
        return redirect("login")
    
def listar_clientes(request):
    verificar = request.session.get("auth", False)
    if verificar:
        if verificar["rol"] == "Administrador":
            q = Usuario.objects.all()
            contexto = {
                "data": q
            }
            return render(request,"listar/listar_clientes.html",contexto)
        else:
            messages.error(
                request, "Usted no tiene permisos para éste módulo...")
        return render(request, "index.html")
    else:
        messages.info(request, "Debe loguearse primero...")
        return redirect("login")

def editar_habitacion(request, id_habitacion):
    if request.method == "POST":


        try:
            q = Habitacion.objects.get(pk=id_habitacion)
            
            q.nombre = request.POST.get("nombre")
            q.descripcion = request.POST.get("descripcion")
            q.capacidad = request.POST.get("capacidad")
            q.precio = Decimal(request.POST.get("precio")) 
            q.foto = request.FILES.get("foto", q.foto)
            q.estado = request.POST.get("estado")

            q.save()
            messages.success(request, "Habitación actualizada correctamente!")
            return redirect("listar_habitaciones")
        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect("editar_habitacion", id_habitacion=id_habitacion)
    else:
        q = Habitacion.objects.get(pk=id_habitacion)
        contexto = {
            "datos": q
        }
        return render(request, "funcionalidades/habitacion.html", contexto)

def agregar_reservas(request):
    if request.method == "POST":
        cliente_id = request.POST.get("cliente")
        empleados_disponibles = Empleado.objects.all() 
        num_per = request.POST.get("num_per")
        fecha_inicio = request.POST.get("inicio")
        fecha_fin = request.POST.get("fin")
        estado = "I"

        if empleados_disponibles.exists():  
            empleado = random.choice(empleados_disponibles)
        else:
            messages.error(request, "No hay empleados disponibles.")
        
        try:
            cliente = Usuario.objects.get(pk=cliente_id)
            q = Reserva(
                cliente=cliente,
                empleado=empleado,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                num_per=num_per,
                estado=estado
            )
            q.save()
            

            messages.success(request, "Reserva creada, procede al pago.")
            return redirect("pago", reserva_id=q.id)

        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect("Reservas")
    
    else:
        return render(request, "Reservas.html")


def terminos(request):
    return render(request,"funcionalidades/terminos_condiciones.html")

def enviar_correo_reserva(cliente_email, nombre_cliente, detalles_reserva):
    asunto = "Confirmación de tu reserva en Hostería El Solecito"
    mensaje = f"""
    Hola {nombre_cliente},

    Tu reserva ha sido confirmada con éxito.

    Detalles de la reserva:
    {detalles_reserva}

    ¡Gracias por elegirnos!

    Atentamente,
    Hostería El Solecito
    """

    send_mail(
        asunto, 
        mensaje,
        settings.EMAIL_HOST_USER,
        [cliente_email],  
        fail_silently=False,
    )

def Recuperar_clave(request):
    if request.method == "POST":
        correo = request.POST.get("email")
        try:
            usuario = Usuario.objects.get(correo=correo)
            messages.success(request,"Correo encontrado")
        except Usuario.DoesNotExist:
            messages.error(request, "El correo ingresado no está registrado.")
            return redirect("Recuperar_clave")
        
        reset_link = f"http://localhost:8000/restablecer_contraseña/{usuario.correo}/"

        enviar_correo_recuperar(usuario.correo,reset_link)
        messages.success(request, "Se ha enviado un enlace de recuperación a tu correo.")
        return redirect("login")


    return render(request,"funcionalidades/recuperar_clave.html")

def restablecer_contraseña(request,correo):
    try:
        usuario = Usuario.objects.get(correo=correo)
    except Usuario.DoesNotExist:
        messages.error(request, "El enlace no es válido.")
        return redirect("login")

    if request.method == "POST":
        nueva = request.POST.get("nueva")
        repite_nueva = request.POST.get("repite_nueva")

        if nueva == repite_nueva:
            if len(nueva) < 5:
                messages.error(request, "La contraseña debe ser mayor a 5 caracteres.")
            else:
                usuario.password = hash_password(nueva)
                usuario.save()
                messages.success(request, "Tu contraseña ha sido restablecida con éxito.")
                return redirect("login")
        else:
            messages.error(request, "Las contraseñas no coinciden.")

    return render(request, "funcionalidades/cambiar_clave.html", {"correo": correo})

def enviar_correo_recuperar(cliente_email,reset_link):
    asunto = "Recuperación de Contraseña - Hostería El Solecito"
    mensaje = f"""
    <html>
    <body>
        <p>Hemos recibido una solicitud para restablecer tu contraseña.</p>
        <p>Para proceder, haz clic en el botón de abajo:</p>
        <a href="{reset_link}" style="display: inline-block; padding: 10px 20px; font-size: 16px; color: white; background-color: #007BFF; text-decoration: none; border-radius: 5px;">Restablecer Contraseña</a>
        <p>Si no solicitaste este cambio, puedes ignorar este correo.</p>
        <p>Atentamente,<br>Hostería El Solecito</p>
    </body>
    </html>
    """

    send_mail(
        asunto, 
        mensaje,
        settings.EMAIL_HOST_USER,
        [cliente_email],  
        fail_silently=False,
    )
   
def eliminar_reserva(request, id_reserva):
    try:
        q = Reserva.objects.get(pk=id_reserva)
        q.delete()
        messages.success(request, "Reserva eliminada correctamente!")
    except IntegrityError:
        messages.warning(
            request, "Error: No puede eliminar la reserva, está en uso.")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    return redirect("Administrador")

def eliminar_habitacion(request, id_habitacion):
    try:
        q = Habitacion.objects.get(pk=id_habitacion)
        q.delete()
        messages.success(request, "Habitacion eliminada correctamente!")
    except IntegrityError:
        messages.warning(
            request, "Error: No puede eliminar la reserva, está en uso.")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    return redirect("listar_habitaciones")

def eliminar_usuario(request, id_usuario):
    try:
        q = Reserva.objects.get(pk=id_usuario)
        q.delete()
        messages.success(request, "Usuario eliminado correctamente!")
    except IntegrityError:
        messages.warning(
            request, "Error: No puede eliminar la reserva, está en uso.")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    return redirect("listar_clientes")

def editar_reserva(request, id_reserva):
    try:
        reserva = Reserva.objects.get(pk=id_reserva)
    except Reserva.DoesNotExist:
        messages.error(request, "La reserva que intentas editar no existe.")
        return redirect("Administrador")

    if request.method == "POST":
        try:
            reserva.cliente = Usuario.objects.get(pk=request.POST.get("cliente"))

            empleado_id = request.POST.get("empleado")
            if empleado_id:
                reserva.empleado = Empleado.objects.get(pk=empleado_id)

            pago_id = request.POST.get("pago")
            if pago_id:
                reserva.pago = Pago.objects.get(pk=pago_id)

            reserva.num_per = request.POST.get("num_per")
            reserva.fecha_inicio = request.POST.get("inicio")
            reserva.fecha_fin = request.POST.get("fin")
            reserva.save()

            messages.success(request, "¡Reserva actualizada correctamente!")
            return redirect("Reservas")

        except Exception as e:
            print(f"Error al actualizar reserva: {e}")
            messages.error(request, "Error al actualizar la reserva.")
            return redirect("editar_reserva", id_reserva=id_reserva)

    else:
        clientes = Usuario.objects.filter(rol=3)
        empleados = Empleado.objects.all()
        pagos = Pago.objects.all()

        contexto = {
            "datos": reserva,
            "clientes": clientes,
            "empleados": empleados,
            "pagos": pagos
        }
        return render(request, "Reservas.html", contexto)



def usuarios(request):
    q = Usuario.objects.all()
    contexto = {
        "data": q
    }
    return render(request, "index.html", contexto)


def agregar_usuario(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        correo = request.POST.get("correo")
        password = request.POST.get("password")
        tipo_documento = request.POST.get("tipo_documento")
        documento = request.POST.get("documento")
        foto = request.FILES.get("foto")
        telefono = request.POST.get("telefono")
        direccion = request.POST.get("direccion")
        
        confirm_password = request.POST.get("confirm_password")

        if "@" not in correo or ".com" not in correo:
            messages.error(
                request, "El correo debe contener '@' y terminar en '.com'")
            return redirect("Register")
        elif Usuario.objects.filter(nombre=nombre).exists():
            messages.error(
                request, "El Nombre de usuario ya está registrado. Usa otro.")
            return redirect("Register")
        elif Usuario.objects.filter(correo=correo).exists():
            messages.error(request, "El coreo ya está registrado. Usa otro.")
            return redirect("Register")
        elif not nombre or not correo or not password or not tipo_documento or not documento or not telefono or not direccion:
            messages.error(request, "Por favor, completa todos los campos.")
            return redirect("Register")
        elif q.documento < 0 or q.telefono < 0:
            messages.error(request, "Los valores de teléfono y documento deben ser positivos.")
            return redirect("Register")
        elif len(password) < 5:
            messages.error(request,"La contraseña debe ser mayor a 5 caracteres")
            return redirect("Register")

        try:
            if foto is not None:
                upload_file(foto)
                foto = f"usuarios/{foto.name}"
            else:
                foto = "usuarios/default.png"

            if password == confirm_password:
                q = Usuario(
                    nombre=nombre,
                    correo=correo,
                    tipo_documento=tipo_documento,
                    documento=int(documento),
                    foto=foto,
                    telefono=int(telefono),
                    direccion=direccion,
                    password=hash_password(password),
                    
                )
                q.save()
                messages.success(request, "Usuario agregado correctamente!")
                return redirect("login")
            else:
                messages.error(request, "Las contraseñas no coinciden")
                return redirect("Register")
        except ValueError:
            messages.error(request, "Los tipos de datos son incorrectos.")
            return redirect("Register")
        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect("Register")
    else:
        return render(request, "Register.html")

def editar_registro(request,id_usuario):
    if request.method == "POST":
        try:
            q = Usuario.objects.get(pk=id_usuario)

            q.nombre = request.POST.get("nombre")
            q.correo = request.POST.get("correo")
            q.tipo_documento = request.POST.get("tipo_documento")
            q.documento = request.POST.get("documento")
            q.foto = request.FILES.get("foto", q.foto)
            q.telefono = request.POST.get("telefono")
            q.direccion = request.POST.get("direccion")

            if q.documento < 0 or q.telefono < 0:
                messages.error(request,"no pueden ser negativos")
                return redirect("editar_registro", id_usuario=id_usuario)

            q.save()
            messages.success(request, "Usuario actualizado correctamente!")
            return redirect("index")
        except Exception as e:
            messages.error(request, f"Error")
            return redirect("editar_registro", id_usuario=id_usuario)
    else:
        q = Usuario.objects.get(pk=id_usuario)
        c = Usuario.objects.filter(rol=3)
        e = Empleado.objects.all()
        p = Pago.objects.all()
        contexto = {
            "datos": q,
            "clientes": c,
            "empleados": e,
            "pagos": p 
        }
        return render(request, "Register.html", contexto)

def upload_file(f):
    with open(f"{settings.MEDIA_ROOT}/usuarios/{f.name}", "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)

"""
<form method="POST" enctype="multipart/form-data">
"""
def editar_habitacion(request,id_habitacion):
    if request.method == "POST":

        try:
            q = Habitacion.objects.get(pk=id_habitacion)
            
            q.nombre = request.POST.get("nombre")
            q.descripcion = request.POST.get("descripcion")
            q.capacidad = request.POST.get("capacidad")
            q.precio = request.POST.get("precio")
            q.foto = request.FILES.get("foto",q.foto)
            q.estado = request.POST.get("estado")

            if q.capacidad < 0 or q.precio < 0:
                messages.error(request, "La capacidad y el precio no pueden ser negativos.")
                return redirect("agregar_habitacion")
            q.save()
            messages.success(request, "Habitacion actualizada correctamente!")
            return redirect("listar_habitaciones")
        except Exception as e:
            messages.error(request, f"Error")
            return redirect("editar_habitacion", id_habitacion=id_habitacion)
    else:
        q = Habitacion.objects.get(pk=id_habitacion)
        contexto = {
            "datos": q
        }
        return render(request, "funcionalidades/habitacion.html", contexto)
    
def agregar_habitacion(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        descripcion = request.POST.get("descripcion")
        capacidad = request.POST.get("capacidad")
        precio = request.POST.get("precio")
        foto = request.FILES.get("foto")
        estado = request.POST.get("estado")

        if not nombre or not descripcion or not capacidad or not precio or not foto or not estado:
            messages.error(request, "Por favor, completa todos los campos.")
            return redirect("agregar_habitacion")
        elif capacidad < 0 or precio < 0:
            messages.error(request, "La capacidad y el precio no pueden ser negativos.")
            return redirect("agregar_habitacion")
        
        try:
            
                
            q = Habitacion(
                nombre=nombre,
                descripcion=descripcion,
                capacidad=int(capacidad),
                foto=foto,
                precio=int(precio),
                estado=estado
            )
            if foto:
                q.foto = foto
            q.save()
            messages.success(request, "Habitacion agregada correctamente!")
            return redirect("listar_habitaciones")
        except ValueError:
            messages.error(request, "Los tipos de datos son incorrectos.")
            return redirect("agregar_habitacion")
        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect("agregar_habitacion")
    else:
        return render(request, "funcionalidades/habitacion.html")

def register(request):
    return render(request, "Register.html")


def vendedor(request):
    return render(request, 'vendedor.html')

def habitacion(request):
    return render(request, 'funcionalidades/habitacion.html')

def contactar(request):
    if request.method == "POST":
        asunto = request.POST.get("txtNombre", "")
        mensaje = request.POST.get("txtMensaje", "") + \
            " / Email: " + request.POST.get("txtEmail", "")
        email_desde = settings.EMAIL_HOST_USER
        email_para = ["hosteriaelsolecito@gmail.com"]

        send_mail(asunto, mensaje, email_desde,
                  email_para, fail_silently=False)

        return JsonResponse(
            {"success": True, "message": "Mensaje enviado con éxito. Nos pondremos en contacto contigo pronto."},
            json_dumps_params={'ensure_ascii': False}
        )

    return JsonResponse({"success": False, "message": "Método no permitido"}, status=400)


def cambiar_clave(request):
    if request.method == "POST":
        clave_actual = request.POST.get("clave_actual")
        nueva = request.POST.get("nueva")
        repite_nueva = request.POST.get("repite_nueva")
        logueado = request.session.get("auth", False)
        q = Usuario.objects.get(pk=logueado["id"])
        if verify_password(clave_actual, q.password):
            if clave_actual != nueva:
                if nueva == repite_nueva:
                    if len(nueva) < 5:
                        messages.error(request,"La contraseña debe ser mayos a 5 caracteres")
                    else:
                        q.password = hash_password(nueva)       # utils.py
                        q.save()
                        messages.success(request, "Contraseña cambiada con éxito!!")
                        return redirect("index")
                else:
                    messages.info(request, "Contraseñas nuevas no coinciden...")
            else:
                messages.warning(request, "para cambiar las contraseña debe ser diferente")     
        else:
            messages.warning(request, "Contraseña no concuerda...")

        return redirect("cambiar_clave")
    else:
        return render(request, "funcionalidades/cambiar_clave.html")
    
            

""" def crear_detalle_reserva(request):
    if request.method == "POST":
        habitacion = request.POST.get("habitacion")
        disponibles = Habitacion.objects.filter(estado="D")
        if habitacion.estado in disponibles:
             """