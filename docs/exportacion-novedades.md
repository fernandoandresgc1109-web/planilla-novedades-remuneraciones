# Módulo de Exportación de Novedades

## 1. Propósito

El módulo de exportación permite preparar la información validada de un período de liquidación para continuar con el proceso contable y de remuneraciones.

Los usuarios autenticados pueden seleccionar un período y descargar sus novedades validadas en alguno de los siguientes formatos:

- CSV.
- Excel XLSX.

La generación del archivo se realiza directamente en memoria. El sistema no almacena copias de los documentos exportados en carpetas públicas ni en la base de datos.

## 2. Alcance

El módulo permite:

- Consultar los períodos que contienen novedades validadas.
- Seleccionar el formato de descarga.
- Generar archivos CSV.
- Generar archivos Excel XLSX.
- Bloquear períodos que todavía contienen borradores.
- Excluir novedades anuladas.
- Registrar quién realizó cada exportación.
- Registrar la fecha, formato, nombre y cantidad de registros.
- Cambiar el período al estado `EXPORTADO`.
- Conservar la primera fecha de cierre.
- Volver a generar una copia de un período exportado.
- Consultar las últimas diez exportaciones realizadas.

## 3. Ruta principal

La interfaz se encuentra disponible en:

```text
/exportaciones/
```

Su nombre dentro del sistema de rutas de Django es:

```text
novedades:exportar_novedades
```

La ruta está protegida con el decorador `login_required`.

Un usuario sin sesión autenticada es redirigido a:

```text
/cuentas/login/?next=/exportaciones/
```

Después de iniciar sesión, Django lo devuelve al módulo solicitado.

## 4. Dependencia para Excel

Para generar archivos XLSX se incorporó:

```text
openpyxl==3.1.5
```

Esta biblioteca permite crear libros de Excel directamente desde Python sin necesidad de instalar Microsoft Excel en el servidor.

También se registró su dependencia:

```text
et_xmlfile==2.0.0
```

Ambas versiones quedaron incorporadas en:

```text
requirements.txt
```

## 5. Formatos disponibles

Los formatos se obtienen desde las opciones definidas en el modelo `Exportacion`:

| Valor interno | Nombre mostrado | Extensión |
|---|---|---|
| `CSV` | CSV | `.csv` |
| `XLSX` | Excel | `.xlsx` |

El formato no se recibe como un texto libre. Django valida que corresponda a una de las opciones permitidas.

## 6. Reglas de exportación

Para que un período pueda exportarse debe cumplir estas reglas:

1. Debe contener al menos una novedad validada.
2. No puede contener novedades en borrador.
3. Las novedades anuladas no se incluyen.
4. El usuario debe tener una sesión autenticada.
5. El formato debe ser CSV o XLSX.

La existencia de una novedad en borrador bloquea la exportación completa del período.

Esto evita entregar a contabilidad información que todavía se encuentra pendiente de revisión.

## 7. Selección de períodos

El formulario utiliza un `ModelChoiceField`.

Su conjunto de opciones se construye con los períodos que contienen al menos una novedad en estado:

```text
VALIDADA
```

La consulta utiliza:

- Relaciones de Django ORM.
- `select_related` para la sucursal.
- `distinct` para evitar períodos repetidos.
- Orden descendente por año y mes.

Aunque un período aparezca en el selector, el servidor vuelve a comprobar sus reglas cuando recibe la solicitud.

## 8. Flujo general

El proceso funciona de la siguiente manera:

1. El usuario abre `/exportaciones/`.
2. Django comprueba que exista una sesión autenticada.
3. El formulario consulta los períodos que tienen novedades validadas.
4. El usuario selecciona el período.
5. El usuario selecciona CSV o Excel.
6. El formulario comprueba que no existan borradores.
7. La vista vuelve a consultar la información dentro de una transacción.
8. Se seleccionan solamente las novedades validadas.
9. Se ordenan los registros por colaborador y tipo de novedad.
10. El archivo se genera en memoria.
11. Se crea un registro de auditoría en `Exportacion`.
12. El período cambia al estado `EXPORTADO`.
13. Se registra la fecha de cierre si todavía no existía.
14. Django entrega el archivo al navegador.

## 9. Columnas exportadas

Los dos formatos contienen las mismas 18 columnas:

| Número | Columna | Contenido |
|---:|---|---|
| 1 | Sucursal | Nombre de la sucursal |
| 2 | Año | Año del período |
| 3 | Mes | Mes del período |
| 4 | RUT | Identificador del colaborador |
| 5 | Nombres | Nombres del colaborador |
| 6 | Apellidos | Apellidos del colaborador |
| 7 | Código de novedad | Código del tipo de novedad |
| 8 | Tipo de novedad | Nombre descriptivo |
| 9 | Unidad | Pesos, días, minutos o registro |
| 10 | Naturaleza | Haber, descuento, asistencia o informativo |
| 11 | Fecha de inicio | Fecha inicial del evento |
| 12 | Fecha de término | Fecha final del evento |
| 13 | Cantidad | Cantidad registrada |
| 14 | Monto | Monto monetario |
| 15 | Observación | Información adicional |
| 16 | Estado | Estado de la novedad |
| 17 | Validado por | Usuario que validó |
| 18 | Validado en | Fecha y hora de validación |

Los campos opcionales sin información se exportan como valores vacíos.

## 10. Generación del archivo CSV

El archivo CSV se genera con el módulo estándar `csv` de Python.

Sus características son:

- Codificación UTF-8.
- Marca BOM para facilitar la apertura en Excel.
- Separador por punto y coma.
- Encabezados en la primera fila.
- Una fila por cada novedad validada.
- Saltos de línea normalizados.

El tipo de contenido enviado por Django es:

```text
text/csv; charset=utf-8
```

Ejemplo del nombre generado:

```text
novedades_rancagua_2026_08.csv
```

## 11. Generación del archivo Excel

El archivo XLSX se genera con OpenPyXL.

Incluye:

- Hoja llamada `Novedades`.
- Encabezados con fondo verde.
- Encabezados en negrita y texto blanco.
- Fila superior inmovilizada.
- Filtros automáticos.
- Ajuste de ancho de columnas.
- Formato decimal para cantidades.
- Formato numérico para montos.
- Propiedades básicas del documento.

El tipo de contenido enviado por Django es:

```text
application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
```

Ejemplo del nombre generado:

```text
novedades_rancagua_2026_08.xlsx
```

## 12. Generación en memoria

Los documentos se construyen utilizando:

- `StringIO` para CSV.
- `BytesIO` para Excel.

El archivo se entrega mediante `HttpResponse`.

No se utiliza un `FileField` y no se crea una copia permanente dentro del proyecto.

Esto reduce el riesgo de:

- Exponer archivos mediante rutas públicas.
- Acumular información sensible en el servidor.
- Mantener versiones desactualizadas.
- Publicar accidentalmente documentos en Git.

## 13. Nombre seguro del archivo

El código de la sucursal se procesa con `slugify`.

De esta manera, el nombre utiliza caracteres seguros y una estructura predecible:

```text
novedades_{sucursal}_{año}_{mes}.{extensión}
```

Si el código no puede convertirse en un nombre válido, se utiliza el identificador de la sucursal.

## 14. Protección contra fórmulas

Los archivos CSV y Excel pueden interpretar algunos textos como fórmulas si comienzan con:

```text
=
+
-
@
```

Para reducir el riesgo de inyección de fórmulas, el exportador agrega un apóstrofo a estos valores antes de incorporarlos al archivo.

Por ejemplo:

```text
=2+2
```

se exporta como:

```text
'=2+2
```

Así se conserva el contenido como texto y no como una instrucción ejecutable por la hoja de cálculo.

## 15. Transacción y consistencia

La exportación utiliza:

```python
transaction.atomic()
```

El período se consulta con:

```python
select_for_update()
```

También se bloquean temporalmente las novedades existentes del período mientras se prepara la exportación.

Dentro de la transacción se vuelve a comprobar:

- Si existen borradores.
- Si existe al menos una novedad validada.
- Cuántos registros serán exportados.

La auditoría y el cambio de estado se realizan dentro de la misma operación.

Si ocurre un error antes de completar el proceso, Django revierte las modificaciones realizadas en la transacción.

## 16. Auditoría de exportaciones

Cada descarga correcta crea un registro en el modelo `Exportacion`.

Se almacenan:

| Campo | Descripción |
|---|---|
| `periodo` | Período exportado |
| `generado_por` | Usuario autenticado |
| `fecha_generacion` | Fecha y hora automática |
| `formato` | CSV o XLSX |
| `nombre_archivo` | Nombre entregado al navegador |
| `cantidad_registros` | Cantidad de novedades incluidas |

La base de datos conserva la metadata de auditoría, pero no almacena el contenido del archivo.

## 17. Cambio de estado del período

Después de una descarga correcta, el período cambia a:

```text
EXPORTADO
```

Si `fecha_cierre` está vacía, se registra la fecha y hora actuales.

Si el período ya tenía una fecha de cierre, esta se conserva.

La exportación bloqueada por borradores no cambia el estado ni la fecha del período.

## 18. Reexportación

Un período exportado puede volver a descargarse.

Cada nueva descarga:

- Genera nuevamente la información validada.
- Crea un nuevo registro de auditoría.
- Conserva la primera fecha de cierre.
- Mantiene el estado `EXPORTADO`.

Esto permite obtener otra copia sin almacenar archivos antiguos en el servidor.

## 19. Encabezados de seguridad

La respuesta incorpora:

```text
X-Content-Type-Options: nosniff
```

Este encabezado evita que el navegador intente interpretar el archivo como un tipo de contenido diferente.

También utiliza:

```text
Cache-Control: no-store, private
```

Esto indica que la respuesta no debe almacenarse en cachés compartidas.

## 20. Protección CSRF

El formulario utiliza:

```django
{% csrf_token %}
```

La solicitud que genera el archivo se realiza mediante `POST`.

Django comprueba el token antes de procesar la descarga, reduciendo el riesgo de solicitudes enviadas desde sitios externos sin autorización.

## 21. Diseño adaptable

La plantilla fue desarrollada con Tailwind CSS.

En pantallas grandes presenta:

- Formulario principal.
- Panel lateral con reglas.
- Tabla de exportaciones recientes.

En pantallas pequeñas:

- Los bloques se muestran verticalmente.
- Los botones ocupan un espacio accesible.
- La tabla se transforma en tarjetas.
- El menú móvil permite acceder a Exportaciones.
- No se requiere desplazamiento horizontal para consultar el historial.

## 22. Historial visible

La pantalla consulta las últimas diez exportaciones.

Para cada una muestra:

- Nombre del archivo.
- Período.
- Formato.
- Cantidad de registros.
- Usuario.
- Fecha y hora.

Este historial representa metadata de auditoría. No funciona como almacenamiento de copias descargables.

## 23. Pruebas manuales

Durante la comprobación manual se utilizaron exclusivamente datos ficticios.

Se preparó un período con:

- Una novedad validada.
- Una novedad en borrador.
- Una novedad anulada.

Primero se comprobó que el borrador bloqueara la exportación.

Después de validar todos los registros pendientes se comprobó:

- Descarga CSV.
- Descarga Excel.
- Exclusión de la novedad anulada.
- Inclusión de dos novedades validadas.
- Registro del usuario.
- Cambio del período a `EXPORTADO`.
- Registro de la fecha de cierre.
- Reexportación en otro formato.
- Historial visible en la interfaz.

## 24. Pruebas automáticas

El archivo:

```text
novedades/test_exportacion.py
```

incorpora ocho pruebas específicas:

1. La ruta exige autenticación.
2. La página utiliza la plantilla y muestra el período disponible.
3. Los períodos sin novedades validadas no aparecen.
4. La exportación se bloquea cuando existen borradores.
5. El CSV incluye solamente registros validados y crea auditoría.
6. El Excel contiene la estructura y datos esperados.
7. La reexportación conserva la primera fecha de cierre.
8. Los textos peligrosos no se interpretan como fórmulas.

Después de incorporar estas pruebas, el proyecto cuenta con:

```text
52 pruebas automáticas aprobadas
```

## 25. Archivos principales

| Archivo | Responsabilidad |
|---|---|
| `novedades/exportadores.py` | Genera CSV y Excel en memoria |
| `novedades/forms.py` | Define `ExportacionForm` |
| `novedades/views.py` | Procesa la exportación y entrega el archivo |
| `novedades/urls.py` | Registra `/exportaciones/` |
| `novedades/models.py` | Contiene `Exportacion` y los estados del período |
| `novedades/test_exportacion.py` | Pruebas automatizadas |
| `templates/novedades/exportar_novedades.html` | Interfaz del módulo |
| `templates/novedades/base_interno.html` | Navegación lateral y móvil |
| `static/novedades/css/landing.css` | CSS generado por Tailwind |
| `requirements.txt` | Registra OpenPyXL y et-xmlfile |

## 26. Funcionalidades futuras

El módulo actual genera archivos estructurados para revisión y continuidad del proceso.

En jornadas posteriores podrían incorporarse:

- Configuración personalizada de columnas.
- Exportaciones por rangos de fechas.
- Firma o huella digital de archivos.
- Integración directa con sistemas contables.
- Permisos diferenciados para generar exportaciones.
- Reportes resumidos por tipo de novedad.
- Exportaciones masivas de varios períodos.

Estas funciones no son necesarias para el alcance actual del proyecto.

## 27. Explicación para la sustentación

La exportación no consiste solamente en convertir información a Excel.

Primero, el sistema comprueba que el período esté preparado y que no existan novedades pendientes. Después consulta únicamente los registros validados, excluyendo los anulados.

El archivo se genera en memoria para evitar almacenar información sensible en carpetas públicas. Al mismo tiempo, la base de datos registra quién realizó la exportación, cuándo la hizo, qué formato utilizó y cuántos registros fueron incluidos.

El proceso se ejecuta dentro de una transacción para mantener consistencia entre el archivo generado, la auditoría y el estado del período.

Finalmente, se aplican controles contra fórmulas peligrosas, caché compartida, formatos no permitidos, solicitudes sin autenticación y solicitudes POST sin token CSRF.