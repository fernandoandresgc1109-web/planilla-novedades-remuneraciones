# Pruebas funcionales y de seguridad

## 1. Información general

| Elemento | Detalle |
|---|---|
| Proyecto | Planilla de Novedades de Remuneraciones |
| Fecha de ejecución | 28 de agosto de 2026 |
| Rama evaluada | `test/pruebas-funcionales-seguridad` |
| Entorno | Desarrollo local controlado |
| Base de datos | PostgreSQL |
| Framework | Django 5.2.17 |
| Python | 3.14.7 |
| Navegador principal | Microsoft Edge |
| Datos utilizados | Información completamente ficticia |

## 2. Objetivo

Comprobar el funcionamiento integral de la aplicación antes de su despliegue, verificando autenticación, captura, edición, validación, anulación, exportación, auditoría, API REST, comportamiento adaptable y controles básicos de seguridad.

## 3. Pruebas automáticas

La aplicación cuenta con 72 pruebas automáticas distribuidas de la siguiente forma:

| Módulo | Pruebas |
|---|---:|
| Dominio y administración | 8 |
| API REST | 14 |
| Autenticación y acceso interno | 13 |
| Captura de novedades | 6 |
| Exportación | 8 |
| Gestión de estados | 8 |
| Landing page | 4 |
| Seguridad | 11 |
| **Total** | **72** |

Resultado general:

- `Found 72 test(s).`
- `Ran 72 tests.`
- `OK`.

También se comprobó:

- `System check identified no issues (0 silenced).`
- `No changes detected`.

## 4. Pruebas funcionales manuales

| ID | Comprobación | Resultado |
|---|---|---|
| PF-01 | Acceso público a la landing page | Aprobada |
| PF-02 | Redirección del panel para usuarios no autenticados | Aprobada |
| PF-03 | Rechazo de credenciales incorrectas | Aprobada |
| PF-04 | Inicio de sesión con credenciales válidas | Aprobada |
| PF-05 | Carga del panel y sus indicadores | Aprobada |
| PF-06 | Consulta del listado de novedades | Aprobada |
| PF-07 | Filtro de novedades por estado | Aprobada |
| PF-08 | Búsqueda por RUT del colaborador | Aprobada |
| PF-09 | Acciones disponibles según el estado | Aprobada |
| PF-10 | Carga del formulario de registro | Aprobada |
| PF-11 | Presentación exclusiva de períodos abiertos | Aprobada |
| PF-12 | Rechazo de una novedad sin el monto requerido | Aprobada |
| PF-13 | Registro válido como borrador | Aprobada |
| PF-14 | Edición de una novedad en borrador | Aprobada |
| PF-15 | Validación con registro de usuario y fecha | Aprobada |
| PF-16 | Rechazo de un motivo de anulación demasiado corto | Aprobada |
| PF-17 | Anulación válida con trazabilidad | Aprobada |
| PF-18 | Visualización del motivo de anulación | Aprobada |
| PF-19 | Selección de períodos disponibles para exportar | Aprobada |
| PF-20 | Exportación CSV de novedades validadas | Aprobada |
| PF-21 | Exclusión de novedades anuladas en la exportación | Aprobada |
| PF-22 | Exportación Excel de novedades validadas | Aprobada |
| PF-23 | Registro de cada exportación en el historial | Aprobada |
| PF-24 | Cambio del período al estado exportado | Aprobada |
| PF-25 | Registro de la primera fecha de cierre | Aprobada |
| PF-26 | Reexportación sin modificar la fecha inicial de cierre | Aprobada |
| PF-27 | Cierre seguro de sesión | Aprobada |
| PF-28 | Protección del panel al utilizar el botón Atrás | Aprobada |
| PF-29 | Vista móvil del panel y las novedades | Aprobada |
| PF-30 | Vista móvil del formulario e historial de exportaciones | Aprobada |

## 5. Verificación de archivos exportados

### 5.1 Archivo CSV

Se verificó el archivo `novedades_rancagua_2026_09.csv`.

El archivo contiene:

- Encabezados completos.
- Codificación UTF-8 compatible con Excel.
- Separación mediante punto y coma.
- Una novedad validada de 90 minutos.
- Usuario responsable y fecha de validación.
- Exclusión de la novedad anulada.

### 5.2 Archivo Excel

Se verificó el archivo `novedades_rancagua_2026_09.xlsx`.

El libro contiene:

- Una hoja denominada `Novedades`.
- 18 columnas.
- Una novedad validada.
- Cantidad igual a 90 minutos.
- Usuario `admin_planilla`.
- Fecha de validación.
- Ninguna novedad anulada.
- Ninguna fórmula ni error visible.

## 6. Pruebas de seguridad

### 6.1 Autenticación y sesiones

Se comprobó que:

- Las páginas internas requieren autenticación.
- Las credenciales incorrectas se rechazan con un mensaje genérico.
- El cierre de sesión se realiza mediante una solicitud POST.
- Después del cierre no es posible recuperar el panel mediante la caché.
- Las páginas internas utilizan encabezados que impiden su almacenamiento.
- Las rutas de recuperación de contraseña no implementadas no se encuentran expuestas.

### 6.2 API REST

Se comprobó que:

- Un usuario no autenticado recibe `HTTP 403 Forbidden`.
- La API autenticada presenta los diez recursos previstos.
- Las exportaciones son de solo lectura.
- No se pueden crear, reemplazar, modificar ni eliminar exportaciones manualmente.
- Las novedades no admiten eliminación física.
- Los catálogos protegidos no admiten eliminación mediante la API.

Los métodos permitidos en la API de exportaciones son:

- `GET`.
- `HEAD`.
- `OPTIONS`.

### 6.3 Entradas maliciosas

Las pruebas automáticas comprobaron:

- Escape de contenido XSS almacenado.
- Escape de contenido XSS reflejado.
- Protección de las consultas frente a entradas similares a SQL Injection.
- Validación de cantidades, montos, fechas y estados.
- Protección contra fórmulas peligrosas en CSV y Excel.

### 6.4 Administración

Se bloqueó la eliminación física desde el panel administrativo para:

- Novedades.
- Sucursales.
- Bancos.
- AFP.
- Instituciones de salud.
- Tipos de novedad.

La aplicación conserva estos registros como evidencia histórica o permite desactivarlos cuando corresponda.

### 6.5 Dependencias

Se actualizó la dependencia:

- `sqlparse 0.5.5` a `sqlparse 0.6.0`.

Los resultados fueron:

- `No known vulnerabilities found`.
- `No broken requirements found`.

### 6.6 Análisis estático

Bandit analizó 1.971 líneas de código de producción.

Resultado:

- `No issues identified`.

| Severidad | Hallazgos |
|---|---:|
| Baja | 0 |
| Media | 0 |
| Alta | 0 |

## 7. Configuración para producción

La configuración de seguridad se controla mediante variables de entorno para:

- `DEBUG`.
- Hosts permitidos.
- Redirección obligatoria a HTTPS.
- Cookies de sesión seguras.
- Cookies CSRF seguras.
- HSTS.
- Subdominios HSTS.
- Precarga HSTS.
- Orígenes CSRF confiables.
- Encabezado HTTPS del proxy.
- Ruta de archivos estáticos.

La simulación de la configuración de despliegue produjo:

- `System check identified no issues (0 silenced).`

HSTS deberá habilitarse definitivamente solamente cuando el dominio de producción funcione completamente mediante HTTPS.

## 8. Mejoras realizadas durante las pruebas

Las pruebas permitieron identificar y corregir:

1. Creación, modificación y eliminación manual de exportaciones mediante la API.
2. Exposición de rutas de recuperación de contraseña todavía no implementadas.
3. Almacenamiento en caché de páginas internas.
4. Eliminación de catálogos mediante la API.
5. Eliminación física de novedades y catálogos desde Administración.
6. Falta de visualización del motivo de anulación en el listado interno.
7. Vulnerabilidades conocidas de la versión anterior de `sqlparse`.
8. Configuraciones de producción que todavía no se controlaban mediante variables de entorno.
9. Ajuste adaptable del motivo de anulación en escritorio y dispositivos móviles.

## 9. Alcance pendiente

El control de acceso específico por sucursal y los roles especializados se implementarán después de la sustentación para no ampliar el alcance de la versión académica actual.

Los roles proyectados son:

- Administrador.
- Contabilidad central.
- Operador de sucursal.
- Auditor.

## 10. Conclusión

Las pruebas funcionales, automáticas y de seguridad se completaron satisfactoriamente.

La aplicación:

- Cumple las reglas principales del flujo de novedades.
- Mantiene trazabilidad por usuario y fecha.
- Protege las páginas y la API frente a accesos no autenticados.
- Impide eliminaciones físicas contrarias a las reglas del negocio.
- Exporta exclusivamente información validada.
- Funciona correctamente en escritorio y dispositivos móviles.
- No presenta vulnerabilidades conocidas en sus dependencias.
- No presenta hallazgos en el análisis estático de seguridad.

El proyecto se encuentra preparado para continuar con la documentación final y la configuración del entorno de despliegue.