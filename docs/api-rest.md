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
| `DELETE` | Eliminar un registro |
| `OPTIONS` | Consultar las operaciones permitidas |

## 6. Paginación

Los listados utilizan paginación por número de página y muestran un máximo de 25 registros por página.

La respuesta contiene la siguiente estructura:

```json
{
    "count": 0,
    "next": null,
    "previous": null,
    "results": []
}
```

## 7. Campos de trazabilidad

Algunos campos son asignados automáticamente por el servidor y no pueden ser enviados directamente por el cliente.

### Novedades

- `creado_por`: usuario autenticado que registra la novedad.
- `validado_por`: usuario que cambia el estado a `VALIDADA`.
- `creado_en`: fecha y hora de creación.
- `actualizado_en`: fecha y hora de la última modificación.

Si una novedad deja de tener el estado `VALIDADA`, el campo `validado_por` se limpia automáticamente.

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

Se agregaron cinco pruebas específicas:

1. Rechazo de solicitudes realizadas por usuarios no autenticados.
2. Comprobación de los 10 recursos de la raíz de la API.
3. Comprobación de la paginación de los listados.
4. Creación y validación de novedades con trazabilidad del usuario.
5. Creación de exportaciones con registro automático del usuario.

En conjunto, el proyecto cuenta actualmente con 13 pruebas automáticas ejecutadas correctamente.

## 10. Protección de datos

Las pruebas automáticas utilizan exclusivamente información ficticia.

No deben incorporarse al repositorio:

- Contraseñas.
- Credenciales de base de datos.
- Archivos `.env`.
- RUT reales.
- Nombres reales de colaboradores.
- Información bancaria, previsional o salarial real.