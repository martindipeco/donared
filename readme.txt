Proyecto DonaRed - Grupo 4 - Acelerador Polo IT 2025

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