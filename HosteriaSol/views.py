from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect,  get_object_or_404
from .models import Usuario, Reserva, Empleado, Pago, Habitacion, DetalleReserva, Servicio
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django.db.utils import IntegrityError
from django.contrib import messages
from datetime import datetime,date
import pytz
from django.utils import timezone
from decimal import Decimal
from django.core.mail import send_mail
from django.conf import settings
import random
import time
import string
import re
from .utils import verify_password, hash_password



def index(request):
    return render(request, 'index.html')


def eliminar_usuario(request, id_usuario):
    try:
        usuario_a_eliminar = get_object_or_404(Usuario, pk=id_usuario)
        usuario_id_en_sesion = request.session.get('auth', {}).get('id')

        if usuario_id_en_sesion and int(usuario_id_en_sesion) == usuario_a_eliminar.id:
            messages.warning(
                request, "Este usuario está logueado actualmente y no puede ser eliminado.")
        
        elif usuario_a_eliminar.activo:
            messages.warning(
                request, "Este usuario tiene una sesión activa y no puede ser eliminado.")
        
        else:
            usuario_a_eliminar.delete()
            messages.success(request, "Usuario eliminado correctamente!")

    except IntegrityError:
        messages.warning(
            request, "Error: No puede eliminar el usuario, está en uso.")
    except Exception as e:
        messages.error(request, f"Error: {e}")

    return redirect("listar_clientes")



def login(request):
    if request.method == 'POST':
        request.session["data"] = request.POST

        usuario = request.POST.get('usuario')
        contrasena = request.POST.get('contrasena')
        
        try:
            q = Usuario.objects.get(correo=usuario)
            if verify_password(contrasena, q.password):
                q.activo = True
                q.save()

                request.session["auth"] = {
                    "id": q.id,
                    "nombre": q.nombre,
                    "correo": q.correo,
                    "foto": q.foto.url,
                    "telefono": q.telefono,
                    "rol": q.get_rol_display(),
                }
                request.session["data"] = None
                return redirect("index")
            else:
                raise Usuario.DoesNotExist()
        except Usuario.DoesNotExist:
            messages.warning(request, "Usuario o contraseña no válidos..")
            request.session["auth"] = None
        except Exception as e:
            messages.error(request, f"Error: {e}")
            request.session["auth"] = None
        return render(request,"login.html")
    
    else:
        verificar = request.session.get("auth", False)
        if verificar:
            return redirect("index")
        else:
            return render(request, "login.html")

def logout(request):
    try:
        usuario = request.session.get("auth")
        
        if usuario:
            try:
                q = Usuario.objects.get(pk=usuario["id"])
                if q.activo:
                    q.activo = False
                    q.save()
            except Usuario.DoesNotExist:
                pass

       
            request.session.flush()

            messages.success(request, "Sesión cerrada correctamente.")
            return redirect("login")
        else:
            messages.info(request, "No hay una sesión activa.")
            return redirect("login")
            
    except Exception as e:
        messages.error(request, f"No se pudo cerrar sesión: {e}")
        return redirect("index")

def galeria(request):
    imagenes = [
        'img/imag/64501219.jpg',
        'img/imag/Delux.jpg',
        'img/imag/caption.jpg',
        'img/imag/caption (1).jpg',
        'img/imag/hosteria-florida-tropical.jpg',
        'img/imag/el-paraiso.jpg',
        'img/imag/IMG_4580.avif',
        'img/imag/restaurante.avif',
        'img/imag/jiji.jpg',
        'img/imag/sala.avif',
        'img/imag/juegos.jpg',
        'img/imag/natu.jpg',
    ]
    return render(request, 'Galeria.html', {'imagenes': imagenes})



def nosotros(request):
    return render(request, 'Nosotros.html')


def habitaciones(request):
    q = Habitacion.objects.all()
    contexto = {
        "habitaciones": q
    }
    return render(request, 'Habitaciones.html', contexto)

def servicios(request):
    servicios = Servicio.objects.all()
    return render(request, 'Servicios.html', {'servicios': servicios})



def menu(request):
    return render(request, 'menu.html')


def administrador(request):
    verificar = request.session.get("auth", False)
    if verificar:
        if verificar["rol"] == "Administrador":
            try:
                reservas = Reserva.objects.all()
                detalles = DetalleReserva.objects.all()
                toda_reserva = []
                for reserva in reservas:
                    detalles_reserva = DetalleReserva.objects.filter(reserva_id=reserva.id)
                    total_habitaciones = 0
                    habitaciones_lista = []
                    nombres_habitaciones = []

                    if detalles_reserva.exists():
                        for detalle in detalles_reserva:
                            if detalle.habitacion:
                                total_habitaciones += 1
                                habitaciones_lista.append(detalle.habitacion)
                                nombre_hab = detalle.habitacion.nombre
                                nombres_habitaciones.append(nombre_hab)
                        
                    toda_reserva.append({
                        'reserva': reserva,
                        'habitacion': None,
                        'habitacion_nombre': "Sin habitación asignada"
                    })        
                    reserva.total_habitaciones = total_habitaciones
                    reserva.habitaciones = habitaciones_lista
                    reserva.num_p = reserva.adultos + reserva.ninos 
                    reserva.nombres_habitaciones = ", ".join(nombres_habitaciones) if nombres_habitaciones else "Sin habitaciones"

                    
                    
            except Exception as e:
                print(f"Error al procesar reservas: {e}")
                toda_reserva = []

                        
            except Reserva.DoesNotExist:
                reserva_existente = None
            except DetalleReserva.DoesNotExist:
                detalle = None

            contexto= {
                "servicios": servicios,
                'reserva_existente': toda_reserva,
                'detalles' : detalles,
            }
            request.session["admin"] = "soy admin"
            request.session["datos"] = None
            return render(request, "admin.html", contexto)
        else:
            messages.error(
                request, "Usted no tiene permisos para éste módulo...")
        return render(request, "index.html")
    else:
        messages.info(request, "Debe loguearse primero...")
        return redirect("login") 

def listar_habitaciones(request):
    verificar = request.session.get("auth", False)
    if verificar:
        if verificar["rol"] == "Administrador":
            q = Habitacion.objects.all()
            contexto = {
                "data": q
            }
            return render(request, "listar/listar_habitaciones.html", contexto)
        else:
            messages.error(
                request, "Usted no tiene permisos para éste módulo...")
        return render(request, "index.html")
    else:
        messages.info(request, "Debe loguearse primero...")
        return redirect("login")

def listar_empleados(request):
    verificar = request.session.get("auth", False)
    if verificar:
        if verificar["rol"] == "Administrador":
            q = Empleado.objects.all()
            contexto = {
                "data": q
            }
            return render(request, "listar/listar_empleados.html", contexto)
        else:
            messages.error(
                request, "Usted no tiene permisos para este módulo...")
            return render(request, "index.html")
    else:
        messages.info(request, "Debe loguearse primero...")
        return redirect("login")
    
    
def listar_clientes(request):
    verificar = request.session.get("auth", False)
    admin = request.session.get("auth", False)
    if verificar:
        if verificar["rol"] == "Administrador":
            q = Usuario.objects.all()
            contexto = {
                "data": q,
                'admin': admin
            }
            request.session["data"] = None
            return render(request, "listar/listar_clientes.html", contexto)
        else:
            messages.error(
                request, "Usted no tiene permisos para éste módulo...")
        return render(request, "index.html")
    else:
        messages.info(request, "Debe loguearse primero...")
        return redirect("login")

def listar_servicios(request):
    
    verificar = request.session.get("auth", False)
    if verificar:
        if verificar["rol"] == "Administrador":
            servicios = Servicio.objects.all()
            contexto = {
                "data": servicios
            }
            request.session["data"] = None
            return render(request, "listar/listar_servicios.html", contexto)
        else:
            messages.error(
                request, "Usted no tiene permisos para este módulo...")
            return render(request, "index.html")
    else:
        messages.info(request, "Debe loguearse primero...")
        return redirect("login")

def editar_habitacion(request, id_habitacion):
    if request.method == "POST":
        request.session["data"] = request.POST

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
        request.session["data"] = None
        return render(request, "funcionalidades/habitacion.html", contexto)

def editar_servicio(request, id_servicio):
    servicio = get_object_or_404(Servicio, pk=id_servicio)

    if request.method == "POST":
        request.session["data"] = request.POST
        try:
            servicio.nombre = request.POST.get("nombre", servicio.nombre)
            servicio.precio = Decimal(request.POST.get("precio", servicio.precio))
            servicio.descripcion = request.POST.get("descripcion", servicio.descripcion)
            servicio.hora_inicio = request.POST.get("inicio", servicio.hora_inicio)
            servicio.hora_fin = request.POST.get("fin", servicio.hora_fin)
            
            if request.FILES.get("foto"):  # Esta verifica si el usuario subió una nueva imagen
                servicio.foto = request.FILES["foto"]  # Si el usuario subio una nueva imagen, actualiza la imagen
                
            if request.POST.get("estado") == "on":
                servicio.estado = "A"
            else:
                servicio.estado = "I"

            if not servicio.nombre or not servicio.descripcion or not servicio.precio or not servicio.hora_inicio or not servicio.hora_fin or not servicio.foto:
                messages.error(request, "Por favor, completa todos los campos.")
                return redirect("editar_servicio")
            
            if servicio.hora_inicio >= servicio.hora_fin:
                messages.error(request, "La hora de inicio debe ser menor que la hora de fin.")
                return redirect("editar_servicio")

            if len(servicio.descripcion) > 250:
                messages.error(request, "La descripción no puede superar los 250 caracteres.")
                return redirect("editar_servicio")
            
            if len(servicio.descripcion) <= 20:
                messages.error(request, "La descripción no puede ser menor o igual que 20 caracteres.")
                return redirect("editar_servicio")
            
            if Servicio.objects.filter(nombre=servicio.nombre).exists():
                messages.error(request, "El Nombre de servicio ya está registrado. Usa otro.")  
                return redirect("editar_servicio")

            try:
                servicio.precio = float(servicio.precio)
                if servicio.precio < 0:
                    messages.error(request, "El precio no puede ser negativo.")
                    return redirect("editar_servicio")
            except ValueError:
                messages.error(request, "El precio debe ser un número válido.")
                return redirect("editar_servicio")
            servicio.save()
            messages.success(request, "Servicio actualizado correctamente!")
            request.session["data"] = None
            return redirect("listar_servicios")
        except Exception as e:
            messages.error(request, f"Error al actualizar el servicio: {e}")
            return redirect("editar_servicio", id_servicio=id_servicio)
    else:
        contexto = {
            "datos": servicio
        }
        request.session["data"] = None
        return render(request, "funcionalidades/servicio.html", contexto)

def agregar_reservas(request):
    verificar = request.session.get("auth", False)
    request.session["datos"] = None
    if verificar:
        if request.method == "POST":    
            request.session["data"] = request.POST
            fechas = request.POST.get("fechas")
            adultos = int(request.POST.get('adultos',0))
            ninos = int(request.POST.get('ninos', 0))
            cliente_id = request.POST.get("cliente")
            empleados_disponibles = Empleado.objects.all()
            num_per = adultos + ninos
            estado = "I"
            servicio_id = request.POST.get("servicio_id",None)
            servicios = Servicio.objects.all()
            usuario_id = request.session.get('auth', {}).get('id')
            ahora = date.today()
            reservas = Reserva.objects.all()
            for reserva in reservas:
                if reserva.fecha_fin < ahora and reserva.estado != "C":
                    reserva.estado = "C"
                    reserva.save()
            todas_habitaciones = Habitacion.objects.all()
            cantidad= int(request.POST.get("cantidad"))
            

            contexto= {
                "servicios": servicios,
            }
            
            try:
                usuario = Usuario.objects.get(pk=usuario_id)
                reserva_existente = Reserva.objects.filter(cliente_id=usuario)
            except Reserva.DoesNotExist:
                reserva_existente = None
            

            if not fechas or "a" not in fechas:
                messages.info(
                    request, "Debes seleccionar una fecha de entrada y salida.")
                return render(request, 'Reservas.html',contexto)

            if not all([cliente_id, cantidad, adultos, fechas]):
                messages.error(request, "Por favor, completa todos los campos obligatorios.")
                return render(request, 'Reservas.html',contexto)

            if cantidad < 1:
                messages.info(request, "Debes seleccionar minimo 1 habitacion.")
                return render(request, 'Reservas.html',contexto)
            elif cantidad > 5:
                messages.info(request, "Debes seleccionar minimo 1 habitacion.")
                return render(request, 'Reservas.html',contexto)

            try:
                if not adultos:
                    adultos = 0
                else:
                    adultos = int(adultos)
                if adultos < 1:
                    messages.info(
                        request, "Debe haber al menos un adulto por habitación.")
                    return render(request, 'Reservas.html',contexto)
                elif adultos > 20:
                    messages.info(request, "paso el maximo de capacidad por reserva")
                    return render(request, 'Reservas.html',contexto)
            except:
                messages.error(request, "Número de adultos inválido.")
                return render(request, 'Reservas.html',contexto)

            try:
                if not ninos:
                    ninos = 0
                else:
                    ninos = int(ninos)
                ninos = int(ninos)
                if ninos < 0:
                    messages.error(
                        request, "El número de niños no puede ser negativo.")
                    return render(request, 'Reservas.html',contexto)
                elif ninos > 30:
                    messages.info(request, "paso el maximo de capacidad por reserva")
                    return render(request, 'Reservas.html',contexto)
            except:
                messages.error(request, "Número de niños inválido.")
                return render(request, 'Reservas.html',contexto)
            
            adult_e = adultos * 2
            if ninos > adult_e:
                messages.info(request, "cada adulto puede llevar 2 niños.")
                return render(request, 'Reservas.html',contexto)
            
            if adultos < cantidad:
                messages.info(request, "Debe haber un adulto por habitacion.")
                return render(request, 'Reservas.html',contexto)

            try:
                fecha_entrada_str, fecha_salida_str = fechas.split(" a ")
                fecha_entrada = datetime.strptime(fecha_entrada_str.strip(), "%Y-%m-%d").date()
                fecha_salida = datetime.strptime(fecha_salida_str.strip(), "%Y-%m-%d").date()
                
                if fecha_entrada >= fecha_salida:
                    messages.error(request, "La fecha de salida debe ser después de la fecha de entrada.")
                    return render(request, 'Reservas.html',contexto)
                
                if fecha_entrada < ahora or fecha_salida < ahora:
                    messages.error(request, "La fecha debe ser despues de hoy no antes.")
                    return render(request, 'Reservas.html',contexto)
                
                empleado = random.choice(empleados_disponibles)
                cliente = Usuario.objects.get(pk=cliente_id)
                
                ocupadas_ids = []
                disponibles_ids = []

                for habitacion in todas_habitaciones:
                    disponibles_ids.append(habitacion.id)

                for reserva in reservas:
                    fecha_inicio_reserva = reserva.fecha_inicio
                    fecha_fin_reserva = reserva.fecha_fin
                    
                    if not disponible(fecha_entrada, fecha_salida, fecha_inicio_reserva, fecha_fin_reserva):
                        detalles = DetalleReserva.objects.filter(reserva=reserva)
                        
                        for detalle in detalles:
                            habitacion_id = detalle.habitacion.id
                            if habitacion_id in disponibles_ids:
                                disponibles_ids.remove(habitacion_id)
                                if habitacion_id not in ocupadas_ids:
                                    ocupadas_ids.append(habitacion_id)

                habitaciones_ocupadas = Habitacion.objects.filter(id__in=ocupadas_ids)
                habitaciones_disponibles = Habitacion.objects.filter(id__in=disponibles_ids)
                        
                        
                request.session['datos_reserva'] = {
                    'cantidad': cantidad,
                    'disponibles': [habitacion.to_dict() for habitacion in habitaciones_disponibles],
                    'ocupadas': [habitacion.to_dict() for habitacion in habitaciones_ocupadas]
                }     
                    
                q = Reserva(
                    cliente=cliente,
                    empleado=empleado,
                    fecha_inicio=fecha_entrada,
                    fecha_fin=fecha_salida,
                    adultos=adultos,
                    ninos=ninos,
                    estado=estado
                )
                q.save()
                
                if servicio_id:
                    return redirect('Reservas2', reserva_id=q.id, servicio_id=servicio_id)
                else:
                    return redirect('Reservas2_sin_servicio', reserva_id=q.id)      
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
                return render(request, 'Reservas.html',contexto)
            except Reserva.DoesNotExist:
                messages.error(request, "Algo salio mal Sal y vuelve a entrar")
                return render(request, 'Reservas.html',contexto)
        else:
            servicios = Servicio.objects.all()
            usuario_id = request.session.get('auth', {}).get('id')
            
            try:
                usuario = Usuario.objects.get(pk=usuario_id)
                reserva_existente = Reserva.objects.filter(cliente_id=usuario)
                detalles = DetalleReserva.objects.all()
                for reserva in reserva_existente:
                    total = 1
                    for detalle in detalles:
                        if detalle.reserva_id == reserva.id:
                            total += detalle.cantidad or 1
                    reserva.total_habitaciones = total
                    reserva.num_p = reserva.adultos + reserva.ninos

            except Reserva.DoesNotExist:
                reserva_existente = None
            except DetalleReserva.DoesNotExist:
                detalle = None

            contexto= {
                "servicios": servicios,
                'reserva_existente': reserva_existente,
                'detalles' : detalles,
            }
            request.session["data"] = None
            return render(request, 'Reservas.html',contexto)
    else:
        messages.info(request, "Debe loguearse primero...")
        request.session["data"] = None
        return redirect("login")

def disponible(fecha_entrada, fecha_salida, fecha1, fecha2):
    return not (fecha_entrada <= fecha2) and (fecha1 <= fecha_salida)
# revisar esto

def empleados(request):
    verificar = request.session.get("auth", False)
    if verificar:
        if verificar["rol"] == "Administrador":
            q = Empleado.objects.all()
            contexto = {
                "data": q
            }
            return render(request, "listar/listar_empleados.html", contexto)
        else:
            messages.error(
                request, "Usted no tiene permisos para este módulo...")
        return render(request, "index.html")
    else:
        messages.info(request, "Debe loguearse primero...")
        return redirect("login")

def agregar_empleados(request):
    if request.method == "POST":
        request.session["data"] = request.POST
        
        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        correo = request.POST.get("correo")
        password = request.POST.get("password")
        foto = request.FILES.get("foto")
        cargo = request.POST.get("cargo")
        confirm_password = request.POST.get("confirm_password")

        if not nombre or not apellido or not correo or not cargo:
            messages.error(request, "Por favor, completa todos los campos.")
            return redirect("agregar_empleados")

        if "@" not in correo or ".com" not in correo:
            messages.error(request, "El correo ingresado no es válido.")
            return redirect("agregar_empleados")

        if Empleado.objects.filter(correo=correo).exists():
            messages.error(request, "Este correo ya está registrado.")
            return redirect("agregar_empleados")
        
        if Empleado.objects.filter(nombre=nombre).exists():
                messages.error(request, "El correo ya está registrado en otro empleado.")
                return redirect("agregar_empleados")

        
        try:
            if password == confirm_password:
                i = Empleado(
                    nombre=nombre,
                    apellido=apellido,
                    correo=correo,
                    password=hash_password(password),
                    cargo=cargo,
                )
                if foto:
                    i.foto = foto

                i.save()
                o = Usuario(
                    nombre=nombre,
                    correo=correo,
                    password=hash_password(password),
                    rol=3,
                )
                if foto:
                    o.foto = foto
                o.save()
                request.session["data"] = None
                messages.success(request, "Empleado agregardo correctamente.")
                return redirect("listar_empleados")
            else:
                messages.error(request, "Las contraseñas no coinciden")
                return redirect("agregar_empleados")
        except Exception as a:
            messages.error(request, f"Error al guardar el empleado: {a}")
        return redirect("agregar_empleados")

    else:
        return render(request, "funcionalidades/empleados.html")

def editar_empleados(request, id_empleado):
    if request.method == "POST":
        request.session["data"] = request.POST
        try:
            i = Empleado.objects.get(pk=id_empleado)

            nombre = request.POST.get("nombre")
            apellido = request.POST.get("apellido")
            correo = request.POST.get("correo")
            cargo = request.POST.get("cargo")
            foto = request.FILES.get("foto")

            if not nombre or not apellido or not correo or not cargo:
                messages.error(request, "Todos los campos son obligatorios.")
                return redirect("editar_empleados", id_empleado=id_empleado)

            if "@" not in correo or ".com" not in correo:
                messages.error(request, "El correo debe contener '@' y '.com'")
                return redirect("editar_empleados", id_empleado=id_empleado)

            if Empleado.objects.exclude(pk=i.pk).filter(correo=correo).exists():
                messages.error(request, "El correo ya está registrado en otro empleado.")
                return redirect("editar_empleados", id_empleado=id_empleado)
            
            if Empleado.objects.exclude(pk=i.pk).filter(correo=nombre).exists():
                messages.error(request, "El correo ya está registrado en otro empleado.")
                return redirect("editar_empleados", id_empleado=id_empleado)

            i.nombre = nombre
            i.apellido = apellido
            i.correo = correo
            i.cargo = cargo
            if foto:
                i.foto = foto

            i.save()
            
            try:
                u = Usuario.objects.get(correo=i.correo)  
                u.nombre = nombre
                u.correo = correo
                if foto:
                    u.foto = foto
                u.save()
            except Usuario.DoesNotExist:
                pass
            
            request.session["data"] = None
            messages.success(request, "Empleado actualizado correctamente.")
            return redirect("listar_empleados")

        except Exception as a:
            messages.error(request, f"Error al actualizar el empleado: {a}")
            return redirect("editar_empleados", id_empleado=id_empleado)

    else:
        i = Empleado.objects.get(pk=id_empleado)
        contexto = {
            "datos": i
        }     
        return render(request, "funcionalidades/empleados.html", contexto)
    
    
def listar_reservas(request):
    reserva_existente = Reserva.objects.all()
    
    detalles = DetalleReserva.objects.all()
    for reserva in reserva_existente:
        total = 1
        for detalle in detalles:
            if detalle.reserva_id == reserva.id:
                total += detalle.cantidad or 1
        reserva.total_habitaciones = total
        reserva.num_p = reserva.adultos + reserva.ninos

    contexto = {
        'reserva_existente': reserva_existente,
    }
    return render(request, 'admin.html', contexto)

def Reservas2(request, reserva_id,servicio_id=None):
    try:
        cantidad = request.session.get('datos_reserva', {}).get('cantidad') 
        disponibles = request.session.get('datos_reserva', {}).get('disponibles')
        datos = request.session.get("datos",False)

        if cantidad > len(disponibles):
            messages.info(request, f"en esa fecha solo hay {len(disponibles)} habitaciones disponibles.")
            return redirect('agregar_reservas')
        
        try:
            cantidad = int(cantidad)
        except (ValueError, TypeError):
            cantidad = 1
        reserva = Reserva.objects.get(pk=reserva_id)

        seleccionadas = request.session.get('datos_reserva', {}).get('h_seleccionadas', [])
        cantidad_h = request.session.get('datos_reserva', {}).get('cantidad',1)

                
        contexto = {
            'servicio_id': servicio_id,
            'reserva': reserva,
            'cantidad':cantidad,
            'seleccionadas':seleccionadas,
            'cantidad ': cantidad_h,
            'datos':datos
        }
        
    except Reserva.DoesNotExist:
        messages.error(request, "La reserva no existe.")
        return redirect('agregar_reservas')
    
    return render(request, "Reservas2.html", contexto)

def seleccion_habitacion(request,id_habitacion,reserva_id,servicio_id=None):
    verificar = request.session.get("auth", False)
    if verificar:
        if request.method == "POST":
            try:
                datos_reserva = request.session.get('datos_reserva', {})
                habitacion = Habitacion.objects.get(id=id_habitacion)
                if 'h_seleccionadas' not in datos_reserva:
                    datos_reserva['h_seleccionadas'] = []
                id_seleccionadas = [h.get('id') for h in datos_reserva['h_seleccionadas']]
                cantidad_h = request.session.get('datos_reserva', {}).get('cantidad',0)

                if 'h_seleccionadas' not in datos_reserva:
                    datos_reserva['h_seleccionadas'] = []

                if len(id_seleccionadas) <  cantidad_h:
                    if habitacion.id not in id_seleccionadas:
                        datos_reserva['h_seleccionadas'].append(habitacion.to_dict())
                        request.session['datos_reserva'] = datos_reserva    
                        messages.success(request,"Agregada correctamente")
                    else:
                        messages.info(request, "Esta habitación ya estaba seleccionada")
                else:
                    messages.info(request, f"ya no puedes agregar mas de la cantidad deleccionada {cantidad_h}")
                                
                if servicio_id:
                    return redirect("Reservas2",reserva_id=reserva_id,servicio_id=servicio_id)
                else:
                    return redirect("Reservas2",reserva_id=reserva_id,servicio_id=4)
            except Exception as e:
                messages.error(request, f"Error al guardar el habitacion: {e}")
                if servicio_id:
                    return redirect("Reservas2",reserva_id=reserva_id,servicio_id=servicio_id)
                else:
                    return redirect("Reservas2",reserva_id=reserva_id)
        else:
            messages.info(request, "intente de nuevo...")
    else:
        messages.info(request, "Debe loguearse primero...")
        return redirect("login")
    
def eliminar_seleccion(request,id_habitacion,reserva_id,servicio_id=None):
    datos_reserva = request.session.get('datos_reserva', {})
    habitaciones_seleccionadas = datos_reserva.get('h_seleccionadas', [])

    encontrada = False

    habitaciones_filtradas = []

    for habitacion in habitaciones_seleccionadas:
        if habitacion.get('id') != id_habitacion:
            habitaciones_filtradas.append(habitacion)
        else:
            encontrada = True 

    if encontrada:
        datos_reserva['h_seleccionadas'] = habitaciones_filtradas
        request.session['datos_reserva'] = datos_reserva
        messages.success(request, "Habitación eliminada con éxito.")
    else:
        messages.error(request, "Habitación no encontrada en la selección.")

    if servicio_id:
        return redirect("Reservas2",reserva_id=reserva_id,servicio_id=servicio_id)
    else:
        return redirect("Reservas2_sin_servicio",reserva_id=reserva_id) 

def pago(request,reserva_id,id_habitacion=None,servicio_id=None):
    try:
        datos_reserva = request.session.get('datos_reserva', {})
        cantidad = int(datos_reserva.get('cantidad', 1))
        seleccionadas = datos_reserva.get('h_seleccionadas', [])
        
        reserva = Reserva.objects.get(pk=reserva_id)
        zona = pytz.timezone('America/Bogota')
        fecha_pago_actual = datetime.now(zona)
        precio_total = 0  
        num_per = reserva.ninos +reserva.adultos
        DetalleReserva.objects.filter(reserva=reserva).delete()
        if cantidad > 1:
            cap_m = 0
            for habitacion in seleccionadas:
                habitacion = Habitacion.objects.filter(id=habitacion.get('id'))
                for habita in habitacion:
                    cap_m += habita.capacidad
            cap_m += 4
            if cap_m < num_per:
                messages.info(request, "pasa la capacidad maxima de las habitaciones.")
                if servicio_id:
                    return redirect("Reservas2",reserva_id=reserva_id,servicio_id=servicio_id)
                else:
                    return redirect("Reservas2_sin_servicio",reserva_id=reserva_id)
        else:
            habitacion = Habitacion.objects.get(pk=id_habitacion)
            if habitacion.capacidad < num_per:
                messages.info(request, "pasa la capacidad maxima de la habitacion.")
                if servicio_id:
                    return redirect("Reservas2",reserva_id=reserva_id,servicio_id=servicio_id)
                else:
                    return redirect("Reservas2_sin_servicio",reserva_id=reserva_id)

        if cantidad > 1:
            habitaciones = []
            for habi in seleccionadas:
                habitacion = Habitacion.objects.get(pk=habi['id'])
                dias = (reserva.fecha_fin - reserva.fecha_inicio).days
                precio_habi = habitacion.precio * dias
                precio_total += precio_habi
                habitaciones.append(habitacion)
        else:
            habitacion = Habitacion.objects.get(pk=id_habitacion)
            dias = (reserva.fecha_fin - reserva.fecha_inicio).days
            precio_habi = habitacion.precio * dias
            precio_total = precio_habi

        if servicio_id:
            try:
                servicio = Servicio.objects.get(id=servicio_id)
                precio_total += float(servicio.precio)
            except Servicio.DoesNotExist:
                servicio = None
        else:
            servicio = None

        pagon = Pago.objects.create(
            monto_total=precio_total,
            fecha_pago=fecha_pago_actual
        )

        if cantidad > 1:
            for habitacion in habitaciones:
                if servicio_id:
                    DetalleReserva.objects.create(
                        habitacion=habitacion,
                        reserva=reserva,
                        cantidad=1,
                        precio_neto=habitacion.precio * dias,
                        servicio=servicio,
                    )
                else:
                    DetalleReserva.objects.create(
                        habitacion=habitacion,
                        reserva=reserva,
                        cantidad=1,
                        precio_neto=habitacion.precio * dias,
                    )
        else:
            if servicio_id:
                detalle_reserva = DetalleReserva(
                        habitacion=habitacion,
                        reserva=reserva,
                        cantidad=cantidad,
                        precio_neto=precio_total,
                        servicio=servicio
                    )
            else:
                detalle_reserva = DetalleReserva(
                        habitacion=habitacion,
                        reserva=reserva,
                        cantidad=cantidad,
                        precio_neto=precio_total,
                    )
                
            detalle_reserva.save()
        
        reserva.estado = "P"
        reserva.pago = pagon
        reserva.save()
        
        contexto = {
            'habitacion': habitacion,
            'reserva': reserva,
            'fecha_entrada': reserva.fecha_inicio,
            'fecha_salida': reserva.fecha_fin,
            'numero_personas': reserva.adultos + reserva.ninos,
            'precio_habi': habitacion.precio,
            'precio_total': precio_total,
            'seleccionadas':seleccionadas,
            'cantidad':cantidad,
        }

    except (Habitacion.DoesNotExist, Reserva.DoesNotExist):
        messages.error(request, "Error al cargar los detalles.")
        return redirect('reservas')
    request.session["data"] = None

    return render(request, 'funcionalidades/pago.html', contexto)

def confirmar_pago(request):
    if request.method == "POST":
        request.session["data"] = request.POST.dict()
        
        reserva_id = request.POST.get("reserva_id")
        habitacion_id = request.POST.get("habitacion_id")
        servicio_id = request.POST.get("servicio_id")
        peticion = request.POST.get("peticion")
        telefono = request.POST.get("telefono")
        email = request.POST.get("email")
        nombre = request.POST.get("nombre")
        precio_total = request.POST.get("precio_total")
        metodo__pago = request.POST.get("metodo_pago")
        titular = request.POST.get("titular")
        tarjeta = request.POST.get("tarjeta")
        cvc = request.POST.get("cvc")
        caducidad = request.POST.get("caducidad")
        
        
        if metodo__pago == "3":
            if not titular:
                messages.warning(request, "El nombre del titular es obligatorio.") 
                if servicio_id:
                    return redirect("pago", reserva_id=reserva_id, servicio_id=servicio_id)
                else:
                    return redirect("pago_sin_servicio", reserva_id=reserva_id,id_habitacion=habitacion_id)

            if not tarjeta:
                messages.warning(request, "El número de tarjeta es obligatorio.")
                if servicio_id:
                    return redirect("pago", reserva_id=reserva_id, servicio_id=servicio_id)
                else:
                    return redirect("pago_sin_servicio", reserva_id=reserva_id,id_habitacion=habitacion_id)
            elif not tarjeta.isdigit():
                messages.warning(request, "El número de tarjeta debe contener solo dígitos.")
                if servicio_id:
                    return redirect("pago", reserva_id=reserva_id, servicio_id=servicio_id)
                else:
                    return redirect("pago_sin_servicio", reserva_id=reserva_id,id_habitacion=habitacion_id)
            elif len(tarjeta) < 13 or len(tarjeta) > 19:
                messages.warning(request, "Número de tarjeta inválido.")
                if servicio_id:
                    return redirect("pago", reserva_id=reserva_id, servicio_id=servicio_id)
                else:
                    return redirect("pago_sin_servicio", reserva_id=reserva_id,id_habitacion=habitacion_id)

            if not cvc:
                messages.warning(request, "El código de seguridad es obligatorio.")
                if servicio_id:
                    return redirect("pago", reserva_id=reserva_id, servicio_id=servicio_id)
                else:
                    return redirect("pago_sin_servicio", reserva_id=reserva_id,id_habitacion=habitacion_id)
            elif not cvc.isdigit() or not (3 <= len(cvc) <= 4):
                messages.warning(request, "CVC inválido.")
                if servicio_id:
                    return redirect("pago", reserva_id=reserva_id, servicio_id=servicio_id)
                else:
                    return redirect("pago_sin_servicio", reserva_id=reserva_id,id_habitacion=habitacion_id)

            if not caducidad:
                messages.warning(request, "La fecha de caducidad es obligatoria.")
                if servicio_id:
                    return redirect("pago", reserva_id=reserva_id, servicio_id=servicio_id)
                else:
                    return redirect("pago_sin_servicio", reserva_id=reserva_id,id_habitacion=habitacion_id)
            
            reserva = Reserva.objects.get(pk=reserva_id)
            reserva.estado = "P"
        else:
            pass
                
        
        try:
            """ if not email or not telefono or not nombre:
                messages.error(request, "El los datos de Huesped son obligatorios.") """

            reserva = Reserva.objects.get(pk=reserva_id)
            if metodo__pago == "3":
                reserva.estado = "P"
            else:
                reserva.estado = "A"
            reserva.pago.metodo_pago=metodo__pago
            reserva.num_per = reserva.adultos + reserva.ninos
            reserva.save()

            detalles = f"""
                - Cliente: {reserva.cliente.nombre}
                - Habitación asignada por: {reserva.empleado.nombre}
                - Fecha de entrada: {reserva.fecha_inicio}
                - Fecha de salida: {reserva.fecha_fin}
                - Número de personas: {reserva.num_per}
                - Estado: {reserva.get_estado_display()}
                - metodo de pago: {reserva.pago.get_metodo_pago_display()}
                - Monto total: {precio_total}
                -con una peticion especial de: {peticion}"""
                

            enviar_correo_reserva(reserva.cliente.correo,reserva.cliente.nombre, detalles)
            request.session["datos_reserva"] = None
            request.session["data"] = None
            messages.success(request, "¡Pago confirmado y reserva realizada con éxito! se te ha enviado correo.")
            return redirect('agregar_reservas')

        except (Reserva.DoesNotExist, Habitacion.DoesNotExist) as e:
            messages.error(request, f"Error al confirmar el pago: {e}")
            return redirect('agregar_reservas')
    else:
        return redirect('reservas')

def cancelar_reserva(request,id_reserva):
    admin = request.session.get("admin", False)
    q = Reserva.objects.get(pk=id_reserva)
    if q.estado == "P":
        detalle = DetalleReserva.objects.filter(reserva=id_reserva)
        detalle.delete()
        q.estado = "C"
        q.save()

        detalles = f"""
        - Cliente: {q.cliente.nombre}
        - Habitación asignada por: {q.empleado.nombre}
        - Fecha de entrada: {q.fecha_inicio}
        - Fecha de salida: {q.fecha_fin}
        - Número de personas: {q.adultos + q.ninos}
        - Estado: {q.get_estado_display()}
        - Método de pago: {q.pago.get_metodo_pago_display()}
        - Monto total: {q.pago.monto_total}
        """

        # Envía el correo de reembolso/cancelación
        enviar_correo_reembolso(q.cliente.correo, q.cliente.nombre, detalles)

        messages.success(request,f"se le acaba de mandar un correo a {q.cliente.nombre} del reembolzo.")
        if admin:
            return redirect("Administrador")
            
        else:
            return redirect("agregar_reservas")
    else:
        q.estado = "C"
        q.save()
        messages.success(request,f"su reserva ha sido cancelada")
        if admin:
            return redirect("Administrador")
            
        else:
            return redirect("agregar_reservas")



def enviar_correo_reembolso(cliente_email, nombre_cliente, detalles_reserva):
    asunto = "Tu reserva ha sido cancelada y reembolsada"
    mensaje = f"""
    Hola {nombre_cliente},

    Te informamos que tu reserva ha sido cancelada y el monto correspondiente será reembolsado.

    Detalles de la reserva cancelada:
    {detalles_reserva}

    Si tienes alguna duda, por favor contáctanos.

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

def agregar_servicio(request):
    if request.method == "POST":
        request.session["data"] = request.POST


        nombre = request.POST.get("nombre")
        descripcion = request.POST.get("descripcion")
        precio = request.POST.get("precio")
        hora_inicio = request.POST.get("hora_inicio")
        hora_fin = request.POST.get("hora_fin")
        foto = request.FILES.get("foto")
        estado = "A" if request.POST.get("estado") == "on" else "I"

        if not nombre or not descripcion or not precio or not hora_inicio or not hora_fin:
            messages.error(request, "Por favor, completa todos los campos.")
            return redirect("agregar_servicio")
        
        if hora_inicio >= hora_fin:
            messages.error(request, "La hora de inicio debe ser menor que la hora de fin.")
            return redirect("agregar_servicio")


        if len(descripcion) > 250:
                messages.error(request, "La descripción no puede superar los 250 caracteres.")
                return redirect("agregar_servicio")
            
        if len(descripcion) <= 20:
            messages.error(request, "La descripción no puede ser menor o igual que 20 caracteres.")
            return redirect("agregar_servicio")

        if Servicio.objects.filter(nombre=nombre).exists():
                messages.error(request, "El Nombre de servicio ya está registrado. Usa otro.")  
                return redirect("agregar_servicio")

        if Servicio.objects.filter(nombre=descripcion).exists():
                messages.error(request, "La descripcion de servicio ya está registrada. Usa otra.")  
                return redirect("agregar_servicio")
        
        try:
            precio = float(precio)
            if precio < 0:
                messages.error(request, "El precio no puede ser negativo.")
                return redirect("agregar_servicio")
        except ValueError:
            messages.error(request, "El precio debe ser un número válido.")
            return redirect("agregar_servicio")

        try:
            o = Servicio(
                nombre=nombre,
                descripcion=descripcion,
                precio=precio,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                estado=estado
            )
            if foto:
                o.foto = foto
            o.save()
            request.session["data"] = None
            messages.success(request, "Servicio agregado correctamente.")
            return redirect("listar_servicios")
        except Exception as e:
            messages.error(request, f"Error al guardar el servicio: {e}")
            return redirect("agregar_servicio")
    else:
        request.session["data"] = None
        return render(request, "funcionalidades/servicio.html")




"""def pago(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    if request.method == "POST":
        monto_total = request.POST.get("monto_total")
        monto_total = float(monto_total)
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

            detalles = f
            - Cliente: {reserva.cliente.nombre}
            - Habitación asignada por: {reserva.empleado.nombre}
            - Fecha de entrada: {reserva.fecha_inicio}
            - Fecha de salida: {reserva.fecha_fin}
            - Número de personas: {reserva.num_per}
            - Estado: {reserva.get_estado_display()}
            - Monto total: {monto_total}
            - Método de pago: {q.get_metodo_pago_display()}  
            

            enviar_correo_reserva(reserva.cliente.correo,
                                  reserva.cliente.nombre, detalles)

            messages.success(
                request, "Pago realizado con éxito. Se ha enviado un correo de confirmación.")
            return redirect("Reservas")
        except Exception as e:
            messages.error(request, f"Error al procesar el pago: {e}")

    return render(request, 'funcionalidades/pago.html', {"reserva": reserva})
"""


def terminos(request):
    return render(request, "funcionalidades/terminos_condiciones.html")


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


def generate_random_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def Recuperar_clave(request):
    if request.method == "POST":
        correo = request.POST.get("email")
        try:
            usuario = Usuario.objects.get(correo=correo)
            messages.success(request,"Correo encontrado")
            
            code = generate_random_code()
            
            usuario.password = hash_password(code)
            usuario.save()
        except Usuario.DoesNotExist:
            messages.error(request, "El correo ingresado no está registrado.")
            return redirect("Recuperar_clave")
        
        enviar_correo_recuperar(usuario.correo,code)
        messages.success(request, "Se ha enviado un enlace de recuperación a tu correo.")
        return redirect("login")
    return render(request,"funcionalidades/recuperar_clave.html")   



def restablecer_contraseña(request, correo):
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
                messages.error(
                    request, "La contraseña debe ser mayor a 5 caracteres.")
            else:
                usuario.password = hash_password(nueva)
                usuario.save()
                messages.success(
                    request, "Tu contraseña ha sido restablecida con éxito.")
                return redirect("login")
        else:
            messages.error(request, "Las contraseñas no coinciden.")

    return render(request, "funcionalidades/cambiar_clave.html", {"correo": correo})


def enviar_correo_recuperar(cliente_email, code):
    asunto = "Recuperación de Contraseña - Hostería El Solecito"
    mensaje = f"""
    Hola {cliente_email},\n\nHas solicitado recuperar tu contraseña. ' \
                    Utiliza el siguiente código para restablecerla:\n\n' \
                    Contraseña: **{code}**\n\n' \
                    Este código expirará en 24 horas.\n\n' \
                    Si no has solicitado este cambio, puedes ignorar este correo.'
    """
    send_mail(
        asunto,
        mensaje,
        settings.EMAIL_HOST_USER,
        [cliente_email],
        fail_silently=False,
    )


def eliminar_empleados(request, id_empleado):
    q = Empleado.objects.get(pk=id_empleado)
    try:
        q.delete()
        messages.success(request, "Empleado eliminado correctamente!")
    except IntegrityError:
        messages.warning(
            request, "Error: No puede eliminar el empleado, está en uso.")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    return redirect("listar_empleados")

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
    return redirect("index")

def eliminar_servicio(request, id_servicio):
    try:
        q = Servicio.objects.get(pk=id_servicio)
        q.delete()
        messages.success(request, "Servicio eliminado correctamente!")
    except IntegrityError:
        messages.warning(
            request, "Error: No puede eliminar el servicio, está en uso.")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    return redirect("listar_servicios")


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
    
    usuario = get_object_or_404(Usuario, pk=id_usuario)
    try:
        Empleado.objects.filter(correo=usuario.correo).delete()
        if usuario.activo:
            messages.warning(
                request,
                "No se puede eliminar un usuario que está logueado actualmente."
            )
        else:
            usuario.delete()
            messages.success(request, "Usuario eliminado correctamente!")

    except IntegrityError:
        messages.warning(
            request,
            "Error: No puede eliminar el usuario porque está en uso en otras referencias."
        )
    except Exception as e:
        messages.error(request, f"Error al eliminar el usuario: {e}")

    return redirect("listar_clientes")

def eliminar_empleado(request, id_empleado):
    
    usuario = get_object_or_404(Usuario, pk=id_empleado)
    try:
        Empleado.objects.filter(correo=Empleado.correo).delete()
        if Empleado.activo:
            messages.warning(
                request,
                "No se puede eliminar un empleado que está logueado actualmente."
            )
        else:
            Empleado.delete()
            messages.success(request, "Empleado eliminado correctamente!")

    except IntegrityError:
        messages.warning(
            request,
            "Error: No puede eliminar el empleado porque está en uso en otras referencias."
        )
    except Exception as e:
        messages.error(request, f"Error al eliminar el empleado: {e}")

    return redirect("listar_empleados")



def editar_reserva(request, id_reserva, id_habitacion=None):
    # Importación necesaria si no está al principio del archivo
    import random
    from datetime import date, datetime
    
    # Obtener objetos necesarios
    reserva = get_object_or_404(Reserva, pk=id_reserva)
    servicios = Servicio.objects.all()
    clientes = Usuario.objects.filter(rol=3)
    empleados = Empleado.objects.all()
    pagos = Pago.objects.all()
    todas_habitaciones = Habitacion.objects.all()
    reservas = Reserva.objects.exclude(pk=reserva.id)  # Excluye la reserva actual
    
    # Configuración de la sesión
    request.session["datos"] = "editando"
    
    # Contexto base para los renders
    contexto_base = {
        "servicios": servicios,
        "clientes": clientes,
        "empleados": empleados,
        "pagos": pagos,
        "datos": reserva,
    }
    
    if request.method == "POST":
        try:
            # Obtener y validar datos del formulario
            request.session["data"] = request.POST
            fechas = request.POST.get("fechas")
            servicio_id = request.POST.get("servicio_id", None)
            cliente_id = request.POST.get("cliente")
            
            # Validar fechas
            if not fechas or "a" not in fechas:
                messages.info(request, "Debes seleccionar una fecha de entrada y salida.")
                return redirect("editar_reserva", id_reserva=id_reserva)
                
            # Validar cantidad
            try:
                cantidad = int(request.POST.get("cantidad", 0))
                if cantidad < 1:
                    messages.info(request, "Debes seleccionar mínimo 1 habitación.")
                    return render(request, 'Reservas.html', contexto_base)
                elif cantidad > 5:
                    messages.info(request, "No puedes seleccionar más de 5 habitaciones.")
                    return render(request, 'Reservas.html', contexto_base)
            except ValueError:
                messages.error(request, "Cantidad de habitaciones inválida.")
                return render(request, 'Reservas.html', contexto_base)
                
            # Validar adultos
            try:
                adultos = int(request.POST.get('adultos', 0))
                if adultos < 1:
                    messages.info(request, "Debe haber al menos un adulto por habitación.")
                    return render(request, 'Reservas.html', contexto_base)
                elif adultos > 20:
                    messages.info(request, "Excedió el máximo de capacidad por reserva.")
                    return render(request, 'Reservas.html', contexto_base)
            except ValueError:
                messages.error(request, "Número de adultos inválido.")
                return render(request, 'Reservas.html', contexto_base)
                
            # Validar niños
            try:
                ninos = int(request.POST.get('ninos', 0))
                if ninos < 0:
                    messages.error(request, "El número de niños no puede ser negativo.")
                    return render(request, 'Reservas.html', contexto_base)
                elif ninos > 30:
                    messages.info(request, "Excedió el máximo de capacidad por reserva.")
                    return render(request, 'Reservas.html', contexto_base)
            except ValueError:
                messages.error(request, "Número de niños inválido.")
                return render(request, 'Reservas.html', contexto_base)
                
            # Validar proporción adultos/niños
            adult_e = adultos * 2
            if ninos > adult_e:
                messages.info(request, "Cada adulto puede llevar máximo 2 niños.")
                return render(request, 'Reservas.html', contexto_base)
                
            # Validar adultos por habitación
            if adultos < cantidad:
                messages.info(request, "Debe haber un adulto por habitación como mínimo.")
                return render(request, 'Reservas.html', contexto_base)
                
            # Procesar fechas
            try:
                fecha_entrada_str, fecha_salida_str = fechas.split(" a ")
                fecha_entrada = datetime.strptime(fecha_entrada_str.strip(), "%Y-%m-%d").date()
                fecha_salida = datetime.strptime(fecha_salida_str.strip(), "%Y-%m-%d").date()
                
                ahora = date.today()
                
                if fecha_entrada >= fecha_salida:
                    messages.error(request, "La fecha de salida debe ser después de la fecha de entrada.")
                    return render(request, 'Reservas.html', contexto_base)
                
                if fecha_entrada < ahora or fecha_salida < ahora:
                    messages.error(request, "Las fechas deben ser posteriores a hoy.")
                    return render(request, 'Reservas.html', contexto_base)
            except ValueError:
                messages.error(request, "Formato de fechas inválido.")
                return render(request, 'Reservas.html', contexto_base)
                
            # Verificar existencia del cliente
            try:
                cliente = Usuario.objects.get(pk=cliente_id)
            except Usuario.DoesNotExist:
                messages.error(request, "El cliente seleccionado no existe.")
                return render(request, 'Reservas.html', contexto_base)
                
            # Seleccionar un empleado aleatorio
            empleados_disponibles = Empleado.objects.all()
            if not empleados_disponibles:
                messages.error(request, "No hay empleados disponibles.")
                return render(request, 'Reservas.html', contexto_base)
            empleado = random.choice(empleados_disponibles)
            
            # Verificar disponibilidad de habitaciones
            ocupadas_ids = []
            disponibles_ids = [habitacion.id for habitacion in todas_habitaciones]

            for reserva_item in reservas:
                fecha_inicio_reserva = reserva_item.fecha_inicio
                fecha_fin_reserva = reserva_item.fecha_fin
                
                if not disponible(fecha_entrada, fecha_salida, fecha_inicio_reserva, fecha_fin_reserva):
                    detalles = DetalleReserva.objects.filter(reserva=reserva_item)
                    
                    for detalle in detalles:
                        habitacion_id = detalle.habitacion.id
                        if habitacion_id in disponibles_ids:
                            disponibles_ids.remove(habitacion_id)
                            if habitacion_id not in ocupadas_ids:
                                ocupadas_ids.append(habitacion_id)

            habitaciones_ocupadas = Habitacion.objects.filter(id__in=ocupadas_ids)
            habitaciones_disponibles = Habitacion.objects.filter(id__in=disponibles_ids)
            
            # Guardar en la sesión
            request.session['datos_reserva'] = {
                'cantidad': cantidad,
                'disponibles': [habitacion.to_dict() for habitacion in habitaciones_disponibles],
                'ocupadas': [habitacion.to_dict() for habitacion in habitaciones_ocupadas]
            }     

            # Actualizar la reserva
            reserva.cliente = cliente
            reserva.empleado = empleado
            reserva.fecha_inicio = fecha_entrada
            reserva.fecha_fin = fecha_salida
            reserva.adultos = adultos
            reserva.ninos = ninos
            reserva.estado = "I"
            reserva.save()

            # Redireccionar según corresponda
            if servicio_id:
                return redirect('Reservas2', reserva_id=id_reserva, servicio_id=servicio_id)
            else:
                return redirect('Reservas2_sin_servicio', reserva_id=id_reserva)
                
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return render(request, 'Reservas.html', contexto_base)
    
    else:  # GET request
        detal = DetalleReserva.objects.filter(reserva=reserva)
        total = sum((detalle.cantidad or 1) for detalle in detal)   
        reserva.total_habitaciones = total
        fechas = f"{reserva.fecha_inicio.strftime('%Y-%m-%d')} a {reserva.fecha_fin.strftime('%Y-%m-%d')}"
        
        # Actualizar contexto para GET
        contexto = contexto_base.copy()
        contexto.update({
            "servi": detal,
            "dat_fechas": fechas,
            "total_habitaciones": reserva.total_habitaciones,
        })
        
        return render(request, "Reservas.html", contexto)
def detalles(request,reserva_id,id_habitacion = None,servicio_id= None):
    
    reserva = Reserva.objects.get(pk=reserva_id)
    dias = (reserva.fecha_fin - reserva.fecha_inicio).days
    datos_reserva = request.session.get('datos_reserva', {})
    cantidad = int(datos_reserva.get('cantidad', 1))
    seleccionadas = datos_reserva.get('h_seleccionadas', [])
    num_per = reserva.ninos + reserva.adultos
    DetalleReserva.objects.filter(reserva=reserva).delete()
    
    if cantidad > 1:
        cap_m = 0
        for habitacion in seleccionadas:
            habitacion = Habitacion.objects.filter(id=habitacion.get('id'))
            for habita in habitacion:
                cap_m += habita.capacidad
        cap_m += 4
        if cap_m < num_per:
            messages.info(request, "pasa la capacidad maxima de las habitaciones.")
            if servicio_id:
                return redirect("Reservas2",reserva_id=reserva_id,servicio_id=servicio_id)
            else:
                return redirect("Reservas2_sin_servicio",reserva_id=reserva_id)
    else:
        habitacion = Habitacion.objects.get(pk=id_habitacion)
        if habitacion.capacidad < num_per:
            messages.info(request, "pasa la capacidad maxima de la habitacion.")
            if servicio_id:
                return redirect("Reservas2",reserva_id=reserva_id,servicio_id=servicio_id)
            else:
                return redirect("Reservas2_sin_servicio",reserva_id=reserva_id)

    precio_total = 0
    if cantidad > 1:
        habitaciones = []
        for habi in seleccionadas:
            habitacion = Habitacion.objects.get(pk=habi['id'])
            dias = (reserva.fecha_fin - reserva.fecha_inicio).days
            precio_habi = habitacion.precio * dias
            precio_total += precio_habi
            habitaciones.append(habitacion)
            
        if servicio_id:
            try:
                servicio = Servicio.objects.get(id=servicio_id)
                precio_total += float(servicio.precio)
            except Servicio.DoesNotExist:
                servicio = None
        else:
            servicio = None
            
        # Crear detalle para múltiples habitaciones
        for habitacion in habitaciones:
            if servicio_id:
                DetalleReserva.objects.create(
                    habitacion=habitacion,
                    reserva=reserva,
                    cantidad=1,
                    precio_neto=habitacion.precio * dias,
                    servicio=servicio,
                )
            else:
                DetalleReserva.objects.create(
                    habitacion=habitacion,
                    reserva=reserva,
                    cantidad=1,
                    precio_neto=habitacion.precio * dias,
                )
    else:
        # Código para una sola habitación
        habitacion = Habitacion.objects.get(pk=id_habitacion)
        dias = (reserva.fecha_fin - reserva.fecha_inicio).days
        precio_habi = habitacion.precio * dias
        precio_total = precio_habi

        if servicio_id:
            try:
                servicio = Servicio.objects.get(id=servicio_id)
                precio_total += float(servicio.precio)
            except Servicio.DoesNotExist:
                servicio = None
        else:
            servicio = None
            
        # Crear detalle para una sola habitación
        if servicio_id:
            servicio = Servicio.objects.get(pk=servicio_id)
            detalle_reserva = DetalleReserva(
                habitacion=habitacion,
                reserva=reserva,
                cantidad=1,
                precio_neto=precio_total,
                servicio=servicio
            )
        else:
            detalle_reserva = DetalleReserva(
                habitacion=habitacion,
                reserva=reserva,
                cantidad=1,
                precio_neto=precio_total,
            )
        detalle_reserva.save()
    
    return redirect("index")
    
def agregar_usuario(request):
    if request.method == "POST":
        request.session["data"] = request.POST

        nombre = request.POST.get("nombre")
        correo = request.POST.get("correo")
        password = request.POST.get("password")
        tipo_documento = request.POST.get("tipo_documento")
        documento = request.POST.get("documento")
        foto = request.FILES.get("foto")
        telefono = request.POST.get("telefono")
        rol = int(request.POST.get("rol", 2)) 
        direccion = request.POST.get("direccion")

        confirm_password = request.POST.get("confirm_password")

        if not nombre or not correo or not tipo_documento or not documento or not telefono or not direccion or not password or not confirm_password :
                messages.error(request, "Por favor, completa todos los campos.")
                return redirect("editar_registro")
        
        if "@" not in correo or ".com" not in correo:
            messages.error(
                request, "El correo debe contener '@' y terminar en '.com'")
            return render(request, "Register.html")
        elif Usuario.objects.filter(nombre=nombre).exists():
            messages.error(
                request, "El Nombre de usuario ya está registrado. Usa otro.")  
            return render(request, "Register.html")
        elif Usuario.objects.filter(correo__iexact=correo).exists():
            messages.error(request, "El coreo ya está registrado. Usa otro.")
            return render(request, "Register.html")
            
        elif len(password) < 5:
            messages.error(
                request, "La contraseña debe ser mayor a 5 caracteres")
            return render(request, "Register.html")

        try:
            if password == confirm_password:
                q = Usuario(
                    nombre=nombre,
                    correo=correo,
                    tipo_documento=tipo_documento,
                    documento=int(documento),
                    telefono=int(telefono),
                    rol=rol,
                    direccion=direccion,
                    password=hash_password(password),

                )
                if foto:
                    q.foto = foto
                q.save()
                messages.success(request, "Usuario agregado correctamente!")
                verificar = request.session.get("auth", False)
                if verificar:
                    return redirect("listar_clientes")
                else:
                    return redirect("login")
            else:
                messages.error(request, "Las contraseñas no coinciden")
                return render(request, "Register.html")
        except ValueError:
            messages.error(request, "Los tipos de datos son incorrectos.")
            return render(request, "Register.html")
        except Exception as e:
            messages.error(request, f"Error: {e}")
            return render(request, "Register.html")
    else:
        request.session["data"] = None
        return render(request, "Register.html")

def usuarios(request):
    q = Usuario.objects.all()
    contexto = {
        "data": q
    }
    return render(request, "index.html", contexto)


def editar_registro(request, id_usuario):
    if request.method == "POST":
        request.session["data"] = request.POST
        try:
            q = Usuario.objects.get(pk=id_usuario)

            nombre = request.POST.get("nombre")
            correo = request.POST.get("correo")
            tipo_documento = request.POST.get("tipo_documento")
            documento = request.POST.get("documento")
            telefono = request.POST.get("telefono")
            direccion = request.POST.get("direccion")
            rol = request.POST.get("rol")
            foto = request.FILES.get("foto")

            if not nombre or not correo or not tipo_documento or not documento or not telefono or not direccion:
                messages.error(request, "Por favor, completa todos los campos.")
                return redirect("editar_registro", id_usuario=id_usuario)

            if "@" not in correo or ".com" not in correo:
                messages.error(request, "El correo debe contener '@' y terminar en '.com'")
                return redirect("editar_registro", id_usuario=id_usuario)
      
            
            q.nombre = nombre
            q.correo = correo
            q.tipo_documento = tipo_documento
            q.documento = documento
            q.telefono = telefono
            q.direccion = direccion
            q.rol = rol
            if foto:
                q.foto = foto  

            q.save()  
            messages.success(request, "Usuario actualizado correctamente!")
            return redirect("listar_clientes")

        except Exception as e:
            print("Error al editar usuario:", e)
            messages.error(request, f"Error al editar usuario: {e}")
            return redirect("editar_registro", id_usuario=id_usuario)

    else:
        q = Usuario.objects.get(pk=id_usuario)
        c = Usuario.objects.filter(rol=2)
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



def editar_habitacion(request, id_habitacion):
    if request.method == "POST":
        request.session["data"] = request.POST

        
        try:
            q = Habitacion.objects.get(pk=id_habitacion)

            nombre = request.POST.get("nombre")
            descripcion = request.POST.get("descripcion")
            capacidad = request.POST.get("capacidad")
            precio = request.POST.get("precio")
            estado = request.POST.get("estado")
            foto = request.FILES.get("foto") or q.foto


            if not nombre or not descripcion or not capacidad or not precio or not estado:
                messages.error(request, "Por favor, completa todos los campos.")
                return redirect("editar_habitacion", id_habitacion=id_habitacion)

            if len(descripcion) > 250:
                messages.error(request, "La descripción no puede superar los 250 caracteres.")
                return redirect("editar_habitacion", id_habitacion=id_habitacion)

            try:
                capacidad = int(capacidad)
                precio = float(precio)
                if capacidad <= 0 or precio < 0:
                    messages.error(request, "La capacidad debe ser mayor a 0 y el precio no puede ser negativo.")
                    return redirect("editar_habitacion", id_habitacion=id_habitacion)
            except ValueError:
                messages.error(request, "Capacidad y precio deben ser valores numéricos válidos.")
                return redirect("editar_habitacion", id_habitacion=id_habitacion)

            q.nombre = nombre
            q.descripcion = descripcion
            q.capacidad = capacidad
            q.precio = precio
            q.foto = foto
            q.estado = estado

            q.save()
            messages.success(request, "Habitación actualizada correctamente!")
            return redirect("listar_habitaciones")
        except Exception as e:
            messages.error(request, f"Error al actualizar la habitación: {e}")
            return redirect("editar_habitacion", id_habitacion=id_habitacion)
    else:
        q = Habitacion.objects.get(pk=id_habitacion)
        contexto = {
            "datos": q
        }
        return render(request, "funcionalidades/habitacion.html", contexto)

    

def agregar_habitacion(request):
    if request.method == "POST":
        request.session["data"] = request.POST

        nombre = request.POST.get("nombre")
        descripcion = request.POST.get("descripcion")
        capacidad = request.POST.get("capacidad")
        precio = request.POST.get("precio")
        foto = request.FILES.get("foto")
        estado = request.POST.get("estado")

        if not nombre or not descripcion or not capacidad or not precio or not estado:
            messages.error(request, "Por favor, completa todos los campos.")
            return redirect("agregar_habitacion")
        
        if len(descripcion) > 250:
            messages.error(request, "La descripción no puede superar los 250 caracteres.")
            return redirect("agregar_habitacion")

        try:
            capacidad = int(capacidad)
            precio = float(precio)
            if capacidad <= 0 or precio < 0:
                messages.error(request, "La capacidad debe ser mayor a 0 y el precio no puede ser negativo.")
                return redirect("agregar_habitacion")
        except ValueError:
            messages.error(request, "Capacidad y precio deben ser valores numéricos válidos.")
            return redirect("agregar_habitacion")
        
        try:

            q = Habitacion(
                nombre=nombre,
                descripcion=descripcion,
                capacidad=int(capacidad),
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
        request.session["data"] = None
        return render(request, "funcionalidades/habitacion.html")


def Register(request):
    return render(request, 'Register.html')


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
                        messages.error(
                            request, "La contraseña debe ser mayos a 5 caracteres")
                    else:
                        q.password = hash_password(nueva)       # utils.py
                        q.save()
                        messages.success(
                            request, "Contraseña cambiada con éxito!!")
                        return redirect("index")
                else:
                    messages.info(
                        request, "Contraseñas nuevas no coinciden...")
            else:
                messages.warning(
                    request, "para cambiar las contraseña debe ser diferente")
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

