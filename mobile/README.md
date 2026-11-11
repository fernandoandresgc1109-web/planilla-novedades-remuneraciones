# Aplicación Android de Planilla de Novedades

Esta carpeta contiene el cliente Android nativo del sistema. La aplicación no reemplaza el backend: se conecta mediante HTTPS a la API REST de Django y utiliza la misma base de datos PostgreSQL que la interfaz web.

## Funcionalidad de esta etapa

- Pantalla de inicio de sesión desarrollada con Jetpack Compose.
- Conexión con la ruta /api/autenticacion/iniciar/.
- Envío automático del token en el encabezado Authorization.
- Conservación cifrada del token en el dispositivo.
- Recuperación de la sesión al volver a abrir la aplicación.
- Visualización del usuario, rol, sucursal y permisos.
- Cierre de sesión local y en el servidor.
- Panel principal móvil con acceso a las funciones disponibles.
- Listado de colaboradores filtrado por los permisos de Django.
- Búsqueda local por nombre, RUT o sucursal.
- Listado de novedades filtrado por los permisos de Django.
- Búsqueda de novedades por persona, RUT, tipo, período, sucursal o estado.
- Presentación del monto, cantidad, fechas, observación y estado del registro.
- Consulta automática de todas las páginas de resultados.
- Tiempo de espera ampliado para el inicio en frío de Render.

## Cómo abrir el proyecto

1. Instalar Android Studio.
2. Seleccionar Open y elegir la carpeta mobile.
3. Esperar la sincronización de Gradle.
4. Crear un emulador o conectar un teléfono con Android 8.0 o superior.
5. Ejecutar el módulo app.

La URL pública del backend se define como API_BASE_URL en app/build.gradle.kts. No contiene contraseñas ni secretos.

La primera solicitud puede tardar porque el servicio gratuito de Render se suspende cuando no tiene actividad.

GitHub Actions ejecuta las pruebas unitarias y compila un APK de depuración en cada pull request que modifica la carpeta móvil.

## Explicación sencilla

La pantalla móvil envía el usuario y la contraseña al servidor Django. Si los datos son correctos, el servidor entrega un token. El teléfono guarda ese token cifrado y lo incluye en las siguientes solicitudes. Django sigue siendo responsable de comprobar el rol y la sucursal, por lo que la aplicación móvil no puede saltarse las reglas del sistema.

Después de iniciar sesión, el panel permite consultar colaboradores y novedades. Android solicita la información a la API y Django devuelve únicamente los registros autorizados para el usuario. Los buscadores trabajan sobre la información recibida y los nombres de la sucursal, la persona, el período y el tipo de novedad se entregan como datos de solo lectura para facilitar la comprensión.
