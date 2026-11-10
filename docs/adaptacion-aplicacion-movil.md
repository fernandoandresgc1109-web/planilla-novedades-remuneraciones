# Adaptación de la aplicación para Android

## 1. Propósito

La aplicación web continuará siendo el sistema central para administrar las novedades de remuneración. La nueva aplicación Android funcionará como un cliente móvil que se conectará a la API REST existente.

Este enfoque permite reutilizar las reglas de negocio, la base de datos, los usuarios, los roles y el aislamiento entre sucursales sin construir nuevamente todo el sistema.

## 2. Arquitectura propuesta

```text
Aplicación Android -> API REST de Django -> PostgreSQL en Neon
                          ^
                          |
                 Interfaz web y Django Admin
```

- **Android:** interfaz móvil desarrollada con Kotlin y Jetpack Compose.
- **Django REST Framework:** valida las solicitudes y aplica los permisos.
- **PostgreSQL en Neon:** conserva la información centralizada.
- **Render:** publica el backend mediante HTTPS.
- **GitHub:** registra el código, la documentación y el historial de cambios.

## 3. Primera etapa: autenticación móvil

La API web utilizaba inicialmente sesiones y cookies del navegador. Para que Android pueda identificarse de manera independiente, se agregó autenticación por token sin retirar la autenticación por sesión utilizada por la aplicación web.

### Rutas incorporadas

| Método | Ruta | Función |
|---|---|---|
| `POST` | `/api/autenticacion/iniciar/` | Valida usuario y contraseña y entrega un token. |
| `GET` | `/api/autenticacion/usuario/` | Devuelve usuario, rol, sucursal y permisos. |
| `POST` | `/api/autenticacion/cerrar/` | Invalida el token del dispositivo. |

Las demás rutas de la API aceptan el encabezado:

```text
Authorization: Token TOKEN_DEL_USUARIO
```

## 4. Seguridad

- Las credenciales solo se envían al iniciar sesión mediante HTTPS.
- El token identifica al usuario en las solicitudes posteriores.
- El cierre de sesión elimina el token del servidor. Como esta primera versión utiliza un token por usuario, también se cerrará el acceso en cualquier otro dispositivo que estuviera utilizando el mismo token.
- Los permisos siguen siendo aplicados por Django, no por el teléfono.
- Un operador conserva acceso únicamente a su sucursal.
- Contabilidad continúa con acceso de solo lectura y exportación.
- La aplicación Android no debe incluir contraseñas ni variables secretas dentro del código.
- En Android, el token deberá almacenarse mediante un mecanismo cifrado.

## 5. Pruebas automatizadas

La etapa incorpora pruebas para comprobar:

1. Inicio de sesión correcto.
2. Rechazo de contraseñas incorrectas.
3. Consulta del usuario mediante token.
4. Acceso del token a los endpoints existentes.
5. Conservación del aislamiento por sucursal.
6. Bloqueo de solicitudes no autenticadas.
7. Invalidación del token al cerrar sesión.

## 6. Explicación sencilla para la sustentación

> La aplicación web y la aplicación móvil no tendrán bases de datos separadas. Las dos se conectarán al mismo backend de Django. El teléfono enviará las solicitudes a la API mediante HTTPS y utilizará un token para demostrar qué usuario inició sesión. Django comprobará el rol y la sucursal antes de entregar o modificar información. Así se reutiliza el sistema existente y se mantiene el aislamiento de los datos.

## 7. Próximas etapas

- Crear los listados móviles de períodos, colaboradores y novedades.
- Incorporar navegación entre las funciones móviles.
- Permitir el registro de novedades según el rol.
- Incorporar pruebas de la aplicación Android.
- Actualizar el README y preparar las evidencias de la entrega.

## 8. Segunda etapa: cliente Android inicial

El proyecto nativo se encuentra en la carpeta `mobile` y utiliza Kotlin con Jetpack Compose. La primera pantalla permite iniciar sesión con las mismas credenciales de la aplicación web.

Después de una autenticación correcta, el cliente:

1. Guarda el token cifrado en el dispositivo.
2. Agrega el encabezado `Authorization` a las solicitudes protegidas.
3. Recupera la sesión cuando se vuelve a abrir la aplicación.
4. Muestra el usuario, el rol, la sucursal y los permisos entregados por Django.
5. Elimina el token local y el token del servidor al cerrar sesión.

La aplicación solo permite conexiones HTTPS y no contiene contraseñas, credenciales de base de datos ni llaves privadas en el código.

GitHub Actions ejecuta automáticamente las pruebas unitarias y la compilación del APK cuando se propone un cambio en la aplicación móvil.

### Estructura principal

| Carpeta o archivo | Responsabilidad |
|---|---|
| `data/model` | Representa los datos recibidos desde Django. |
| `data/remote` | Define las rutas de la API y agrega el token. |
| `data/repository` | Coordina el inicio, recuperación y cierre de sesión. |
| `data/session` | Guarda el token cifrado. |
| `ui/auth` | Mantiene el estado de autenticación. |
| `ui/PlanillaApp.kt` | Presenta las pantallas de acceso y bienvenida. |

### Explicación para la sustentación

> Primero preparé Django para aceptar tokens y después construí un cliente Android nativo. La aplicación móvil envía las credenciales por HTTPS, recibe un token y lo guarda cifrado. En cada solicitud, Django identifica al usuario y aplica las reglas de rol y sucursal. Por eso la seguridad sigue centralizada en el servidor y no depende únicamente del teléfono.
