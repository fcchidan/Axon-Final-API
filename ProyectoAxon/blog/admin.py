from django.contrib import admin
from .models import Categoria, Producto, ElementoCarrito, Orden, DireccionEnvio, ElementoOrden, DetalleProducto, Pedido

#class CategoriaAdmin(admin.ModelAdmin):
#   readonly_fields = ('creado',)
#  search_fields = ('nombre', 'descripcion')


#class ProductoAdmin(admin.ModelAdmin):
#   readonly_fields = ('usuario', 'creado',) 
#   search_fields = ('titulo', 'contenido')  
#   list_display = ('titulo', 'creado', 'precio') 
#   list_filter = ('categorias',)
    
#   def save_model(self, request, obj, form, change):
#       if not obj.usuario_id:
#           obj.usuario_id = request.user.id
#       obj.save()



#class OrdenAdmin(admin.ModelAdmin):
#    list_display = ('usuario', 'nombre_usuario', 'telefono_usuario', 'correo_usuario', 'direccion_envio', 'mostrar_productos', 'fecha_creacion', 'precio_total')
#    search_fields = ('usuario__username', 'nombre_usuario', 'direccion_envio__telefono', 'direccion_envio__correo')
#    list_filter = ('fecha_creacion',)
#    ordering = ('-fecha_creacion',)

#    def telefono_usuario(self, obj):
#       return obj.direccion_envio.telefono if obj.direccion_envio else "No disponible"

#   def correo_usuario(self, obj):
#       return obj.direccion_envio.correo if obj.direccion_envio else "No disponible"

#   def mostrar_productos(self, obj):
#       elementos_orden = obj.elementoorden_set.all()
#       productos_unicos = set()
#       productos_unicos_str = []
        
#      for elemento in elementos_orden:
#          producto_str = f"{elemento.cantidad} x {elemento.producto.titulo}"
#          if producto_str not in productos_unicos:
#              productos_unicos.add(producto_str)
#              productos_unicos_str.append(producto_str)
        
#      return ", ".join(productos_unicos_str)
    
#   mostrar_productos.short_description = 'Productos'
#   telefono_usuario.short_description = 'Teléfono'
#   correo_usuario.short_description = 'Correo'
"""def mostrar_precio_formateado(self, obj):
        if obj and obj.precio is not None:  # Verificar si obj y precio no son None
            return f"{obj.precio:,.0f}".replace(',', '.')
        return "N/A"  # Devolver "N/A" si el precio es None
    mostrar_precio_formateado.short_description = 'Precio'
    """

class DireccionEnvioAdmin(admin.ModelAdmin):
    list_display = ('direccion', 'ciudad', 'codigo_postal', 'telefono', 'correo')

class DetalleProductoInline(admin.TabularInline):  # Usamos TabularInline para una vista en tabla
    model = DetalleProducto
    extra = 0  # No mostrar filas adicionales vacías
    readonly_fields = ('nombre_producto', 'mostrar_precio_formateado', 'cantidad', 'producto_codigo_comercial')  # Solo lectura
    exclude = ('precio',) 

    def mostrar_precio_formateado(self, obj):
        if obj and obj.precio is not None:  # Verificar si obj y precio no son None
            return f"{obj.precio:,.0f}".replace(',', '.')
        return "N/A"  # Devolver "N/A" si el precio es None
    mostrar_precio_formateado.short_description = 'Precio'

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_cliente', 'email_cliente', 'mostrar_total_formateado', 'fecha_creacion')  # Campos a mostrar en la lista de pedidos
    list_filter = ('fecha_creacion',)  # Filtro por fecha
    search_fields = ('nombre_cliente', 'email_cliente')  # Búsqueda por nombre y email
    inlines = [DetalleProductoInline]  # Anidar el inline de DetalleProducto
    readonly_fields = ('usuario', 'nombre_cliente', 'email_cliente', 'direccion', 'telefono', 'codigo_postal', 'comentario', 'mostrar_total_formateado', 'fecha_creacion')
    exclude = ('total_carrito',)

    def mostrar_total_formateado(self, obj):
        if obj.total_carrito is not None:
            return f"{obj.total_carrito:,.0f}".replace(',', '.')
        return "N/A"

    mostrar_total_formateado.short_description = 'Total Carrito'

# Register your models here.
#admin.site.register(Categoria, CategoriaAdmin)
#admin.site.register(Producto, ProductoAdmin)
admin.site.register(ElementoCarrito)
#admin.site.register(Orden, OrdenAdmin)
admin.site.register(DireccionEnvio, DireccionEnvioAdmin)
# Ocultar el modelo completo
admin.site.unregister(ElementoCarrito)
admin.site.unregister(DireccionEnvio)