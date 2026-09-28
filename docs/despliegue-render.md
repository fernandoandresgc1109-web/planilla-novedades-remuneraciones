# Despliegue en Render y Neon

## 1. Objetivo

Este documento registra el despliegue de la aplicación Planilla de Novedades de Remuneraciones, la migración de su base de datos y las verificaciones realizadas en producción.

Aplicación desplegada:

<https://planilla-novedades-remuneraciones.onrender.com/>

El servicio web se ejecuta en Render y la información persistente se almacena en Neon PostgreSQL. El entorno de demostración utiliza exclusivamente datos ficticios para proteger la información personal, bancaria, previsional y salarial.

## 2. Arquitectura desplegada

1. El navegador accede mediante HTTPS.
2. Render ejecuta la aplicación con Gunicorn.
3. Django procesa la interfaz, autenticación y API REST.
4. WhiteNoise entrega los archivos estáticos.
5. Neon PostgreSQL 18 conserva la información.
6. La aplicación utiliza una conexión agrupada a PostgreSQL mediante `DATABASE_URL`.
7. GitHub activa los despliegues desde la rama `main`.

## 3. Infraestructura

| Proveedor | Recurso | Configuración |
|---|---|---|
| GitHub | Repositorio | `fernandoandresgc1109-web/planilla-novedades-remuneraciones` |
| GitHub | Rama de producción | `main` |
| Render | Blueprint | `planilla-novedades-remuneraciones` |
| Render | Servicio web | `planilla-novedades-remuneraciones` |
| Render | Runtime | Python 3.14.7 |
| Render | Plan web | Free |
| Render | Región | Virginia |
| Neon | Proyecto PostgreSQL | `planilla-novedades-remuneraciones` |
| Neon | Rama de datos | `production` |
| Neon | Base de datos | `neondb` |
| Neon | Motor | PostgreSQL 18 |
| Neon | Plan | Free |
| Neon | Región | AWS US East 1 (N. Virginia) |
| Neon | Conexión agrupada | Habilitada |

## 4. Archivos de configuración

| Archivo | Función |
|---|---|
| `.python-version` | Fija Python 3.14.7. |
| `requirements.txt` | Incluye Gunicorn y WhiteNoise. |
| `build.sh` | Instala dependencias, recopila estáticos y aplica migraciones. |
| `render.yaml` | Declara el servicio web y las variables de entorno. |
| `.gitattributes` | Mantiene `build.sh` con finales de línea LF. |
| `config/settings.py` | Configura PostgreSQL, HTTPS y WhiteNoise. |

Comando de inicio: `python -m gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`.

El proceso de construcción instala las dependencias, ejecuta `collectstatic` y aplica las migraciones. La base de datos no se declara como recurso de Render en `render.yaml`; `DATABASE_URL` utiliza `sync: false` y su valor se configura de forma privada en el panel de Render.

## 5. Variables de entorno

Los valores secretos no se guardan en el repositorio.

| Variable | Propósito |
|---|---|
| `DATABASE_URL` | Conexión agrupada y cifrada con Neon PostgreSQL. |
| `DJANGO_SECRET_KEY` | Clave generada por Render. |
| `DJANGO_DEBUG` | Mantiene la depuración desactivada. |
| `DJANGO_SECURE_SSL_REDIRECT` | Redirige a HTTPS. |
| `DJANGO_SESSION_COOKIE_SECURE` | Protege la cookie de sesión. |
| `DJANGO_CSRF_COOKIE_SECURE` | Protege la cookie CSRF. |
| `DJANGO_SECURE_HSTS_SECONDS` | Activa HSTS. |
| `DJANGO_TRUST_X_FORWARDED_PROTO` | Reconoce el proxy HTTPS. |
| `RENDER_EXTERNAL_HOSTNAME` | Autoriza el dominio de Render. |

Las contraseñas, claves y cadenas de conexión nunca se almacenan en Git. Las credenciales temporales se eliminaron del entorno local y del portapapeles después de las comprobaciones.

## 6. Despliegue inicial en Render

1. Se creó la rama `chore/despliegue-render`.
2. Se incorporaron los ajustes de producción.
3. Se ejecutaron las comprobaciones locales.
4. El commit `0718ca2` se envió a GitHub.
5. El pull request 10 se fusionó mediante `ef3e043`.
6. Se conectó Render con el repositorio.
7. Se creó el Blueprint desde `render.yaml`.
8. Render creó inicialmente PostgreSQL y el servicio web.
9. Se aplicaron las migraciones y archivos estáticos.
10. Se creó el superusuario en PostgreSQL de producción.
11. Las credenciales temporales se eliminaron de PowerShell y Render.

## 7. Migración de Render PostgreSQL a Neon

La base gratuita de Render tenía fecha de expiración el 28 de septiembre de 2026. La migración se realizó el 24 de septiembre de 2026, antes del vencimiento.

1. Se instaló y verificó PostgreSQL Client 18.4 en Windows.
2. Se creó un respaldo personalizado con `pg_dump`.
3. El respaldo se validó con `pg_restore --list`; contenía 190 entradas.
4. Se creó un proyecto Neon Free con PostgreSQL 18 en N. Virginia.
5. Se comprobó la conexión al destino antes de restaurar.
6. Se restauró el respaldo con `pg_restore`, sin transferir propietarios ni ACL.
7. Se verificó la existencia de las 21 tablas públicas.
8. Se comprobaron cantidades representativas de registros.
9. Django se conectó localmente a Neon y `python manage.py check` no informó problemas.
10. Se habilitó la conexión agrupada de Neon.
11. `DATABASE_URL` se reemplazó manualmente en Render sin exponer su valor.
12. El Blueprint dejó de declarar la base de datos de Render.
13. El cambio se integró mediante el pull request 13 y el commit `f01a320`.
14. Render completó el despliegue y Neon registró actividad de conexión.
15. Las variables y credenciales temporales se eliminaron del equipo local.

Se conserva fuera del repositorio el respaldo `planilla-render-2026-09-24.dump`.

## 8. Comprobaciones técnicas

| Comprobación | Resultado |
|---|---|
| `python manage.py check` | Sin problemas. |
| `python manage.py makemigrations --check --dry-run` | Sin cambios pendientes. |
| `python manage.py test` | 72 pruebas aprobadas antes del despliegue inicial. |
| `collectstatic` | Manifiesto generado. |
| `python -m pip check` | Sin dependencias rotas. |
| `git diff --cached --check` | Sin errores. |
| Formato de `build.sh` | LF confirmado. |
| Conexión de Django con Neon | Correcta. |
| Tablas restauradas en Neon | 21. |
| Despliegue posterior a la migración | Live. |

## 9. Verificación de la migración

Las cantidades verificadas inmediatamente después de restaurar el respaldo fueron:

| Entidad | Cantidad |
|---|---:|
| Usuarios | 3 |
| Sucursales | 3 |
| Perfiles | 3 |
| Colaboradores | 2 |
| Períodos | 6 |
| Tipos de novedad | 3 |
| Novedades | 8 |
| Exportaciones | 6 |

También se comprobaron la landing, autenticación, panel interno, administración, aislamiento por sucursal, consulta de novedades, API REST y exportaciones.

## 10. Lighthouse móvil

Resultados obtenidos durante la verificación inicial de producción:

| Categoría | Puntaje | Meta |
|---|---:|---:|
| Rendimiento | 100 | 80 |
| Accesibilidad | 95 | 80 |
| Buenas prácticas | 100 | 80 |
| SEO | 100 | 80 |

Todas las categorías superaron la meta mínima del proyecto.

## 11. Privacidad y respaldo

La base contiene exclusivamente información ficticia de demostración. No se utilizaron datos laborales reales.

El respaldo de migración se almacena localmente y no se publica en GitHub. Ninguna contraseña, cadena de conexión o dirección privada forma parte del repositorio.

## 12. Limitaciones

- Render suspende el servicio web gratuito después de un período sin tráfico; la primera solicitud posterior puede tardar cerca de un minuto.
- Neon Free escala el cómputo a cero cuando no hay actividad, por lo que una conexión posterior puede experimentar un breve arranque.
- Ambos planes gratuitos están sujetos a límites mensuales de uso.
- El sistema conserva un respaldo manual externo, pero no implementa todavía una política automática de copias periódicas.
- La infraestructura es académica y de demostración.

Referencias oficiales:

- <https://render.com/docs/free>
- <https://neon.com/pricing>

## 13. Resultado

La aplicación quedó operativa con HTTPS, autenticación, API REST, archivos estáticos, aislamiento multi-sucursal, validación y exportación Excel. El servicio web continúa en Render y los datos persistentes funcionan en Neon PostgreSQL mediante conexión agrupada. La migración eliminó la dependencia de la base gratuita de Render que expiraba a los 30 días.
