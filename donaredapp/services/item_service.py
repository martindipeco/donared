from ..models import Zona, Categoria

def crear_item(data):
    try:
        zona = Zona.objects.get(pk=data["zona_id"])
        categoria = Categoria.objects.get(pk=data["categoria_id"])
    except (Zona.DoesNotExist, Categoria.DoesNotExist):
        raise ValueError("Zona o categoría inválida.")
    
    item = Item(
        nombre=data["nombre"],
        descripcion=data["descripcion"],
        zona=zona,
        categoria=categoria
    )
    item.save()
    return item