# API REST del Sistema de Novedades

## 1. Propósito

La API REST permite consultar y administrar la información del sistema de novedades de remuneraciones mediante solicitudes HTTP estructuradas.

Fue desarrollada con Django REST Framework y utiliza los modelos almacenados en PostgreSQL.

## 2. Dirección principal

Durante el desarrollo local, la API se encuentra disponible en:

```text
http://127.0.0.1:8000/api/
```

El inicio de sesión para la interfaz navegable se encuentra en:

```text
http://127.0.0.1:8000/api-auth/login/
```

## 3. Autenticación y permisos

La API utiliza autenticación por sesión de Django.

Todas las rutas están protegidas mediante el permiso `IsAuthenticated`. Por lo tanto, un usuario no autenticado no puede consultar, crear, modificar ni eliminar registros.

En esta primera versión, todo usuario autenticado puede utilizar las operaciones disponibles. Los permisos diferenciados por cargo o grupo se implementarán posteriormente.

## 4. Recursos disponibles

| Recurso | Ruta |
|---|---|
| Sucursales | `/api/sucursales/` |
| Bancos | `/api/bancos/` |
| AFP | `/api/afp/` |
| Instituciones de salud | `/api/instituciones-salud/` |
| Colaboradores | `/api/colaboradores/` |
| Contratos | `/api/contratos/` |
| Períodos de liquidación | `/api/periodos/` |
| Tipos de novedad | `/api/tipos-novedad/` |
| Novedades | `/api/novedades/` |
| Exportaciones | `/api/exportaciones/` |

La consulta de un registro específico utiliza su identificador:

```text
/api/recurso/{id}/
```

Ejemplo:

```text
/api/novedades/1/
```

## 5. Operaciones disponibles

Los recursos fueron implementados mediante `ModelViewSet`.

| Método HTTP | Operación |
|---|---|
| `GET` | Listar registros o consultar un registro |
| `POST` | Crear un registro |
| `PUT` | Reemplazar completamente un registro |
| `PATCH` | Modificar parcialmente un registro |
| `DELETE` | Eliminar registros en los recursos que lo permiten |
| `OPTIONS` | Consultar las operaciones permitidas |

### Operaciones especiales de novedades

La gestión de estados utiliza acciones controladas:

| Método | Ruta | Operación |
|---|---|---|
| `POST` | `/api/novedades/{id}/validar/` | Validar una novedad en borrador |
| `POST` | `/api/novedades/{id}/anular/` | Anular una novedad indicando el motivo |

El recurso de novedades no permite `DELETE`. Una novedad debe anularse para conservar su historial y auditoría.

## 7. Campos de trazabilidad

Algunos campos son asignados automáticamente por el servidor y son de solo lectura.

### Novedades

- `estado`: estado controlado mediante las acciones de validación y anulación.
- `creado_por`: usuario autenticado que registra la novedad.
- `validado_por`: usuario que valida la novedad.
- `validado_en`: fecha y hora de validación.
- `anulado_por`: usuario que anula la novedad.
- `anulado_en`: fecha y hora de anulación.
- `motivo_anulacion`: explicación registrada durante la anulación.
- `creado_en`: fecha y hora de creación.
- `actualizado_en`: fecha y hora de la última modificación.

El campo `estado` no puede cambiarse directamente mediante `PUT` o `PATCH`. Para validar o anular deben utilizarse las acciones especiales de la API.

### Exportaciones

- `generado_por`: usuario autenticado que registra la exportación.
- `fecha_generacion`: fecha y hora automática de generación.

### Períodos de liquidación

- `creado_en`: fecha y hora automática de creación.

## 8. Serializadores

Se implementaron serializadores explícitos para los 10 modelos del dominio:

1. `SucursalSerializer`.
2. `BancoSerializer`.
3. `AFPSerializer`.
4. `InstitucionSaludSerializer`.
5. `ColaboradorSerializer`.
6. `ContratoSerializer`.
7. `PeriodoLiquidacionSerializer`.
8. `TipoNovedadSerializer`.
9. `NovedadSerializer`.
10. `ExportacionSerializer`.

Los serializadores convierten los modelos de Django a representaciones JSON y validan la información recibida por la API.

## 9. Pruebas automáticas de la API

Actualmente existen diez pruebas específicas de la API:

1. Rechazo de solicitudes realizadas por usuarios no autenticados.
2. Comprobación de los 10 recursos de la raíz de la API.
3. Comprobación de la paginación de los listados.
4. Creación y validación de novedades con trazabilidad.
5. Creación de exportaciones con registro automático del usuario.
6. Protección contra cambios directos del estado.
7. Anulación de novedades con auditoría.
8. Rechazo de motivos de anulación demasiado cortos.
9. Bloqueo de edición de novedades validadas.
10. Rechazo de la eliminación de novedades mediante `DELETE`.

En conjunto, el proyecto cuenta actualmente con 52 pruebas automáticas ejecutadas correctamente.