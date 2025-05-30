Proyecto DonaRed - Grupo 4 - Acelerador Polo IT 2025

### Actualización: 30 de Mayo 2024 - Mejoras en la Geolocalización y Validación de Direcciones

**Cambios Recientes:**

1. **Eliminación del Campo Zona:**
    * Se eliminó el modelo `Zona` y su relación con `Item` para simplificar la estructura.
    * Se actualizó el formulario de publicación para eliminar la selección de zona.
    * Se generaron y aplicaron las migraciones correspondientes.

2. **Mejoras en la Validación de Direcciones:**
    * Se implementó autocompletado de direcciones usando Nominatim/OpenStreetMap.
    * El sistema ahora sugiere direcciones válidas mientras el usuario escribe.
    * Se agregó validación específica para direcciones en Argentina.
    * Se mejoró el manejo de errores y los mensajes de validación.

3. **Requisitos Técnicos:**
    * Python 3.x
    * Django 5.2
    * geopy (para geocodificación)
    * Leaflet y Leaflet.markercluster (para el mapa)
    * Conexión a internet (para geocodificación y mapa)

4. **Instalación de Dependencias:**
    ```bash
    pip install geopy
    ```

5. **Configuración del Sistema:**
    * Se agregó configuración de logging para mejor depuración.
    * Se configuró el user-agent para Nominatim.
    * Se implementaron límites de tasa para respetar las políticas de uso de la API.

6. **Funcionamiento del Mapa:**
    * El mapa se centra automáticamente en Buenos Aires.
    * Los marcadores se agrupan automáticamente cuando hay muchos en una zona.
    * Se puede filtrar por categoría.
    * Cada marcador muestra:
        * Imagen del item (si existe)
        * Nombre del item
        * Categoría
        * Botón para ver más detalles

7. **Validación de Direcciones:**
    * El sistema verifica que la dirección esté en Argentina.
    * Se validan las coordenadas para asegurar que estén dentro del territorio argentino.
    * Se muestra un menú desplegable con sugerencias de direcciones válidas.
    * Las coordenadas se guardan automáticamente al seleccionar una dirección válida.

8. **Panel de Administración:**
    * Se agregaron las coordenadas (latitud y longitud) a la vista de lista de items.
    * Se pueden ver y filtrar items por sus coordenadas.
    * Se mantiene un registro de las direcciones y coordenadas para cada item.

**Notas Importantes:**
* El sistema requiere conexión a internet para la geocodificación y el mapa.
* Se recomienda usar direcciones completas (calle, número, localidad, provincia).
* Las coordenadas se validan para asegurar que estén dentro de Argentina.
* El sistema respeta los límites de uso de la API de Nominatim.

### Documento de Cambios: Implementación de Geolocalización y Mapa de Donaciones

Este documento detalla los cambios realizados en el proyecto DonaRed para incorporar una funcionalidad de geolocalización y visualizar las donaciones en un mapa interactivo.

**Objetivo Principal:** Permitir a los usuarios ver las donaciones disponibles geolocalizadas en un mapa y facilitar la búsqueda por ubicación.

**Cambios Realizados:**

1.  **Creación de la nueva App `geo`:**
    *   Se creó una nueva aplicación de Django llamada `geo`.
    *   Esta app contendrá toda la lógica relacionada con la geolocalización y la visualización del mapa.
    *   Se añadió `'geo.apps.GeoConfig'` a `INSTALLED_APPS` en `donared/settings.py` para registrar la nueva app en el proyecto.

2.  **Actualización del Modelo `Item`:**
    *   Se modificó el modelo `Item` en `donaredapp/models.py` para añadir dos nuevos campos:
        *   `latitude`: Campo Decimal para almacenar la latitud de la donación.
        *   `longitude`: Campo Decimal para almacenar la longitud de la donación.
    *   Estos campos son opcionales (`null=True, blank=True`) para mantener la compatibilidad con ítems existentes que no tienen coordenadas.
    *   Se generaron y aplicaron las migraciones correspondientes (`python manage.py makemigrations` y `python manage.py migrate`) para actualizar la base de datos con estos nuevos campos.

3.  **Validación y Geocodificación en `ItemForm`:**
    *   Se actualizó el `ItemForm` en `donaredapp/forms.py`.
    *   Se añadió un método `clean()` que se ejecuta durante la validación del formulario.
    *   Dentro de `clean()`, se utiliza la librería `geopy` con el servicio Nominatim (OpenStreetMap) para obtener la latitud y longitud a partir del domicilio ingresado por el usuario.
    *   Se implementó un `RateLimiter` para cumplir con las políticas de uso de Nominatim (una solicitud por segundo).
    *   Si la geocodificación es exitosa, se almacenan la latitud y longitud en los datos limpios del formulario (`cleaned_data`).
    *   Si la geocodificación falla (no se encuentra la dirección), se añade un error al campo `domicilio` del formulario, impidiendo que se guarde el ítem.
    *   Se modificó el método `save()` del formulario para asegurarse de que la latitud y longitud obtenidas en `clean()` se asignen correctamente a la instancia del modelo `Item` antes de guardarla en la base de datos.

4.  **Implementación de Vistas para el Mapa (`geo/views.py`):**
    *   Se creó la vista `GeoMapView` (basada en `TemplateView`) para renderizar la plantilla HTML que contiene el mapa. Esta vista pasa las categorías al contexto para el filtro.
    *   Se creó la vista `GeoJSONView` (basada en `TemplateView`) que responde a las solicitudes AJAX desde el frontend. Esta vista:
        *   Filtra los ítems activos (`activo=True`).
        *   Filtra los ítems que tienen coordenadas (`latitude__isnull=False, longitude__isnull=False`).
        *   Permite filtrar por categoría si se recibe el parámetro `categoria` en la solicitud GET.
        *   Formatea los datos de los ítems en formato GeoJSON, incluyendo las coordenadas, nombre, categoría, URL de la imagen (si existe) y la URL de detalle para la página de tarjeta del ítem.

5.  **Configuración de URLs para la App `geo` (`geo/urls.py` y `donared/urls.py`):**
    *   Se definió un archivo `urls.py` dentro de la app `geo`.
    *   Se mapeó la URL `/mapa/` a la vista `GeoMapView`.
    *   Se mapeó la URL `/api/items/` a la vista `GeoJSONView` para la API que proporciona los datos de los ítems en formato JSON.
    *   Se incluyeron las URLs de la app `geo` en el archivo principal `donared/urls.py` utilizando `path('geo/', include('geo.urls'))`.

6.  **Creación de la Plantilla del Mapa (`geo/templates/geo/mapa.html`):**
    *   Se creó un directorio `geo/templates/geo/` dentro de la app `geo`.
    *   Se creó el archivo `mapa.html` dentro de ese directorio.
    *   La plantilla extiende de la plantilla base existente (`donaredapp/base.html`) para mantener la consistencia del sitio.
    *   Se incluyeron los enlaces a las librerías de Leaflet y Leaflet.markercluster (CSS y JavaScript) desde un CDN.
    *   Se definió un contenedor (`<div id="map"></div>`) donde se inicializará el mapa.
    *   Se añadió un selector (`<select id="categoria-filter">`) para filtrar los ítems por categoría, poblado con las categorías pasadas desde la vista.
    *   Se implementó código JavaScript para:
        *   Inicializar el mapa Leaflet centrado en una ubicación por defecto (Buenos Aires) y con una capa base de OpenStreetMap.
        *   Crear una instancia de `L.markerClusterGroup()` para agrupar los marcadores cercanos automáticamente.
        *   Implementar una función `loadMarkers()` que realiza una solicitud `fetch` a la API `/geo/api/items/` (opcionalmente con filtro de categoría), procesa la respuesta GeoJSON y crea marcadores en el mapa.
        *   Cada marcador se enlaza a un popup que muestra la miniatura de la imagen (si existe), el nombre, la categoría y un botón "Ver más" que enlaza a la página de detalle del ítem.
        *   Se añadió un manejador de eventos al selector de categoría para recargar los marcadores cuando cambia la selección.
        *   Se añadió el grupo de clusters al mapa.
        *   Se incluyeron console logs para depuración (`API Response data:`, `Processing feature:`, `Invalid coordinates for feature:`) y se aseguró que las coordenadas sean válidas antes de crear el marcador.
        *   Se corrigió el orden de las coordenadas para Leaflet a `[lat, lon]`.

7.  **Actualización del Menú de Navegación:**
    *   Se modificó la plantilla base (`donaredapp/templates/donaredapp/base.html`) para añadir un enlace a la página del mapa en el menú de navegación principal, utilizando la URL nombrada `'geo:mapa'`.

**Cómo Funciona la Geolocalización y el Mapa:**

1.  **Publicación del Ítem:** Cuando un usuario publica un nuevo ítem a través del formulario, al enviar los datos, el método `clean()` del `ItemForm` toma el domicilio ingresado. Utiliza `geopy` para consultar el servicio Nominatim y obtener las coordenadas de latitud y longitud para esa dirección. Si Nominatim puede geocodificar la dirección, las coordenadas se almacenan temporalmente en el formulario. Si no, se muestra un error y el ítem no se guarda.
2.  **Guardado de Coordenadas:** Cuando el formulario es válido (incluyendo la geocodificación exitosa), el método `save()` del `ItemForm` se encarga de asignar la latitud y longitud obtenidas a los campos correspondientes del objeto `Item` antes de guardarlo en la base de datos.
3.  **Visualización en el Mapa:**
    *   Al acceder a la página `/geo/mapa/`, la vista `GeoMapView` renderiza la plantilla `mapa.html`.
    *   El código JavaScript en `mapa.html` realiza una solicitud `fetch` a la API `/geo/api/items/`.
    *   La vista `GeoJSONView` procesa esta solicitud, consulta la base de datos para obtener los ítems activos y con coordenadas, y devuelve estos datos en formato GeoJSON.
    *   El JavaScript en `mapa.html` recibe el JSON, itera sobre cada "feature" (cada ítem), extrae las coordenadas y la información de las propiedades (nombre, categoría, imagen, URL de detalle).
    *   Para cada ítem, crea un marcador de Leaflet en las coordenadas correspondientes.
    *   Configura un popup para cada marcador con la miniatura de la imagen (si existe), el nombre, la categoría y un enlace a la página de detalle del ítem.
    *   Los marcadores se añaden a un grupo de clusters (`L.markerClusterGroup`), que automáticamente agrupa los marcadores cercanos en diferentes niveles de zoom para mejorar la visualización cuando hay muchos ítems en una misma área.
    *   El filtro de categorías permite refinar qué ítems se muestran en el mapa realizando una nueva solicitud a la API con el filtro aplicado.
