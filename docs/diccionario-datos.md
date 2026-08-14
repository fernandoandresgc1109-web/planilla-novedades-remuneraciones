# Diccionario de Datos

## 1. Propósito

Este documento define los campos, tipos de datos, restricciones y responsabilidades de las entidades que conformarán la base de datos de la aplicación de novedades de remuneraciones.

El diccionario servirá como guía para crear posteriormente los modelos de Django y las tablas de PostgreSQL.

## 2. Convenciones utilizadas

- `PK`: clave primaria.
- `FK`: clave foránea.
- `Único`: el valor no puede repetirse.
- `Opcional`: el campo puede quedar vacío.
- `Automático`: el sistema genera el valor.
- Los nombres técnicos se escribirán sin espacios y en minúsculas.
- Los datos personales utilizados durante el desarrollo serán ficticios.

## 3. Entidad Sucursal

| Campo | Tipo en Django | Requerido | Restricción | Descripción |
|---|---|---:|---|---|
| `id` | `BigAutoField` | Sí | PK, automático | Identificador interno de la sucursal. |
| `codigo` | `CharField(20)` | Sí | Único | Código corto utilizado para identificar la sucursal. |
| `nombre` | `CharField(100)` | Sí |  | Nombre de la sucursal. |
| `direccion` | `CharField(200)` | No | Opcional | Dirección física de la sucursal. |
| `activo` | `BooleanField` | Sí | Valor inicial `True` | Indica si la sucursal puede utilizarse en nuevos registros. |

## 4. Entidad Banco

| Campo | Tipo en Django | Requerido | Restricción | Descripción |
|---|---|---:|---|---|
| `id` | `BigAutoField` | Sí | PK, automático | Identificador interno del banco. |
| `codigo` | `CharField(20)` | Sí | Único | Código interno o bancario de la institución. |
| `nombre` | `CharField(100)` | Sí | Único | Nombre del banco. |
| `activo` | `BooleanField` | Sí | Valor inicial `True` | Indica si el banco se encuentra disponible. |

## 5. Entidad AFP

| Campo | Tipo en Django | Requerido | Restricción | Descripción |
|---|---|---:|---|---|
| `id` | `BigAutoField` | Sí | PK, automático | Identificador interno de la AFP. |
| `codigo` | `CharField(20)` | Sí | Único | Código utilizado para identificar la AFP. |
| `nombre` | `CharField(100)` | Sí | Único | Nombre de la administradora de fondos de pensiones. |
| `activo` | `BooleanField` | Sí | Valor inicial `True` | Indica si la AFP puede asignarse a un colaborador. |

## 6. Entidad Institución de Salud

Nombre técnico propuesto: `InstitucionSalud`.

| Campo | Tipo en Django | Requerido | Restricción | Descripción |
|---|---|---:|---|---|
| `id` | `BigAutoField` | Sí | PK, automático | Identificador interno de la institución. |
| `codigo` | `CharField(20)` | Sí | Único | Código utilizado para identificar la institución. |
| `nombre` | `CharField(100)` | Sí |  | Nombre de FONASA o de la ISAPRE. |
| `tipo` | `CharField(10)` | Sí | Opciones controladas | Identifica si corresponde a `FONASA` o `ISAPRE`. |
| `activo` | `BooleanField` | Sí | Valor inicial `True` | Indica si la institución puede utilizarse. |

## 7. Entidad Colaborador

| Campo | Tipo en Django | Requerido | Restricción | Descripción |
|---|---|---:|---|---|
| `id` | `BigAutoField` | Sí | PK, automático | Identificador interno del colaborador. |
| `rut` | `CharField(12)` | Sí | Único | RUT normalizado del colaborador. |
| `nombres` | `CharField(100)` | Sí |  | Nombres del colaborador. |
| `apellidos` | `CharField(150)` | Sí |  | Apellidos del colaborador. |
| `sucursal` | `ForeignKey` | Sí | FK a `Sucursal` | Sucursal a la que pertenece. |
| `banco` | `ForeignKey` | No | FK a `Banco`, opcional | Banco utilizado para el pago. |
| `numero_cuenta` | `CharField(30)` | No | Opcional y sensible | Número de cuenta bancaria. |
| `tipo_cuenta` | `CharField(20)` | No | Opciones controladas | Tipo de cuenta bancaria. |
| `afp` | `ForeignKey` | Sí | FK a `AFP` | AFP vigente del colaborador. |
| `institucion_salud` | `ForeignKey` | Sí | FK a `InstitucionSalud` | Institución de salud vigente. |
| `cargas_familiares` | `PositiveSmallIntegerField` | Sí | Valor inicial `0` | Número de cargas familiares informadas. |
| `seguro_cesantia` | `BooleanField` | Sí | Valor inicial `True` | Indica si corresponde aplicar seguro de cesantía. |
| `activo` | `BooleanField` | Sí | Valor inicial `True` | Indica si el colaborador mantiene una relación vigente con la empresa. |

## 8. Tratamiento de datos sensibles

Los siguientes campos serán considerados sensibles:

- RUT.
- Nombres y apellidos.
- Banco.
- Número y tipo de cuenta bancaria.
- AFP.
- Institución de salud.
- Sueldo base.
- Montos de bonos, descuentos, préstamos y anticipos.

Estos datos solamente podrán ser consultados por usuarios autenticados y autorizados. No se incluirán datos reales en pruebas automáticas, capturas públicas, documentación o archivos enviados a GitHub.


## 9. Entidad Contrato

| Campo | Tipo en Django | Requerido | Restricción | Descripción |
|---|---|---:|---|---|
| `id` | `BigAutoField` | Sí | PK, automático | Identificador interno del contrato. |
| `colaborador` | `ForeignKey` | Sí | FK a `Colaborador` | Colaborador al que pertenece el contrato. |
| `fecha_inicio` | `DateField` | Sí |  | Fecha de inicio de la relación laboral. |
| `fecha_termino` | `DateField` | No | Opcional | Fecha de término cuando corresponda. |
| `tipo_contrato` | `CharField(20)` | Sí | Opciones controladas | Tipo de contrato: indefinido, plazo fijo u otro autorizado. |
| `sueldo_base` | `DecimalField(12,2)` | Sí | Mayor que cero | Sueldo base asociado con el contrato. |
| `cargo` | `CharField(100)` | Sí |  | Cargo desempeñado por el colaborador. |
| `centro_costo` | `CharField(50)` | No | Opcional | Centro de costo utilizado por contabilidad. |
| `activo` | `BooleanField` | Sí | Valor inicial `True` | Indica si el contrato está vigente. |

Un colaborador podrá conservar contratos históricos, pero solamente podrá tener un contrato activo al mismo tiempo.

## 10. Entidad Período de Liquidación

Nombre técnico propuesto: `PeriodoLiquidacion`.

| Campo | Tipo en Django | Requerido | Restricción | Descripción |
|---|---|---:|---|---|
| `id` | `BigAutoField` | Sí | PK, automático | Identificador interno del período. |
| `sucursal` | `ForeignKey` | Sí | FK a `Sucursal` | Sucursal a la que corresponde el período. |
| `anio` | `PositiveSmallIntegerField` | Sí | Rango válido | Año del período de liquidación. |
| `mes` | `PositiveSmallIntegerField` | Sí | Entre 1 y 12 | Mes del período de liquidación. |
| `fecha_inicio` | `DateField` | Sí |  | Fecha inicial del período. |
| `fecha_cierre` | `DateTimeField` | No | Opcional | Fecha y hora en que se cerró el período. |
| `estado` | `CharField(15)` | Sí | Opciones controladas | Estado actual: abierto, cerrado o exportado. |
| `creado_en` | `DateTimeField` | Sí | Automático | Fecha y hora de creación. |

La combinación de `sucursal`, `anio` y `mes` deberá ser única.

## 11. Entidad Tipo de Novedad

Nombre técnico propuesto: `TipoNovedad`.

| Campo | Tipo en Django | Requerido | Restricción | Descripción |
|---|---|---:|---|---|
| `id` | `BigAutoField` | Sí | PK, automático | Identificador interno del tipo de novedad. |
| `codigo` | `CharField(30)` | Sí | Único | Código técnico de la novedad. |
| `nombre` | `CharField(100)` | Sí | Único | Nombre visible de la novedad. |
| `unidad_medida` | `CharField(15)` | Sí | Opciones controladas | Unidad utilizada: días, minutos, pesos o registro. |
| `naturaleza` | `CharField(15)` | Sí | Opciones controladas | Clasificación: asistencia, haber, descuento o informativo. |
| `activo` | `BooleanField` | Sí | Valor inicial `True` | Indica si el tipo puede utilizarse en nuevos registros. |

Ejemplos de códigos iniciales:

| Código | Nombre | Unidad | Naturaleza |
|---|---|---|---|
| `DIAS_TRABAJADOS` | Días trabajados | Días | Asistencia |
| `HORA_EXTRA` | Horas extras | Minutos | Haber |
| `INASISTENCIA` | Inasistencia | Días | Asistencia |
| `LICENCIA_MEDICA` | Licencia médica | Días | Asistencia |
| `VACACIONES` | Vacaciones | Días | Asistencia |
| `FERIADO` | Feriado | Días | Informativo |
| `BONO` | Bono | Pesos | Haber |
| `COLACION` | Colación | Pesos | Haber |
| `MOVILIZACION` | Movilización | Pesos | Haber |
| `COMISION` | Comisión | Pesos | Haber |
| `DESCUENTO` | Descuento | Pesos | Descuento |
| `PRESTAMO` | Préstamo | Pesos | Descuento |
| `ANTICIPO` | Anticipo | Pesos | Descuento |

## 12. Entidad Novedad

| Campo | Tipo en Django | Requerido | Restricción | Descripción |
|---|---|---:|---|---|
| `id` | `BigAutoField` | Sí | PK, automático | Identificador interno de la novedad. |
| `periodo` | `ForeignKey` | Sí | FK a `PeriodoLiquidacion` | Período mensual al que pertenece. |
| `colaborador` | `ForeignKey` | Sí | FK a `Colaborador` | Colaborador afectado por la novedad. |
| `tipo_novedad` | `ForeignKey` | Sí | FK a `TipoNovedad` | Tipo de novedad registrada. |
| `fecha_inicio` | `DateField` | No | Opcional | Fecha inicial del evento. |
| `fecha_termino` | `DateField` | No | Opcional | Fecha final del evento. |
| `cantidad` | `DecimalField(10,2)` | No | Opcional, no negativa | Cantidad de días, minutos u otra unidad. |
| `monto` | `DecimalField(12,2)` | No | Opcional, no negativo | Valor monetario de la novedad. |
| `observacion` | `TextField` | No | Opcional | Explicación o información adicional. |
| `estado` | `CharField(15)` | Sí | Opciones controladas | Estado: borrador, validada o anulada. |
| `creado_por` | `ForeignKey` | Sí | FK a usuario de Django | Usuario que registró la novedad. |
| `validado_por` | `ForeignKey` | No | FK opcional a usuario | Usuario que validó la novedad. |
| `creado_en` | `DateTimeField` | Sí | Automático | Fecha y hora de creación. |
| `actualizado_en` | `DateTimeField` | Sí | Automático | Fecha y hora de la última modificación. |

## 13. Entidad Exportación

| Campo | Tipo en Django | Requerido | Restricción | Descripción |
|---|---|---:|---|---|
| `id` | `BigAutoField` | Sí | PK, automático | Identificador interno de la exportación. |
| `periodo` | `ForeignKey` | Sí | FK a `PeriodoLiquidacion` | Período del cual se exportó la información. |
| `generado_por` | `ForeignKey` | Sí | FK a usuario de Django | Usuario que generó el archivo. |
| `fecha_generacion` | `DateTimeField` | Sí | Automático | Fecha y hora de generación. |
| `formato` | `CharField(10)` | Sí | Opciones controladas | Formato generado, por ejemplo XLSX o CSV. |
| `nombre_archivo` | `CharField(255)` | Sí |  | Nombre asignado al archivo. |
| `cantidad_registros` | `PositiveIntegerField` | Sí | No negativo | Cantidad de novedades incluidas. |

## 14. Usuario

No se creará inicialmente una tabla personalizada para los usuarios.

La aplicación utilizará el modelo de autenticación incluido en Django para administrar:

- Nombre de usuario.
- Contraseña codificada.
- Correo electrónico.
- Estado activo.
- Grupos.
- Permisos.

Las entidades `Novedad` y `Exportacion` se relacionarán con los usuarios de Django para mantener la trazabilidad.

## 15. Reglas de negocio iniciales

1. No podrán existir dos períodos con la misma sucursal, año y mes.
2. Un colaborador no podrá tener más de un contrato activo.
3. La fecha de término de un contrato no podrá ser anterior a su fecha de inicio.
4. La fecha final de una novedad no podrá ser anterior a su fecha inicial.
5. Las cantidades y los montos no podrán ser negativos.
6. Las novedades expresadas en pesos deberán tener un monto.
7. Las novedades expresadas en días o minutos deberán tener una cantidad.
8. Las horas extras se almacenarán en minutos para evitar errores de interpretación.
9. No se podrán modificar novedades de un período cerrado o exportado.
10. Solamente usuarios autorizados podrán validar novedades y cerrar períodos.
11. El sistema deberá advertir posibles novedades duplicadas.
12. Los catálogos utilizados no se eliminarán físicamente; se marcarán como inactivos.
13. Los datos sensibles no deberán aparecer en registros de errores públicos.
14. Toda exportación deberá quedar asociada con el usuario y período correspondiente.

## 16. Correspondencia con la planilla actual

| Información de la planilla | Entidad propuesta |
|---|---|
| Sucursal o sede | `Sucursal` |
| Nombre y RUT | `Colaborador` |
| Banco, cuenta y tipo de cuenta | `Banco` y `Colaborador` |
| AFP y sistema de salud | `AFP`, `InstitucionSalud` y `Colaborador` |
| Fecha de contrato, tipo y sueldo base | `Contrato` |
| Mes y año procesado | `PeriodoLiquidacion` |
| Días trabajados y horas extras | `TipoNovedad` y `Novedad` |
| Licencias, vacaciones, inasistencias y feriados | `TipoNovedad` y `Novedad` |
| Bonos, colación, movilización y comisión | `TipoNovedad` y `Novedad` |
| Descuentos, préstamos y anticipos | `TipoNovedad` y `Novedad` |
| Archivo entregado a contabilidad | `Exportacion` |
| Persona que registra o valida | Usuario de Django |

## 17. Información calculada fuera de la aplicación

En la primera versión no se almacenarán como novedades calculadas automáticamente:

- Gratificación legal.
- Cotización previsional calculada.
- Cotización de salud calculada.
- Seguro de cesantía calculado.
- Impuesto único.
- Total imponible.
- Total tributable.
- Total de descuentos legales.
- Alcance líquido.

Estos valores seguirán siendo calculados por el sistema de remuneraciones utilizado por contabilidad.