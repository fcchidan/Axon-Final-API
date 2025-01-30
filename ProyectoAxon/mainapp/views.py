from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from blog.models import Categoria, Producto, ElementoCarrito, Orden, DireccionEnvio, ElementoOrden, Pedido, DetalleProducto
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.forms import UserCreationForm
from mainapp.forms import RegisterForm, DireccionEnvioForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.conf import settings
from django.template.loader import render_to_string, get_template
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives, send_mail, EmailMessage
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .forms import PasswordResetForm, SetPasswordForm
from django.http import HttpResponse
import json 
# API Obuma
import random
import requests
from django.http import JsonResponse
OBUMA_API_KEY = "37bc03e39bdebcb7db9160d6e89474c3"  
OBUMA_URL = 'https://api.obuma.cl/v1.0'
import requests_cache

# Configura el caché al inicio
requests_cache.install_cache(
    cache_name='obuma_cache',
    backend='sqlite',
    expire_after=1800  # 30 minutos
)

from collections import Counter
import unicodedata



# Diccionario en memoria para registrar las búsquedas
productos_buscados = Counter()


# Create your views here.
def index(request):
    return render(request, 'index.html')


def productos(request):
    
    productos = Producto.objects.all()
    paginator = Paginator(productos, 5)
    
    page = request.GET.get('page')
    page_productos = paginator.get_page(page)
    
    
    return render(request, 'productos.html',{
        'productos': page_productos
    })

def clientes(request):
    return render(request, 'clientes.html')

def contacto(request):
    return render(request, 'contacto.html')

def empresa(request):
    return render(request, 'empresa.html')

def representacion(request):
    return render(request, 'representacion.html')

def servicios(request):
    return render(request, 'servicios.html')

"""
def categoria(request, categoria_id):
    categoria = Categoria.objects.get(id=categoria_id)
    productos_list = Producto.objects.filter(categorias=categoria_id)
    
    paginator = Paginator(productos_list, 10)  # Paginar los productos, mostrando 10 por página
    page_number = request.GET.get('page')  # Obtener el número de página solicitado
    productos = paginator.get_page(page_number)  # Obtener los productos para la página solicitada
    
    return render(request, 'categorias.html', {
        'categoria': categoria,
        'productos': productos
    })   

def producto(request, producto_id):
    
    producto = Producto.objects.get(id=producto_id)
    
    return render(request, 'producto.html',{
        'producto' : producto
    })

"""


    

def register_page(request):

    registro_form = RegisterForm()

    if request.method == 'POST':
        registro_form = RegisterForm(request.POST)

        if registro_form.is_valid():
            registro_form.save()
            messages.success(request, 'Te has registrado correctamente!!')

            return redirect('inicio')

    return render(request, 'registro.html',{
        'title': 'Registro',
        'registro_form': registro_form
    })


def login_page(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    else:

        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('inicio')
            else:
                messages.warning(request, 'No te has podido identificado correctamente')

        return render(request, 'login.html',{
            'title': 'Acceso'
        })

def logout_user(request):
    logout(request)
    return redirect('login')

#Recuperar contraseña
def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            request.session['email'] = form.cleaned_data['email']
            return redirect('set_new_password')
    else:
        form = PasswordResetForm()
    return render(request, 'password_reset_request.html', {'form': form})

def set_new_password(request):
    if 'email' not in request.session:
        return redirect('password_reset_request')

    if request.method == "POST":
        form = SetPasswordForm(request.POST)
        if form.is_valid():
            email = request.session['email']
            user = User.objects.get(email=email)
            user.password = make_password(form.cleaned_data['new_password1'])
            user.save()
            del request.session['email']
            return redirect('login')
    else:
        form = SetPasswordForm()
    return render(request, 'set_new_password.html', {'form': form})
# aqui empieza las funciones de la base de datos&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&z
"""
@login_required
def ver_carrito(request):
    elementos_carrito = ElementoCarrito.objects.filter(usuario=request.user)
    total_carrito = sum(item.subtotal() for item in elementos_carrito)
    total_productos_carrito = sum(item.cantidad for item in elementos_carrito)
    cantidad_productos_carrito = elementos_carrito.count()
    return render(request, 'carrito.html', {'elementos_carrito': elementos_carrito, 'total_carrito': total_carrito, 'cantidad_productos_carrito': cantidad_productos_carrito, 'total_productos_carrito': total_productos_carrito})

@login_required
def agregar_al_carrito(request, producto_id):
    producto = Producto.objects.get(pk=producto_id)
    elemento, created = ElementoCarrito.objects.get_or_create(usuario=request.user, producto=producto)
    if not created:
        elemento.cantidad += 1
        elemento.save()
    return redirect(request.META.get('HTTP_REFERER','ver_carrito'))

    
@login_required
def eliminar_del_carrito(request, elemento_id):
    elemento = ElementoCarrito.objects.get(pk=elemento_id)
    if elemento.usuario == request.user:
        elemento.delete()
    return redirect('ver_carrito')

@login_required
def vaciar_carrito(request):
    ElementoCarrito.objects.filter(usuario=request.user).delete()
    return redirect('ver_carrito')

@login_required
def realizar_orden(request):
    if request.method == 'POST':
        form = DireccionEnvioForm(request.POST)
        if form.is_valid():
            direccion_envio = form.save()  # Guardar la dirección de envío

            # Calcular el precio total de los elementos en el carrito
            elementos_carrito = ElementoCarrito.objects.filter(usuario=request.user)
            precio_total = sum(elemento.subtotal() for elemento in elementos_carrito)
            
            # Crear la orden y asignar el precio total y la dirección de envío
            orden = Orden.objects.create(
                usuario=request.user,
                precio_total=precio_total,
                direccion_envio=direccion_envio
            )
            
            # Crear los elementos de la orden basados en el carrito
            for elemento in elementos_carrito:
                ElementoOrden.objects.create(
                    orden=orden,
                    producto=elemento.producto,
                    cantidad=elemento.cantidad
                )
            
            # Limpiar el carrito después de realizar la orden
            elementos_carrito.delete()
            
            #return redirect('ver_carrito')
            # Redirigir a la página de éxito con los detalles de la orden
            return redirect('pagina_exito', orden_id=orden.id)
    else:
        form = DireccionEnvioForm()
    
    return render(request, 'ingresar_direccion_envio.html', {'form': form})

@login_required
def pagina_exito(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id)
    elementos = orden.elementoorden_set.all()
    context = {
        'orden': orden,
        'elementos': elementos
    }
    return render(request, 'exito.html', context)

def aumentar_cantidad(request, elemento_id):
    elemento = get_object_or_404(ElementoCarrito, pk=elemento_id)
    elemento.cantidad += 1  # Aumentar la cantidad en 1
    elemento.save()
    return redirect('ver_carrito')

def disminuir_cantidad(request, elemento_id):
    elemento = get_object_or_404(ElementoCarrito, pk=elemento_id)
    if elemento.cantidad > 1:  # Verificar si la cantidad es mayor que 1 para evitar cantidades negativas
        elemento.cantidad -= 1  # Disminuir la cantidad en 1
        elemento.save()
    return redirect('ver_carrito')


def ingresar_direccion_envio(request):
    if request.method == 'POST':
        direccion = request.POST.get('direccion')
        ciudad = request.POST.get('ciudad')
        codigo_postal = request.POST.get('codigo_postal')
        # Aquí puedes hacer la validación de los datos ingresados
        DireccionEnvio.objects.create(
            direccion=direccion,
            ciudad=ciudad,
            codigo_postal=codigo_postal
        )
        # Redirigir a la página de generar orden
        return redirect('realizar_orden')
    return render(request, 'ingresar_direccion_envio.html')


#Enviar correo al hacer una orden
@receiver(post_save, sender=Orden)
def enviar_correo_orden(sender, instance, created, **kwargs):
    if created:
        subject = 'Nueva orden generada'
        elementos = instance.elementoorden_set.all()
        
        context = {
            'orden': instance,
            'elementos': elementos
        }
        
        template = get_template('correo_orden.html')
        content = template.render(context)
        
        email = EmailMultiAlternatives(
            subject,
            content,
            settings.EMAIL_HOST_USER,
            ['ventas@axoningenieria.cl']  # Cambiar el correo destinatario
        )
        email.attach_alternative(content, 'text/html')
        email.send()


#guarda los productos del carito en la orden       

def completar_pedido(request):
    # Obtener el carrito del usuario
    carrito_usuario = ElementoCarrito.objects.filter(usuario=request.user)
    
    # Verificar si el carrito está vacío
    if not carrito_usuario.exists():
        return redirect('carrito')

    # Crear una nueva instancia de Orden
    nueva_orden = Orden(usuario=request.user)
    nueva_orden.save()

    # Transferir los productos del carrito a la orden
    for elemento_carrito in carrito_usuario:
        nuevo_elemento_orden = ElementoOrden(
            orden=nueva_orden,
            producto=elemento_carrito.producto,
            cantidad=elemento_carrito.cantidad
        )
        nuevo_elemento_orden.save()

        # Eliminar los elementos del carrito una vez transferidos a la orden
        elemento_carrito.delete()

    # Calcular el precio total y guardarlo en la orden
    nueva_orden.precio_total = sum(item.subtotal() for item in nueva_orden.elementoorden_set.all())
    nueva_orden.save()

    # Redirigir o mostrar una página de confirmación de pedido
    return render(request, 'completar_pedido.html', {'orden': nueva_orden})

"""
#Correo de contacto
def contacto(request):
    if request.method == "POST":
        try:
            name = request.POST['name']
            email = request.POST['email']
            subject = request.POST['subject']
            message = request.POST['message']
            
            template = render_to_string('correo_contacto.html', {
                'name': name,
                'email': email,
                'message': message
            })
            
            email_message = EmailMessage(
                subject,
                template,
                settings.EMAIL_HOST_USER,
                ['contacto@axoningenieria.cl']
            )
            
            email_message.fail_silently = False
            email_message.send()
            
            messages.success(request, 'Se ha enviado tu correo.')
        except Exception as e:
            messages.error(request, f'Error al enviar el correo: {e}')
        return redirect('contacto')
    else:
        return render(request, 'contacto.html')
    
    
#Botón de busqueda
"""
def buscar_productos(request):
    query = request.GET.get('q')
    mensaje = None
    ultimos_productos = Producto.objects.order_by('-creado')[:5]
    
    if query:
        resultados = Producto.objects.filter(titulo__icontains=query)
        if resultados.exists():
            # Redirigir a la página de resultados
            return redirect(reverse('resultados_busqueda') + f'?q={query}')
        else:
            mensaje = f"No se encontraron resultados para '{query}'."
    else:
        resultados = Producto.objects.none()  # Para asegurar que resultados está definido
    
    return render(request, 'index.html', {
        'query': query,
        'mensaje': mensaje,
        'ultimos_productos': ultimos_productos
    })
    
def resultados_busqueda(request):
    query = request.GET.get('q')
    resultados = Producto.objects.filter(titulo__icontains=query)
    
    # Número de productos por página
    productos_por_pagina = 15
    
    # Aplicar paginación
    paginator = Paginator(resultados, productos_por_pagina)
    
    page_number = request.GET.get('page')
    try:
        resultados_pagina = paginator.page(page_number)
    except PageNotAnInteger:
        # Si el parámetro de página no es un entero, mostrar la primera página
        resultados_pagina = paginator.page(1)
    except EmptyPage:
        # Si la página está fuera de rango, mostrar la última página de resultados
        resultados_pagina = paginator.page(paginator.num_pages)
    
    return render(request, 'resultados_busqueda.html', {
        'query': query,
        'resultados_pagina': resultados_pagina,
        'resultados': resultados  # Pasar los resultados a la plantilla
    })
"""
"""
#trae los productos desde la base de datos
def producto_detalle(request, producto_id):
    producto = Producto.objects.get(pk=producto_id)
    return render(request, 'producto.html', {'producto': producto})
"""


#carrusel productos
"""
def inicio(request):
    ultimos_productos = Producto.objects.order_by('-creado')[:5]
    return render(request, 'index.html', {'ultimos_productos': ultimos_productos})

def ultimos_productos(request):
    ultimos_productos = Producto.objects.order_by('-creado')[:5]
    return render(request, 'index.html', {'ultimos_productos': ultimos_productos})
"""
@receiver(post_save, sender=Orden)
def set_user_info(sender, instance, created, **kwargs):
    if created:
        user = instance.usuario
        instance.nombre_usuario = f"{user.first_name} {user.last_name}"
        instance.save()


# API Obuma //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#API Obuma /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def producto_stock(request, producto_id):
    headers = {
        'Content-Type': 'application/json',
        'access-token': OBUMA_API_KEY,
    }
    try:
        # Construcción de la URL
        url = f"{OBUMA_URL}/productosStock.findById.json/{producto_id}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            stock_data = response.json()
            if isinstance(stock_data, dict) and 'data' in stock_data:
                # Retorna un JSON con el stock
                return {'stock': stock_data['data'], 'producto_id': producto_id}
            else:
                return {'error': 'Respuesta de la API en formato inesperado.'}
        elif response.status_code == 429:  # Límite excedido
            return {'error': 'Se ha superado el límite de consultas diarias a la API.'}
        else:
            return {'error': f'Error en la API: {response.status_code}'}
    except requests.exceptions.RequestException as e:
        return {'error': f'Error de conexión: {str(e)}'}


#--------------------------------------------------------------productos-----------------------------------------


def producto(request, producto_id):
    # Obtener el detalle del producto desde la API
    producto = obtener_detalle_producto(producto_id)

    # Manejo de errores
    if 'error' in producto:
        return JsonResponse({'error': producto['error']})

    # Renderiza los detalles del producto en el template
    return render(request, 'detalle_producto.html', {'producto': producto})


def obtener_productos():
    headers = {
        'content-type': 'application/json',
        'access-token': OBUMA_API_KEY,
    }

    try:
        # Obtener todos los productos
        productos_response = requests.get(f"{OBUMA_URL}/productos.list.json", headers=headers)
        if productos_response.status_code != 200:
            return {'error': f'Error al obtener productos: {productos_response.status_code}'}

        # Obtener todas las categorías
        categorias_response = requests.get(f"{OBUMA_URL}/productosCategorias.list.json", headers=headers)
        if categorias_response.status_code != 200:
            return {'error': f'Error al obtener categorías: {categorias_response.status_code}'}

        # Extraer datos de las respuestas
        productos = productos_response.json().get('data', [])
        categorias = categorias_response.json().get('data', [])

        # Crear un diccionario para mapear el id de categoría a su nombre
        categorias_dict = {categoria['producto_categoria_id']: categoria['producto_categoria_nombre'] for categoria in categorias}

        # Añadir el nombre de la categoría a los productos
        for producto in productos:
            producto['categoria_nombre'] = categorias_dict.get(producto.get('producto_categoria'), 'Desconocida')

        return {'data': productos}
    
    except requests.exceptions.RequestException as e:
        return {'error': f'Error en la solicitud: {str(e)}'}




def listar_productos(request):
    productos = obtener_productos()
    
    # Manejo de errores en la obtención de productos
    if 'error' in productos:
        return JsonResponse({'error': productos['error']})

    # Verifica si la clave 'data' existe y no está vacía para los productos
    if 'data' in productos and productos['data']:
        lista_productos = productos.get('data', [])
    else:
        return JsonResponse({'error': 'No se encontró la lista de productos'})

    # Renderizar la lista de productos en el template
    return render(request, 'lista_productos.html', {
        'productos': lista_productos,
    })




def obtener_detalle_producto(producto_id):
    headers = {
        'content-type': 'application/json',
        'access-token': OBUMA_API_KEY,
    }
    
    try:
        # Obtener el detalle del producto específico
        response = requests.get(f"{OBUMA_URL}/productos.list.json?id={producto_id}", headers=headers)

        print(f"Estado de la respuesta: {response.status_code}")  # Para depurar
        print(f"Contenido de la respuesta: {response.text}")      # Para depurar

        if response.status_code == 200:
            productos = response.json()
            if 'data' in productos and len(productos['data']) > 0:
                producto = productos['data'][0]  # Suponiendo que la API devuelve un array de productos
                producto['producto_id'] = producto_id  # Agregar ID del producto si es necesario

                # Obtener todos los fabricantes para poder mostrar el nombre
                fabricantes_response = obtener_fabricantes()
                if 'error' in fabricantes_response:
                    return {'error': fabricantes_response['error']}
                fabricantes = fabricantes_response.get('data', [])

                # Crear un diccionario de fabricantes
                fabricantes_dict = {fabricante['producto_fabricante_id']: fabricante['producto_fabricante_nombre'] for fabricante in fabricantes}

                # Añadir el nombre del fabricante al producto
                producto['fabricante_nombre'] = fabricantes_dict.get(producto.get('producto_fabricante'), 'Desconocido')

                # Obtener todas las categorías para poder mostrar el nombre
                categorias_response = requests.get(f"{OBUMA_URL}/productosCategorias.list.json", headers=headers)
                if categorias_response.status_code != 200:
                    return {'error': f'Error al obtener categorías: {categorias_response.status_code}'}

                categorias = categorias_response.json().get('data', [])
                
                # Crear un diccionario de categorías
                categorias_dict = {categoria['producto_categoria_id']: categoria['producto_categoria_nombre'] for categoria in categorias}

                # Añadir el nombre de la categoría al producto
                producto['categoria_nombre'] = categorias_dict.get(producto.get('producto_categoria'), 'Desconocida')

                return producto
                
            else:
                return {'error': 'Producto no encontrado en la respuesta de la API'}
        else:
            return {'error': f"Error en la solicitud: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {'error': f"Error en la solicitud: {str(e)}"}

"""
1- este era el original:

def producto_detalle(request, producto_id):
    print(f"Buscando detalles para el producto_id: {producto_id}")  # Para depuración
    producto = obtener_detalle_producto(producto_id)

    # Manejo de errores
    if 'error' in producto:
        return JsonResponse({'error': producto['error']}, status=404)

    # Renderizar la plantilla con el detalle del producto
    return render(request, 'detalle_producto.html', {'producto': producto})

"""

def producto_detalle(request, producto_id):
    print(f"Buscando detalles para el producto_id: {producto_id}")  # Para depuración

    # Obtiene los detalles básicos del producto
    producto = obtener_detalle_producto(producto_id)

    # Manejo de errores si no se encuentra el producto
    if 'error' in producto:
        return JsonResponse({'error': producto['error']}, status=404)

    # Obtén el stock del producto usando la API
    stock_data = producto_stock(request, producto_id)  # Llama a la función para obtener el stock

    # Combina los datos del producto y del stock
    contexto = {
        'producto': producto,
        'producto_id': producto.get('producto_id'),
        'stock': stock_data.get('stock', 'No disponible'),  # Valor por defecto si no hay stock
        'error': stock_data.get('error', None),            # Manejo de errores del stock
    }

    # Renderizar la plantilla con los detalles del producto y el stock
    return render(request, 'detalle_producto.html', contexto) 
#categorias api /////////////////////////////////////////////////////////////////////////////////////////////////////


def obtener_categorias():
    headers = {
        'content-type': 'application/json',
        'access-token': OBUMA_API_KEY,
    }

    try:
        response = requests.get(f"{OBUMA_URL}/productosCategorias.list.json", headers=headers)

        print(f"Estado de la respuesta: {response.status_code}")
        print(f"Contenido de la respuesta: {response.text}")

        if response.status_code == 200:
            return response.json()  
        else:
            return {'error': f'Error al obtener categorías: {response.status_code}'}
    except requests.exceptions.RequestException as e:
        return {'error': f'Error en la solicitud: {str(e)}'}
    

def obtener_fabricantes():
    headers = {
        'content-type': 'application/json',
        'access-token': OBUMA_API_KEY,
    }

    try:
        # Asegúrate de que la URL sea la correcta para obtener fabricantes
        response = requests.get(f"{OBUMA_URL}/productosFabricantes.list.json", headers=headers)

        print(f"Estado de la respuesta: {response.status_code}")
        print(f"Contenido de la respuesta: {response.text}")

        if response.status_code == 200:
            return response.json()  
        else:
            return {'error': f'Error al obtener fabricantes: {response.status_code}'}
    except requests.exceptions.RequestException as e:
        return {'error': f'Error en la solicitud: {str(e)}'}

"""
def listar_categorias(request):# ESTO SE PODRIA ELIMINAR SI SE QUIERE, TAMBIEN HABRIA QUE ELIMINAR LA URL Y EL HTML (SI ES NECESARIO) "para limpiar el codigo"
    categorias = obtener_categorias()

    if 'data' in categorias and categorias['data']:
        lista_categorias = categorias['data']
        return render(request, 'listar_categorias.html', {'categorias': lista_categorias})
    else:
        return JsonResponse({'error': 'No se encontraron categorías'})
"""
#detalle de las categorias

def obtener_productos_por_categoria(categoria_id):
    headers = {
        'content-type': 'application/json',
        'access-token': OBUMA_API_KEY,
    }

    try:
        # Obtener todas las categorías
        categorias_response = requests.get(f"{OBUMA_URL}/productosCategorias.list.json", headers=headers)
        if categorias_response.status_code != 200:
            return {'error': f'Error al obtener categorías: {categorias_response.status_code}'}
        
        # Obtener todos los fabricantes
        fabricantes_response = obtener_fabricantes()
        if 'error' in fabricantes_response:
            return {'error': fabricantes_response['error']}
        fabricantes = fabricantes_response.get('data', [])

        # Crear un diccionario para mapear el id de fabricante a su nombre
        fabricantes_dict = {fabricante['producto_fabricante_id']: fabricante['producto_fabricante_nombre'] for fabricante in fabricantes}

        # Obtener todos los productos
        productos_response = requests.get(f"{OBUMA_URL}/productos.list.json", headers=headers)
        if productos_response.status_code != 200:
            return {'error': f'Error al obtener productos: {productos_response.status_code}'}

        # Extraer datos de las respuestas
        categorias = categorias_response.json().get('data', [])
        productos = productos_response.json().get('data', [])

        # Crear un diccionario para mapear el id de categoría a su nombre
        categorias_dict = {categoria['producto_categoria_id']: categoria['producto_categoria_nombre'] for categoria in categorias}

        # Filtrar productos que pertenecen a la categoría deseada
        productos_filtrados = [
            producto for producto in productos 
            if producto.get('producto_categoria') == str(categoria_id)  # Comparar con producto_categoria
        ]

        # Añadir el nombre de la categoría a los productos filtrados
        for producto in productos_filtrados:
            producto['categoria_nombre'] = categorias_dict.get(producto.get('producto_categoria'), 'Desconocida')
            producto['fabricante_nombre'] = fabricantes_dict.get(producto.get('producto_fabricante'), 'Desconocido')

        # Obtener el nombre de la categoría a partir del id
        categoria_nombre = categorias_dict.get(str(categoria_id), 'Categoría Desconocida')

        return {'data': productos_filtrados, 'categoria_nombre': categoria_nombre}

    
    except requests.exceptions.RequestException as e:
        return {'error': f'Error en la solicitud: {str(e)}'}


def productos_por_categoria(request, categoria_id):
    productos = obtener_productos_por_categoria(categoria_id)
    
    if 'error' in productos:
        return render(request, 'error.html', {'error': productos['error']})
    
    # Extraer el nombre de la categoría
    categoria_nombre = productos.get('categoria_nombre', 'Categoría Desconocida')

    return render(request, 'productos_por_categoria.html', {
        'categoria_id': categoria_id,
        'productos': productos['data'],  # Acceder a la lista de productos filtrados
        'categoria_nombre': categoria_nombre  # Pasar el nombre de la categoría a la plantilla
    })

#------------------------------------------------------------------------------------ver carrito--------------------------------------------------------
def error_view(request):
    return render(request, 'error.html')


@login_required
def agregar_al_carrito(request, producto_id):
    headers = {
        'content-type': 'application/json',
        'access-token': OBUMA_API_KEY,
    }

    try:
        # Obtener el detalle del producto específico
        response = requests.get(f"{OBUMA_URL}/productos.list.json?id={producto_id}", headers=headers)
        print(f"Estado de la respuesta: {response.status_code}")  # Para depurar
        print(f"Contenido de la respuesta: {response.text}")      # Para depurar

        if response.status_code == 200:
            productos = response.json()
            if 'data' in productos and len(productos['data']) > 0:
                producto = productos['data'][0]  # Suponiendo que la API devuelve un array de productos
                producto['producto_id'] = producto_id  # Agregar ID del producto si es necesario

                # Obtener todos los fabricantes para poder mostrar el nombre
                fabricantes_response = obtener_fabricantes()
                if 'error' in fabricantes_response:
                    return {'error': fabricantes_response['error']}
                fabricantes = fabricantes_response.get('data', [])

                # Crear un diccionario de fabricantes
                fabricantes_dict = {fabricante['producto_fabricante_id']: fabricante['producto_fabricante_nombre'] for fabricante in fabricantes}

                # Añadir el nombre del fabricante al producto
                producto['fabricante_nombre'] = fabricantes_dict.get(producto.get('producto_fabricante'), 'Desconocido')

                # Obtener todas las categorías para poder mostrar el nombre
                categorias_response = requests.get(f"{OBUMA_URL}/productosCategorias.list.json", headers=headers)
                if categorias_response.status_code != 200:
                    return {'error': f'Error al obtener categorías: {categorias_response.status_code}'}

                categorias = categorias_response.json().get('data', [])

                # Crear un diccionario de categorías
                categorias_dict = {categoria['producto_categoria_id']: categoria['producto_categoria_nombre'] for categoria in categorias}

                # Añadir el nombre de la categoría al producto
                producto['categoria_nombre'] = categorias_dict.get(producto.get('producto_categoria'), 'Desconocida')

                # Obtener el carrito de la sesión y verificar si el producto ya está
                carrito = request.session.get('carrito', {})
                if producto_id in carrito:
                    # Si ya está en el carrito, solo aumentar la cantidad
                    carrito[producto_id]['cantidad'] += 1
                else:
                    # Si no está en el carrito, agregarlo con la cantidad inicial de 1
                    producto['cantidad'] = 1  # Establecer la cantidad inicial como 1
                    carrito[producto_id] = producto  # Agregar el producto con la cantidad

                # Guardar el carrito actualizado en la sesión
                request.session['carrito'] = carrito

                return redirect('ver_carrito')  # Redirigir a la vista del carrito
            else:
                return {'error': 'Producto no encontrado en la respuesta de la API'}
        else:
            return {'error': f"Error en la solicitud: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {'error': f"Error en la solicitud: {str(e)}"}




@login_required
def ver_carrito(request):
    # Obtener el carrito de la sesión
    carrito = request.session.get('carrito', {})

    # Si el carrito está vacío, podemos redirigir al usuario a la página de inicio o mostrar un mensaje adecuado
    if not carrito:
        return render(request, 'carrito.html')  # O cualquier mensaje o vista que indique que el carrito está vacío

    # Calcular el total del carrito sumando los precios * cantidades de los productos
    total_carrito = 0
    for producto_id, producto in carrito.items():
        # Verificar los valores del carrito
        print(f"Producto ID: {producto_id}, Precio: {producto.get('producto_precio_clp_neto')}, Cantidad: {producto.get('cantidad')}")
        
        # Convertir precio a float y cantidad a int para evitar errores de tipo
        precio = float(producto.get('producto_precio_clp_neto', 0))
        cantidad = int(producto.get('cantidad', 1))
        total_carrito += precio * cantidad

    print(f"Total Carrito: {total_carrito}")  # Verificar el total calculado

    # Renderizar la plantilla con los productos en el carrito y el total calculado
    return render(request, 'carrito.html', {'carrito': carrito, 'total_carrito': total_carrito})


    
@login_required
def eliminar_del_carrito(request, producto_id):
    # Obtener el carrito de la sesión
    carrito = request.session.get('carrito', {})

    # Eliminar el producto si existe
    if str(producto_id) in carrito:
        del carrito[str(producto_id)]

    # Guardar el carrito actualizado en la sesión
    request.session['carrito'] = carrito
    request.session.modified = True

    return redirect('ver_carrito')  # Redirigir a la vista del carrito después de eliminar


    
@login_required
def vaciar_carrito(request):
    # Vaciar el carrito almacenado en la sesión
    request.session['carrito'] = {}
    request.session.modified = True  # Asegura que se guarde el cambio en la sesión

    # Redirige a la vista del carrito
    return redirect('ver_carrito')

@login_required
def aumentar_cantidad(request, producto_id):
    # Obtener el carrito de la sesión
    carrito = request.session.get('carrito', {})

    # Verifica si el producto ya está en el carrito
    if str(producto_id) in carrito:
        # Aumentar la cantidad
        carrito[str(producto_id)]['cantidad'] += 1
    else:
        # Agregar el producto con cantidad 1 si no está en el carrito
        carrito[str(producto_id)] = {'cantidad': 1, 'producto': 'producto'}  # Puedes reemplazar 'producto' con los detalles del producto

    # Guardar el carrito en la sesión
    request.session['carrito'] = carrito

    return redirect('ver_carrito')  # O la vista que desees

    
@login_required
def disminuir_cantidad(request, producto_id):
    carrito = request.session.get('carrito', {})
    if str(producto_id) in carrito:
        if carrito[str(producto_id)]['cantidad'] > 1:
            carrito[str(producto_id)]['cantidad'] -= 1
        else:
            del carrito[str(producto_id)]  # Eliminar el producto si la cantidad es 1

    request.session['carrito'] = carrito
    return redirect('ver_carrito')
    

#----------------------------------------------------------enviar datos de la orden por correo-------------------------------------------------------------
"""
@login_required
def realizar_pedido(request):
    if request.method == 'POST':
        # Obtener los productos del carrito
        carrito = request.session.get('carrito', {})
        
        if not carrito:
            return render(request, 'carrito_vacio.html')
        
        # Datos del cliente (usuario)
        usuario = request.user
        #nombre_cliente = usuario.get_full_name()
        #email_cliente = usuario.email

        # Nuevos datos de dirección
        nombre_cliente = request.POST.get('nombre_cliente')  
        email_cliente = request.POST.get('email_cliente')
        direccion = request.POST.get('direccion')
        telefono = request.POST.get('telefono')
        codigo_postal = request.POST.get('codigo_postal')
        comentario = request.POST.get('comentario')


        # Preparar los productos del carrito
        productos_carrito = []
        for producto_id, producto in carrito.items():
            producto_info = {
                'nombre': producto.get('producto_nombre'),
                'precio': producto.get('producto_precio_clp_neto'),
                'cantidad': producto.get('cantidad'),
                'producto_codigo_comercial': producto.get('producto_codigo_comercial')
            }
            productos_carrito.append(producto_info)
        

        # Calcular el total del carrito de forma segura
        total_carrito = sum([
            (float(producto['precio']) if producto['precio'] else 0) * 
            (int(producto['cantidad']) if producto['cantidad'] else 1)
            for producto in productos_carrito
        ])

        # Enviar el correo con los detalles del pedido y los datos adicionales
        enviar_correo_orden(productos_carrito, total_carrito, nombre_cliente, email_cliente, direccion, telefono, codigo_postal, comentario)
        
        # Limpiar el carrito después de enviar el correo
        request.session['carrito'] = {}
        
        # Redirigir a una página de éxito o confirmación de pedido
        return render(request, 'exito.html', {'nombre_cliente': nombre_cliente, 'total_carrito': total_carrito})

    return render(request, 'ingresar_direccion_envio.html')

"""

@login_required
def realizar_pedido(request):
    if request.method == 'POST':
        carrito = request.session.get('carrito', {})
        
        if not carrito:
            return render(request, 'carrito_vacio.html')
        
        usuario = request.user
        nombre_cliente = request.POST.get('nombre_cliente')  
        email_cliente = request.POST.get('email_cliente')
        direccion = request.POST.get('direccion')
        telefono = request.POST.get('telefono')
        codigo_postal = request.POST.get('codigo_postal')
        comentario = request.POST.get('comentario')

        productos_carrito = []
        for producto_id, producto in carrito.items():
            producto_info = {
                'nombre': producto.get('producto_nombre'),
                'precio': producto.get('producto_precio_clp_neto'),
                'cantidad': producto.get('cantidad'),
                'producto_codigo_comercial': producto.get('producto_codigo_comercial')
            }
            productos_carrito.append(producto_info)
        
        total_carrito = sum([
            (float(producto['precio']) if producto['precio'] else 0) * 
            (int(producto['cantidad']) if producto['cantidad'] else 1)
            for producto in productos_carrito
        ])

        # Guardar el pedido en la base de datos
        pedido = Pedido.objects.create(
            usuario=usuario,
            nombre_cliente=nombre_cliente,
            email_cliente=email_cliente,
            direccion=direccion,
            telefono=telefono,
            codigo_postal=codigo_postal,
            comentario=comentario,
            total_carrito=total_carrito
        )

        # Guardar los detalles de los productos, incluyendo el SKU
        for producto in productos_carrito:
            DetalleProducto.objects.create(
                pedido=pedido,
                nombre_producto=producto['nombre'],
                precio=producto['precio'],
                cantidad=producto['cantidad'],
                producto_codigo_comercial=producto['producto_codigo_comercial']
            )

        # Enviar el correo
        enviar_correo_orden(productos_carrito, total_carrito, nombre_cliente, email_cliente, direccion, telefono, codigo_postal, comentario)
        
        # Limpiar el carrito y redirigir
        request.session['carrito'] = {}
        return render(request, 'exito.html', {'nombre_cliente': nombre_cliente, 'total_carrito': total_carrito})

    return render(request, 'ingresar_direccion_envio.html')


def enviar_correo_orden(productos_carrito, total_carrito, nombre_cliente, email_cliente, direccion, telefono, codigo_postal, comentario):
    subject = 'Nuevo Pedido Recibido'
    
    context = {
        'productos_carrito': productos_carrito,
        'total_carrito': total_carrito,
        'nombre_cliente': nombre_cliente,
        'email_cliente': email_cliente,
        'direccion': direccion,
        'telefono': telefono,
        'codigo_postal': codigo_postal,
        'comentario': comentario,
    }
    
    template = get_template('correo_orden.html')
    content = template.render(context)
    
    email = EmailMultiAlternatives(
        subject,
        content,
        settings.EMAIL_HOST_USER,
        ['fcchidan@gmail.com']
    )
    email.attach_alternative(content, 'text/html')
    email.send()


#----------------------------------------------------------------------boton busqueda----------------------------------------------
def eliminar_acentos(texto):
    """
    Elimina los acentos de un texto dado.
    """
    return ''.join(
        char for char in unicodedata.normalize('NFD', texto)
        if unicodedata.category(char) != 'Mn'
    )

def buscar_productos(request):
    query = request.GET.get('q', '').strip()

    if query:
        headers = {
            'content-type': 'application/json',
            'access-token': OBUMA_API_KEY,  # Tu API key de Obuma
        }

        try:
            # Solicitud a la API para obtener los productos
            response = requests.get(f"{OBUMA_URL}/productos.list.json", headers=headers)
            
            if response.status_code == 200:
                # Imprimir en consola para depuración
                print("Respuesta de la API:", response.json())

                productos = response.json().get('data', [])

                # Normalizar el término de búsqueda
                query_normalizada = eliminar_acentos(query.lower())

                # Filtrar los productos por el término de búsqueda
                productos_filtrados = [
                    producto for producto in productos
                    if query_normalizada in eliminar_acentos(producto.get('producto_nombre', '').lower())
                ]

                # Renderizar resultados
                return render(request, 'resultados_busqueda.html', {
                    'query': query,
                    'productos': productos_filtrados,
                })
            else:
                # Manejar errores de estado HTTP
                mensaje = f"Error al obtener productos: Código {response.status_code}"
                return render(request, 'resultados_busqueda.html', {
                    'query': query,
                    'mensaje': mensaje,
                    'productos': []
                })

        except requests.exceptions.RequestException as e:
            # Manejo de excepciones de red
            mensaje = f"Error al comunicarse con la API: {str(e)}"
            return render(request, 'resultados_busqueda.html', {
                'query': query,
                'mensaje': mensaje,
                'productos': []
            })

    # Caso en que no se ingresó un término de búsqueda
    mensaje = "Por favor, ingresa un término de búsqueda."
    return render(request, 'resultados_busqueda.html', {
        'query': query,
        'mensaje': mensaje,
        'productos': []
    })

def mostrar_productos_buscados(request):
    # Ordenamos los productos por la cantidad de veces que han sido buscados
    productos_ordenados = productos_buscados.most_common(5)

    # Crear una lista de productos que coincidan con los más buscados
    productos_mostrados = []

    for nombre, _ in productos_ordenados:
        # Aquí podrías hacer una consulta a la API para obtener los detalles de cada producto
        headers = {
            'content-type': 'application/json',
            'access-token': OBUMA_API_KEY,
        }

        response = requests.get(f"{OBUMA_URL}/productos.list.json", headers=headers)

        if response.status_code == 200:
            productos = response.json().get('data', [])
            for producto in productos:
                if producto['producto_nombre'] == nombre:
                    productos_mostrados.append(producto)

    return render(request, 'ultimas_imagenes.html', {
        'productos': productos_mostrados
    })


#------------------------------------------------mostrar productos al azar-------------------------------------------------------


def obtener_productos_aleatorios():
    headers = {
        'content-type': 'application/json',
        'access-token': OBUMA_API_KEY,
    }

    try:
        # Obtener todos los productos
        productos_response = requests.get(f"{OBUMA_URL}/productos.list.json", headers=headers)
        if productos_response.status_code != 200:
            return {'error': f'Error al obtener productos: {productos_response.status_code}'}

        # Obtener todas las categorías
        categorias_response = requests.get(f"{OBUMA_URL}/productosCategorias.list.json", headers=headers)
        if categorias_response.status_code != 200:
            return {'error': f'Error al obtener categorías: {categorias_response.status_code}'}

        # Extraer datos de las respuestas
        productos = productos_response.json().get('data', [])
        categorias = categorias_response.json().get('data', [])

        # Crear un diccionario para mapear el id de categoría a su nombre
        categorias_dict = {categoria['producto_categoria_id']: categoria['producto_categoria_nombre'] for categoria in categorias}

        # Añadir el nombre de la categoría a los productos
        for producto in productos:
            # Aquí, asumimos que 'producto_categoria' es el id de la categoría
            producto['producto_categoria_nombre'] = categorias_dict.get(producto.get('producto_categoria'), 'Desconocida')

        # Si no hay productos, devolver un error
        if not productos:
            return {'error': 'No se encontraron productos'}

        # Seleccionar un número determinado de productos al azar (por ejemplo, 5 productos)
        productos_aleatorios = random.sample(productos, min(5, len(productos)))

        return {'data': productos_aleatorios}

    except requests.exceptions.RequestException as e:
        return {'error': f'Error en la solicitud: {str(e)}'}



# Vista para mostrar los productos al azar
def productos_aleatorios(request):
    productos = obtener_productos_aleatorios()
    
    # Manejo de errores en la obtención de productos
    if 'error' in productos:
        return JsonResponse({'error': productos['error']})

    # Verifica si la clave 'data' existe y no está vacía
    if 'data' in productos and productos['data']:
        lista_productos_aleatorios = productos.get('data', [])
    else:
        return JsonResponse({'error': 'No se encontraron productos al azar'})

    # Renderiza los productos al azar en el template
    return render(request, 'ultimas_imagenes.html', {'productos': lista_productos_aleatorios})




def inicio(request):
    productos = obtener_productos_aleatorios()

    # Manejo de errores
    if 'error' in productos:
        return render(request, 'index.html', {'error': productos['error']})

    # Si se obtienen productos, pasarlos al contexto
    productos_aleatorios = productos.get('data', [])

    return render(request, 'index.html', {'productos_aleatorios': productos_aleatorios})


#---------------------------------------verificador pagina principal de bots--------------------------------------
def verify_bot(request):
    if request.method == 'POST':
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY,
            'response': recaptcha_response
        }
        url = 'https://www.google.com/recaptcha/api/siteverify'
        response = requests.post(url, data=data)
        result = response.json()

        if result.get('success'):
            # Verificación exitosa, redirige a la página principal
            request.session['verified'] = True
            return redirect('inicio')  # Cambia 'home' por la URL principal de tu sitio
        else:
            return HttpResponse('Error: No se pudo verificar. Intenta nuevamente.')
    return render(request, 'verify.html')

#---------------------------------------------caché---------------------------------------



def obtener_productos_view(request):
    if request.method != "GET":
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        productos = obtener_productos()
        return JsonResponse(productos, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)