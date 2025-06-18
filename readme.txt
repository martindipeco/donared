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

Implementación y Modificaciones Realizadas

Para la implementación del sistema de reseñas, se realizaron las siguientes modificaciones en la estructura del proyecto:

#### 1. Modelo `Resena` (`donaredapp/models.py`)
- Se creó el modelo `Resena` con los siguientes campos:
    - `solicitud` (OneToOneField a `Solicitud`): Vincula la reseña a una solicitud específica.
    - `calificacion` (IntegerField): La calificación de 1 a 5 estrellas.
    - `comentario` (TextField): El comentario del beneficiario.
    - `fecha_creacion` (DateTimeField): Fecha y hora de creación de la reseña.
    - `estado` (CharField con `ESTADO_CHOICES`): Define el estado de la reseña (`pending`, `approved`, `rejected`). Por defecto, es `pending`.
- Se añadió una `@property` llamada `estrellas` para una representación visual de la calificación en las plantillas.
- **Nota:** El campo `destacada` y su lógica asociada fueron eliminados posteriormente de este modelo y de todo el sistema.

#### 2. Vistas (`donaredapp/views.py` y `donaredapp/views_solicitudes.py`)
- **`crear_resena(request, solicitud_id)`:** Permite a un *beneficiario* crear una reseña para una `Solicitud` cuyo estado sea `COMPLETADA`.
- **`editar_resena(request, resena_id)`:** Permite a un *beneficiario* editar su propia reseña.
- **`eliminar_resena(request, resena_id)`:** Permite a un *beneficiario* eliminar su propia reseña.
- **`ver_resenas(request, username)`:** Muestra todas las reseñas de un *donante* específico, incluyendo su promedio de calificación y el número total de reseñas.
- **`ver_todas_resenas(request)`:** Muestra una lista de todas las reseñas del sistema, con opciones de filtrado y búsqueda.
- **`perfil_donante(request, username)`:** Muestra el perfil público de un *donante*, incluyendo su promedio de calificación, el desglose de calificaciones por porcentaje y las reseñas recientes.
- **Vistas de Administración de Reseñas (en `donaredapp/views.py`):**
    - `admin_resenas(request)`: Panel de administración de reseñas con estadísticas y listado.
    - `aprobar_resena(request, resena_id)`: Cambia el estado de una reseña a `approved`.
    - `rechazar_resena(request, resena_id)`: Cambia el estado de una reseña a `rejected`.
    - `editar_resena_admin(request, resena_id)`: Permite a los administradores editar una reseña y cambiar su estado.
- **Modificaciones clave en las vistas:**
    - Se ajustó la lógica en `crear_resena` para que las reseñas solo puedan crearse para solicitudes con estado `COMPLETADA`.
    - Se incluyó la lógica para calcular y pasar el promedio de calificación y el total de reseñas del donante a las vistas `index` y `categorias` para que se muestren en las tarjetas de ítems.
    - Se implementó un manejo de valores `None` para `item.usuario` en `index` y `categorias` para evitar errores.
    - Se corrigió el cálculo y se pasó la variable `porcentajes_calificaciones` (un diccionario) a la plantills.
    - En `donaredapp/views_solicitudes.py`, se añadió un atributo `has_resena` a los objetos `Solicitud` para indicar si ya existe una reseña.

#### 3. Plantillas (`donaredapp/templates/donaredapp/`)
- Se crearon las plantillas:
    - `crear_resena.html`
    - `ver_resenas.html`
    - `editar_resena.html`
    - `eliminar_resena.html`
    - `perfil_donante.html`
    - `ver_todas_resenas.html`
    - `admin_resenas.html`
- **Modificaciones clave en las plantillas existentes:**
    - En `crear_resena.html`, el slider de calificación fue reemplazado por un sistema de estrellas clickeables para una mejor experiencia de usuario.
    - En `perfil_donante.html`, se ajustó el uso del filtro `get_item` con la variable `porcentajes_calificaciones` para mostrar correctamente los porcentajes de calificación.
    - En `tarjeta.html` y `tarjeta_categorias.html`, se añadió la visualización de la calificación promedio del donante para los ítems.
    - En `solicitudes.html`, el botón "Crear Reseña" para solicitudes completadas ahora se deshabilita y muestra "Reseña Creada" si ya existe una reseña.
- **Eliminado:** La plantilla `resenas_destacadas.html` fue eliminada.

a `perfil_donante.html` para la visualización del desglose de estrella#### 4. URLs (`donaredapp/urls.py`)
- Se añadieron las siguientes rutas URL:
    - `path('perfil-donante/<str:username>/', views.perfil_donante, name='perfil_donante')`
    - `path('solicitud/<int:solicitud_id>/crear-resena/', views.crear_resena, name='crear_resena')`
    - `path('resena/<int:resena_id>/editar/', views.editar_resena, name='editar_resena')`
    - `path('resena/<int:resena_id>/eliminar/', views.eliminar_resena, name='eliminar_resena')`
    - `path('resenas/<str:username>/', views.ver_resenas, name='ver_resenas')`
    - `path('resenas/', views.ver_todas_resenas, name='ver_todas_resenas')`
    - Rutas para la gestión en el admin:
        - `path('admin/resenas/', views.admin_resenas, name='admin_resenas')`
        - `path('admin/resena/<int:resena_id>/aprobar/', views.aprobar_resena, name='aprobar_resena')`
        - `path('admin/resena/<int:resena_id>/rechazar/', views.rechazar_resena, name='rechazar_resena')`
        - `path('admin/resena/<int:resena_id>/editar/', views.editar_resena_admin, name='editar_resena_admin')`
- **Eliminado:** Se eliminaron las URLs relacionadas con `resenas_destacadas`.

#### 5. Panel de Administración (`donaredapp/admin.py`)
- Se registró el modelo `Resena` en el panel de administración.
- Se configuró `list_display` para incluir `display_estado`, una columna personalizada que muestra el estado de la reseña con colores específicos y enlaces si es `Pendiente`.
- Se configuraron `list_filter` y `search_fields` para facilitar la búsqueda y filtrado de reseñas.
- Se añadieron acciones en masa: `aprobar_seleccionadas` y `rechazar_seleccionadas` para gestionar múltiples reseñas simultáneamente.
- **Modificaciones clave:**
    - Se utilizó `from django.utils.html import format_html` en la función `display_estado` para asegurar que el HTML generado se renderice correctamente en lugar de mostrarse como texto plano.
    - Se eliminaron las referencias al campo `destacada` y las acciones `marcar_como_destacada` y `quitar_destacada`.

#### 6. Filtros de Plantilla (`donaredapp/templatetags/donaredapp_extras.py`)
- Se creó el directorio `donaredapp/templatetags/`.
- Se creó el archivo `donaredapp_extras.py` dentro de este directorio.
- Se definió el filtro de plantilla `get_item` para permitir el acceso a elementos de diccionarios en las plantillas (ej. `{{ diccionario|get_item:clave }}`).

#### 7. Migraciones
- Se ejecutaron los comandos `python manage.py makemigrations` y `python manage.py migrate` para aplicar los cambios del modelo `Resena` a la base de datos, incluyendo la creación del modelo y la posterior eliminación del campo `destacada`.

---

### Manual de Uso

#### Para Beneficiarios (Crear y Gestionar Reseñas)

1.  **Crear una Reseña:**
    *   Navega a la sección "Mis Solicitudes" (normalmente accesible desde el menú de usuario).
    *   Busca una solicitud que tenga el estado **"Completada"**.
    *   Si no has creado una reseña para esa solicitud, verás un botón para "Crear Reseña". Haz clic en él.
    *   Serás redirigido a la página de creación de reseña, donde podrás seleccionar una calificación de 1 a 5 estrellas haciendo clic en las estrellas y añadir un comentario opcional.
    *   Haz clic en "Enviar" para guardar tu reseña.
2.  **Ver tus Reseñas:**
    *   Puedes ver las reseñas que has hecho para un donante específico visitando su perfil público (`/perfil-donante/<username>/`).
    *   También puedes ver la reseña asociada a una solicitud completada en tu sección de "Mis Solicitudes".
3.  **Editar o Eliminar una Reseña:**
    *   Desde el perfil público del donante o desde la lista de tus reseñas, podrás acceder a la opción de editar o eliminar las reseñas que hayas creado.

#### Para Donantes (Visualizar Reseñas)

1.  **Ver tu Perfil Público:**
    *   Tu perfil público estará disponible en una URL como `/perfil-donante/<tu_nombre_de_usuario>/`.
    *   En tu perfil, verás tu calificación promedio general, un desglose visual de las calificaciones por estrella (porcentajes) y las reseñas más recientes que hayas recibido (solo las aprobadas).
2.  **Visualización en Tarjetas de Ítems:**
    *   En las tarjetas de ítems que hayas publicado en la página principal (`/`) o en las páginas de categorías (`/categorias/`), se mostrará una calificación resumida junto a tu nombre de usuario.

#### Para Administradores (Gestionar Reseñas)

1.  **Acceder al Panel de Administración:**
    *   Inicia sesión en el panel de administración de Django (normalmente en `/admin/`).
    *   En la sección "DonaRed", haz clic en "Reseñas".
2.  **Ver y Filtrar Reseñas:**
    *   Verás una lista de todas las reseñas. La columna "Estado" mostrará el estado actual de cada reseña con un color (`Pendiente` en naranjo, `Aprobada` en verde, `Rechazada` en rojo).
    *   Puedes usar los filtros en la barra lateral derecha para buscar reseñas por estado, calificación, fecha de creación, etc. También puedes usar la barra de búsqueda para buscar por nombre de usuario del donante/beneficiario o por comentario.
3.  **Aprobar/Rechazar Reseñas Individualmente:**
    *   Las reseñas con estado **"Pendiente"** son clickeables. Al hacer clic en ellas, serás redirigido a la página de edición de esa reseña.
    *   Desde la página de edición, puedes cambiar el campo "Estado" a "Aprobada" o "Rechazada" y guardar los cambios.
4.  **Aprobar/Rechazar Reseñas en Masa:**
    *   En la vista de lista de reseñas del panel de administración, puedes seleccionar varias reseñas usando las casillas de verificación.
    *   En el menú desplegable "Acción", selecciona "Aprobar reseñas seleccionadas" o "Rechazar reseñas seleccionadas" y haz clic en "Ir" para aplicar la acción a todas las reseñas seleccionadas.

---

### Lógica de Aprobación de Reseñas

Las reseñas tienen un ciclo de vida con tres estados principales:

-   **Pendiente (`pending`):** Este es el estado inicial de cualquier reseña creada por un beneficiario. Las reseñas en este estado **no son visibles** en el perfil público del donante ni contribuyen a sus estadísticas. En el panel de administración, se muestran en color **naranjo** y son clickeables.
-   **Aprobada (`approved`):** Las reseñas en este estado son visibles en el perfil público del donante y se utilizan para calcular su calificación promedio y el desglose por estrellas. En el panel de administración, se muestran en color **verde**.
-   **Rechazada (`rejected`):** Las reseñas en este estado **no son visibles** en el perfil público del donante y no contribuyen a sus estadísticas. En el panel de administración, se muestran en color **rojo**.

**El proceso de aprobación es el siguiente:**

1.  Un beneficiario crea una reseña para una solicitud `COMPLETADA`.
2.  La reseña se guarda con el estado `Pendiente`.
3.  Un administrador debe acceder al panel de administración de Django, navegar a la sección "Reseñas".
4.  El administrador puede identificar rápidamente las reseñas `Pendientes` por su color naranjo.
5.  El administrador puede:
    *   Hacer clic en una reseña `Pendiente` para ver sus detalles y cambiar su estado individualmente a `Aprobada` o `Rechazada`.
    *   Seleccionar múltiples reseñas `Pendientes` y usar las acciones en masa para `Aprobar reseñas seleccionadas` o `Rechazar reseñas seleccionadas`.
6.  Solo después de ser `Aprobada`, la reseña será visible para otros usuarios en el perfil del donante.

---