"""
URL configuration for ProyectoAxon project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from mainapp import views
import pages.views
from django.conf import settings




urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inicio, name="inicio"),
    path('inicio/', views.inicio, name="inicio"),
    path('productos/', views.productos, name="productos"),
    path('clientes/', views.clientes, name="clientes"),
    path('contacto/', views.contacto, name="contacto"),
    path('empresa/', views.empresa, name="empresa"),
    path('representacion/', views.representacion, name="representacion"),
    path('servicios/', views.servicios, name="servicios"),
    path('pagina/<str:slug>', pages.views.page, name="page"),
    #path('categoria/<int:categoria_id>', views.categoria, name="categoria"),
    path('producto/<int:producto_id>', views.producto, name="producto"),
    path('registro/', views.register_page, name="registro"),
    path('login/', views.login_page, name="login"),
    path('logout/', views.logout_user, name="logout"),
    #path('carrito/', views.ver_carrito, name='ver_carrito'),
    #path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    #path('carrito/eliminar/<int:elemento_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
    #path('carrito/orden/', views.realizar_orden, name='realizar_orden'),
    #path('ingresar_direccion_envio/', views.ingresar_direccion_envio, name='ingresar_direccion_envio'),
    path('buscar/', views.buscar_productos, name='buscar_productos'),
    #path('producto/<int:producto_id>/', views.producto_detalle, name='producto'),
    #path('aumentar/<int:elemento_id>/', views.aumentar_cantidad, name='aumentar_cantidad'),
    #path('disminuir/<int:elemento_id>/', views.disminuir_cantidad, name='disminuir_cantidad'),
    #path('resultados/', views.resultados_busqueda, name='resultados_busqueda'),
    #path('realizar_orden/', views.realizar_orden, name='realizar_orden'),
    #path('exito/<int:orden_id>/', views.pagina_exito, name='pagina_exito'),
    path('password_reset/', views.password_reset_request, name='password_reset_request'),
    path('set_new_password/', views.set_new_password, name='set_new_password'),
    # urls api
    path('lista_productos/', views.listar_productos, name='lista_productos'),
    path('producto/<int:producto_id>/detalle/', views.producto_detalle, name='producto_detalle'),
    #path('categorias/', views.listar_categorias, name='listar_categorias'),
    #path('categoria/<int:categoria_id>/', views.categoria, name='categoria'),
    path('categoria/<str:categoria_id>/productos/', views.productos_por_categoria, name='productos_por_categoria'),
    path('categoria/<int:categoria_id>/productos/', views.productos_por_categoria, name='productos_por_categoria'),
    path('productos/', views.listar_productos, name='listar_productos'),
    path('productos/<int:producto_id>/', views.producto_detalle, name='producto_detalle'),
    path('productos/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('agregar_al_carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('ver_carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('agregar_al_carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('eliminar_del_carrito/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('error/', views.error_view, name='error'),
    path('aumentar/<int:producto_id>/', views.aumentar_cantidad, name='aumentar_cantidad'),
    path('disminuir/<int:producto_id>/', views.disminuir_cantidad, name='disminuir_cantidad'),
    #path('confirmar-direccion/', views.confirmar_direccion, name='confirmar_direccion'),
    #path('procesar_orden/', views.procesar_orden, name='procesar_orden'),
    #path('orden_completada/', views.orden_completada, name='orden_completada'),
    path('realizar-pedido/', views.realizar_pedido, name='realizar_pedido'),
    path('productos/aleatorios/', views.productos_aleatorios, name='productos_aleatorios'),
    path('producto/<int:producto_id>/stock/', views.producto_stock, name='productos_stock'),
    #path('producto/<int:producto_id>/stock/', views.obtener_stock_producto, name='obtener_stock_producto'),
    

    
]

# Ruta imagenes
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
