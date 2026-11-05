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

- Crear el proyecto Android con Kotlin y Jetpack Compose.
- Implementar la pantalla de inicio de sesión.
- Conectar Android con las rutas de autenticación.
- Crear el panel y los listados móviles.
- Permitir el registro de novedades según el rol.
- Incorporar pruebas de la aplicación Android.
- Actualizar el README y preparar las evidencias de la entrega.
