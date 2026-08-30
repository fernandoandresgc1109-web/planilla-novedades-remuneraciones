# Despliegue en Render

## 1. Objetivo

Este documento registra el despliegue de la aplicación Planilla de Novedades de Remuneraciones en Render y las verificaciones realizadas en producción.

Aplicación desplegada:

<https://planilla-novedades-remuneraciones.onrender.com/>

El despliegue utiliza exclusivamente datos ficticios para proteger la información personal, bancaria, previsional y salarial.

## 2. Arquitectura desplegada

1. El navegador accede mediante HTTPS.
2. Render ejecuta la aplicación con Gunicorn.
3. Django procesa la interfaz, autenticación y API REST.
4. WhiteNoise entrega los archivos estáticos.
5. PostgreSQL 18 conserva la información.
6. GitHub activa los despliegues desde la rama `main`.

## 3. Recursos de Render

| Recurso | Configuración |
|---|---|
| Blueprint | `planilla-novedades-remuneraciones` |
| Repositorio | `fernandoandresgc1109-web/planilla-novedades-remuneraciones` |
| Rama | `main` |
| Servicio web | `planilla-novedades-remuneraciones` |
| Runtime | Python 3.14.7 |
| Plan web | Free |
| Región | Virginia |
| Base de datos | `planilla-novedades-db` |
| Motor | PostgreSQL 18 |
| Plan de base de datos | Free |
| Expiración de la base de datos | 28 de septiembre de 2026 |

## 4. Configuración

| Archivo | Función |
|---|---|
| `.python-version` | Fija Python 3.14.7. |
| `requirements.txt` | Incluye Gunicorn y WhiteNoise. |
| `build.sh` | Instala dependencias, recopila estáticos y aplica migraciones. |
| `render.yaml` | Declara los recursos y variables de entorno. |
| `.gitattributes` | Mantiene `build.sh` con finales de línea LF. |
| `config/settings.py` | Configura PostgreSQL, HTTPS y WhiteNoise. |

Comando de inicio: `python -m gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`.

El proceso de construcción instala las dependencias, ejecuta `collectstatic` y aplica las migraciones.

## 5. Variables de entorno

Los valores secretos no se guardan en el repositorio.

| Variable | Propósito |
|---|---|
| `DATABASE_URL` | Conexión privada con PostgreSQL. |
| `DJANGO_SECRET_KEY` | Clave generada por Render. |
| `DJANGO_DEBUG` | Mantiene la depuración desactivada. |
| `DJANGO_SECURE_SSL_REDIRECT` | Redirige a HTTPS. |
| `DJANGO_SESSION_COOKIE_SECURE` | Protege la cookie de sesión. |
| `DJANGO_CSRF_COOKIE_SECURE` | Protege la cookie CSRF. |
| `DJANGO_SECURE_HSTS_SECONDS` | Activa HSTS. |
| `DJANGO_TRUST_X_FORWARDED_PROTO` | Reconoce el proxy HTTPS. |
| `RENDER_EXTERNAL_HOSTNAME` | Autoriza el dominio de Render. |

La contraseña del administrador nunca se almacena en `render.yaml`. Después de crear el administrador, su valor temporal se eliminó de Render.

## 6. Proceso realizado

1. Se creó la rama `chore/despliegue-render`.
2. Se incorporaron los ajustes de producción.
3. Se ejecutaron las comprobaciones locales.
4. El commit `0718ca2` se envió a GitHub.
5. El pull request 10 se fusionó mediante `ef3e043`.
6. Se conectó Render con el repositorio.
7. Se creó el Blueprint desde `render.yaml`.
8. Render creó PostgreSQL y el servicio web.
9. Se aplicaron las migraciones y archivos estáticos.
10. Se creó el superusuario en PostgreSQL de producción.
11. La conexión externa se eliminó de PowerShell.
12. La contraseña temporal se eliminó de Render.

No se registraron contraseñas, claves ni direcciones privadas en Git.

## 7. Comprobaciones previas

| Comprobación | Resultado |
|---|---|
| `python manage.py check` | Sin problemas. |
| `python manage.py makemigrations --check --dry-run` | Sin cambios pendientes. |
| `python manage.py test` | 72 pruebas aprobadas. |
| `collectstatic` | Manifiesto generado. |
| `python -m pip check` | Sin dependencias rotas. |
| `git diff --cached --check` | Sin errores. |
| Formato de `build.sh` | LF confirmado. |

## 8. Verificación en producción

Se verificaron correctamente:

- Landing page, estilos y HTTPS.
- Inicio de sesión y panel interno.
- Administración de Django.
- API REST autenticada.
- Consulta de cuatro novedades ficticias.
- Validaciones de los formularios.
- Tres novedades validadas.
- Una novedad conservada en borrador.
- Exportación Excel de agosto de 2026.
- Cambio automático de agosto a Exportado.

| Indicador | Cantidad |
|---|---:|
| Colaboradores activos | 1 |
| Períodos abiertos | 1 |
| Novedades en borrador | 1 |
| Novedades validadas | 3 |

## 9. Lighthouse móvil

| Categoría | Puntaje | Meta |
|---|---:|---:|
| Rendimiento | 100 | 80 |
| Accesibilidad | 95 | 80 |
| Buenas prácticas | 100 | 80 |
| SEO | 100 | 80 |

Todas las categorías superaron la meta mínima del proyecto.

## 10. Datos de demostración

La base contiene solamente una sucursal, un colaborador, un contrato, dos períodos, dos tipos de novedad, cuatro novedades y una exportación Excel ficticios.

No se utilizaron datos laborales reales.

## 11. Limitaciones

- El servicio gratuito puede suspenderse por inactividad.
- La primera solicitud puede tardar 50 segundos o más.
- PostgreSQL expira el 28 de septiembre de 2026 si no se cambia de plan.
- La infraestructura es exclusivamente académica.

Estas limitaciones no afectan la presentación del 2 de septiembre de 2026.

## 12. Resultado

La aplicación quedó operativa con HTTPS, PostgreSQL, autenticación, API REST, archivos estáticos, validación y exportación Excel. Las pruebas y Lighthouse confirman el cumplimiento de los objetivos técnicos.
