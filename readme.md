# 🤝 DonaRed

**Conectando generosidad con necesidad**

DonaRed es una plataforma web que facilita las donaciones entre personas, creando una red solidaria donde quienes tienen algo que ya no necesitan pueden ayudar a quienes más lo requieren. Un objeto olvidado puede ser un gran cambio para otra persona.

🌐 **[Ver aplicación en vivo](https://donared.pythonanywhere.com/)**

![DonaRed Homepage](ruta/a/captura/homepage.png)

## ✨ Características Principales

### Para Donantes
- **Publicación de donaciones**: Sube fotos y descripción de los artículos que deseas donar
- **Gestión de perfil**: Edita tu información personal y preferencias
- **Categorización**: Organiza tus donaciones por categorías (Ropa, Tecnología, Libros, Herramientas, Bicicletas, Muebles)
- **Notificaciones**: Recibe alertas cuando alguien está interesado en tus donaciones

### Para Receptores
- **Exploración por categorías**: Busca donaciones según tus necesidades
- **Mapa interactivo**: Localiza donaciones cercanas a tu ubicación
- **Sistema de solicitudes**: Solicita los artículos que necesitas
- **Notificaciones**: Mantente informado sobre nuevas donaciones disponibles

### Funcionalidades Generales
- **Registro y autenticación**: Sistema seguro de usuarios
- **Geolocalización**: Visualización de donaciones en mapa usando OpenStreetMap
- **Sección de novedades**: Noticias y contenido relacionado con donaciones y solidaridad
- **Moderación**: Sistema de validación de contenido a través del panel administrativo
- **Responsive**: Adaptado para dispositivos móviles y escritorio

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python 3.13.3 + Django 5.2
- **Frontend**: HTML5, CSS3, JavaScript
- **Base de datos**: SQLite3
- **Mapas**: OpenStreetMap API
- **Geolocalización**: GeoPy + Geographiclib
- **Manejo de números telefónicos**: django-phonenumber-field
- **Deployment**: PythonAnywhere

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.13.3 o superior
- pip (gestor de paquetes de Python)
- Git

### Instalación Local

1. **Clona el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/donared.git
   cd donared
   ```

2. **Crea un entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instala las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura las variables de entorno**
   Crea un archivo `.env` en la raíz del proyecto:
   ```
   DONARED=tu_clave_secreta_aqui
   DEBUG=True
   ```

5. **Ejecuta las migraciones**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Crea un superusuario (opcional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Inicia el servidor de desarrollo**
   ```bash
   python manage.py runserver
   ```

8. **Accede a la aplicación**
   Abre tu navegador en `http://127.0.0.1:8000`

### Configuración de Producción

Para deployment en producción, asegúrate de:
- Configurar `DEBUG = False`
- Establecer `ALLOWED_HOSTS` apropiadamente
- Configurar variables de entorno de forma segura
- Usar una base de datos más robusta (PostgreSQL recomendado)

## 📱 Capturas de Pantalla

### Página Principal
![Homepage](ruta/a/captura/homepage.png)

### Mapa de Donaciones
![Mapa](ruta/a/captura/mapa.png)

### Perfil de Usuario
![Perfil](ruta/a/captura/perfil.png)

### Publicar Donación
![Publicar](ruta/a/captura/publicar.png)

## 🗂️ Estructura del Proyecto

```
donared/
├── donaredapp/          # Aplicación principal
├── novedades/           # Módulo de noticias
├── geo/                 # Módulo de geolocalización
├── templates/           # Plantillas HTML
├── staticfiles/         # Archivos estáticos
├── media/              # Archivos multimedia subidos
├── requirements.txt    # Dependencias del proyecto
└── manage.py          # Script de gestión de Django
```

## 👥 Equipo de Desarrollo

Este proyecto fue desarrollado como parte del **Acelerador Polo IT** de la Ciudad de Buenos Aires, Argentina.

**Desarrolladores:**
- **Cecilia Ferreyra** - Desarrollo Full Stack
- **Franco Rotella** - Desarrollo Full Stack  
- **Agustín Pino** - Desarrollo Full Stack
- **Martín Di Peco** - Desarrollo Full Stack

## 🌟 Sobre el Proyecto

DonaRed nace de la necesidad de crear conexiones solidarias en nuestra comunidad. Creemos que la tecnología puede ser un puente para que la generosidad de unos llegue a quienes más lo necesitan, creando una red de apoyo mutuo y fomentando la economía circular.

### Impacto Social
- Reducción de desperdicio mediante la reutilización
- Fortalecimiento de lazos comunitarios
- Facilita el acceso a bienes para personas en situación de vulnerabilidad
- Promueve la cultura de la donación y el intercambio solidario

## 🔧 API y Funcionalidades Técnicas

### Límites de la Aplicación
- **Tamaño máximo de imágenes**: 2MB
- **Formatos de imagen soportados**: JPG, PNG, GIF
- **Cobertura geográfica**: Configurable por región

### Configuraciones de Seguridad
- Validación de formularios con CSRF protection
- Autenticación segura de usuarios
- Moderación de contenido mediante panel administrativo
- Logs de actividad para monitoreo

## 🤝 Contribuir

Agradecemos las contribuciones a DonaRed. Si deseas colaborar:

1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Contacto

¿Tienes preguntas o sugerencias? Contáctanos:
- **Email**: donareddonared@gmail.com
- **Web**: [https://donared.pythonanywhere.com/](https://donared.pythonanywhere.com/)

---

**Desarrollado con 💙 en Buenos Aires, Argentina**

*Parte del Acelerador Polo IT - Gobierno de la Ciudad de Buenos Aires*