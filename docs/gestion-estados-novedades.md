# Gestión de Estados de las Novedades

## 1. Propósito

Este módulo controla el ciclo de vida de las novedades de remuneraciones después de su creación.

Una novedad se registra inicialmente como borrador. Posteriormente puede ser revisada, editada, validada o anulada según su estado y el estado del período de liquidación al que pertenece.

El objetivo principal es impedir modificaciones no autorizadas y mantener la trazabilidad de cada decisión realizada por los usuarios del sistema.

## 2. Estados disponibles

El modelo `Novedad` utiliza tres estados:

| Estado | Descripción |
|---|---|
| `BORRADOR` | Registro creado y disponible para revisión o corrección. |
| `VALIDADA` | Registro revisado y confirmado para el proceso de remuneraciones. |
| `ANULADA` | Registro invalidado, pero conservado como evidencia histórica. |

## 3. Transiciones permitidas

| Estado actual | Editar | Validar | Anular |
|---|---:|---:|---:|
| Borrador | Sí, si el período está abierto | Sí, si el período está abierto | Sí |
| Validada | No | No | Sí |
| Anulada | No | No | No |

Las transiciones se encuentran centralizadas en el modelo para que las mismas reglas sean utilizadas por la interfaz web, la API REST y las pruebas automáticas.

## 4. Conservación de los registros anulados

Las novedades anuladas no se eliminan de la base de datos.

Conservarlas permite responder preguntas como:

- Quién creó el registro.
- Quién lo validó.
- Quién lo anuló.
- Cuándo ocurrió cada acción.
- Cuál fue el motivo de la anulación.

Esta decisión protege la trazabilidad del proceso y evita la pérdida de información histórica.

## 5. Campos de auditoría

Se agregaron los siguientes campos al modelo `Novedad`:

| Campo | Tipo | Propósito |
|---|---|---|
| `validado_por` | Llave foránea a usuario | Identifica al usuario que validó la novedad. |
| `validado_en` | Fecha y hora | Registra el momento de la validación. |
| `anulado_por` | Llave foránea a usuario | Identifica al usuario que anuló la novedad. |
| `anulado_en` | Fecha y hora | Registra el momento de la anulación. |
| `motivo_anulacion` | Texto | Explica por qué fue anulada la novedad. |

Los campos de usuario utilizan `on_delete=models.PROTECT` para impedir que la eliminación de una cuenta destruya la trazabilidad asociada.

## 6. Migración de la base de datos

Los nuevos campos fueron incorporados mediante la migración:

```text
novedades.0002_novedad_anulado_en_novedad_anulado_por_and_more
```

La migración agrega:

- `validado_en`
- `anulado_por`
- `anulado_en`
- `motivo_anulacion`

La migración fue aplicada correctamente en PostgreSQL.

## 7. Reglas centralizadas en el modelo

El modelo `Novedad` contiene propiedades que indican qué operaciones están disponibles:

```python
novedad.puede_editar
novedad.puede_validar
novedad.puede_anular
```

También contiene los métodos responsables de ejecutar las transiciones:

```python
novedad.validar(usuario)
novedad.anular(usuario, motivo)
```

### Validación

El método `validar()` comprueba que:

1. La novedad esté en estado borrador.
2. El período de liquidación permanezca abierto.
3. Los datos del modelo superen `full_clean()`.

Después registra:

- Estado `VALIDADA`.
- Usuario validador.
- Fecha y hora de validación.

### Anulación

El método `anular()` comprueba que:

1. La novedad esté en borrador o validada.
2. El motivo sea un texto válido.
3. El motivo tenga entre 10 y 500 caracteres.

Después registra:

- Estado `ANULADA`.
- Usuario que realizó la anulación.
- Fecha y hora de anulación.
- Motivo suministrado.

Si una transición no está permitida, el modelo genera un `ValidationError`.

## 8. Rutas de la interfaz web

| Operación | Método | Ruta |
|---|---|---|
| Editar novedad | GET y POST | `/novedades/<id>/editar/` |
| Validar novedad | POST | `/novedades/<id>/validar/` |
| Anular novedad | GET y POST | `/novedades/<id>/anular/` |

Todas las rutas requieren un usuario autenticado mediante `login_required`.

## 9. Edición de novedades

La edición reutiliza el formulario de captura existente mediante una instancia del modelo:

```python
NovedadForm(request.POST or None, instance=novedad)
```

Solo pueden editarse novedades en estado borrador pertenecientes a períodos abiertos.

Si la novedad ya fue validada o anulada, el sistema rechaza la operación y redirige al listado.

## 10. Validación mediante POST

La validación solamente acepta solicitudes `POST`.

La vista utiliza:

```python
@require_POST
```

Esto evita que una novedad cambie de estado únicamente por visitar una dirección mediante el navegador.

El formulario de validación también incluye el token CSRF de Django.

## 11. Formulario de anulación

La anulación utiliza `AnularNovedadForm`.

El formulario solicita obligatoriamente un motivo con las siguientes condiciones:

- Mínimo: 10 caracteres.
- Máximo: 500 caracteres.
- Los espacios al principio y al final son eliminados.

Antes de confirmar, la pantalla muestra un resumen de la novedad seleccionada.

## 12. Acciones disponibles en el listado

El listado muestra acciones diferentes según el estado:

### Borrador

- Editar.
- Validar.
- Anular.

### Validada

- Anular.

### Anulada

- Sin acciones disponibles.

Estas acciones se muestran tanto en la tabla de escritorio como en las tarjetas de la vista móvil.

## 13. Acciones de la API REST

La API incorpora las siguientes acciones personalizadas:

| Operación | Método | Ruta |
|---|---|---|
| Validar | POST | `/api/novedades/<id>/validar/` |
| Anular | POST | `/api/novedades/<id>/anular/` |

Ejemplo de anulación:

```json
{
  "motivo_anulacion": "Registro anulado después de la revisión."
}
```

Las acciones llaman a los mismos métodos del modelo utilizados por la interfaz web.

## 14. Protección de los estados en la API

Los siguientes campos del serializador son de solo lectura:

- `estado`
- `creado_por`
- `validado_por`
- `validado_en`
- `anulado_por`
- `anulado_en`
- `motivo_anulacion`
- `creado_en`
- `actualizado_en`

Por esta razón, el consumidor de la API no puede validar o anular una novedad modificando directamente el campo `estado` mediante `PATCH`.

Debe utilizar las acciones controladas `validar` o `anular`.

## 15. Protección contra eliminación

El endpoint de novedades no acepta el método `DELETE`.

Una solicitud de eliminación recibe:

```text
405 Method Not Allowed
```

La anulación reemplaza la eliminación física y conserva el registro dentro de PostgreSQL.

## 16. Protección de novedades validadas

Una novedad validada no puede modificarse mediante la interfaz web ni mediante la API REST.

La API responde con código `400 Bad Request` cuando se intenta editar un registro que ya no cumple la propiedad `puede_editar`.

## 17. Administración de Django

El panel administrativo muestra:

- Estado.
- Usuario creador.
- Usuario validador.
- Usuario anulador.
- Fecha de creación.

Los campos de estado y auditoría se configuraron como campos de solo lectura para evitar modificaciones manuales que omitan las reglas del flujo.

## 18. Fechas y zona horaria

Django almacena las fechas con zona horaria.

Internamente pueden observarse en UTC, mientras que las plantillas las presentan según:

```python
TIME_ZONE = "America/Santiago"
USE_TZ = True
```

Esto explica por qué una fecha consultada desde la terminal puede mostrar una hora diferente a la presentada en el navegador.

## 19. Pruebas automáticas

Se creó:

```text
novedades/test_gestion_estados.py
```

Este archivo contiene ocho pruebas para comprobar:

- Protección de rutas.
- Permisos de un borrador.
- Registro del usuario y fecha de validación.
- Uso obligatorio de `POST` para validar.
- Bloqueo de edición después de validar.
- Registro del motivo, usuario y fecha de anulación.
- Rechazo de motivos demasiado cortos.
- Bloqueo de nuevas transiciones después de anular.

También se ampliaron las pruebas de la API para comprobar:

- Validación mediante una acción personalizada.
- Imposibilidad de cambiar directamente el estado.
- Auditoría de la anulación.
- Rechazo de motivos cortos.
- Bloqueo de edición después de validar.
- Rechazo del método `DELETE`.

El proyecto cuenta actualmente con:

```text
44 pruebas automáticas aprobadas
```

## 20. Datos utilizados durante las pruebas

Las verificaciones manuales y automáticas utilizan únicamente información ficticia.

No se incorporaron:

- Nombres reales.
- RUT reales.
- Datos salariales reales.
- Información bancaria real.
- Credenciales dentro del repositorio.

## 21. Archivos principales

| Archivo | Responsabilidad |
|---|---|
| `novedades/models.py` | Estados, auditoría y reglas de transición. |
| `novedades/forms.py` | Formulario de captura y formulario de anulación. |
| `novedades/views.py` | Edición, validación y anulación web. |
| `novedades/urls.py` | Rutas internas del módulo. |
| `novedades/serializers.py` | Protección de campos de auditoría en la API. |
| `novedades/api_views.py` | Acciones REST de validación y anulación. |
| `novedades/admin.py` | Visualización protegida de la auditoría. |
| `templates/novedades/crear_novedad.html` | Creación y edición de borradores. |
| `templates/novedades/lista_novedades.html` | Acciones según el estado. |
| `templates/novedades/anular_novedad.html` | Confirmación y motivo de anulación. |
| `novedades/test_gestion_estados.py` | Pruebas del flujo de estados. |
| `novedades/test_api.py` | Pruebas de seguridad y auditoría de la API. |

## 22. Explicación para la sustentación

La gestión de estados funciona como una máquina de estados sencilla.

Toda novedad nace como borrador. Mientras el período esté abierto puede corregirse y validarse. Cuando se valida, el sistema registra automáticamente quién tomó la decisión y cuándo ocurrió. Desde ese momento el contenido deja de ser editable.

Si posteriormente se detecta que el registro no debe utilizarse, no se elimina. Se anula y se exige un motivo. El sistema conserva al creador, al validador y al usuario que realizó la anulación.

Las reglas están en el modelo y no solamente en los botones de la interfaz. Por eso, aunque alguien intente saltarse la pantalla y utilizar directamente la API, Django aplica las mismas restricciones.

Esta implementación protege la integridad de los datos y permite reconstruir el historial de cada novedad.