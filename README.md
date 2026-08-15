# Planilla de Novedades de Remuneraciones

> *Django REST + Web Frontend para la Automatización de la Planilla de Novedades de Remuneraciones en Alimentos Rancagua SpA*

## Estado del proyecto

Fase actual: modelos de dominio implementados y preparación para el desarrollo de la API REST.

*Fecha de inicio:* 10 de agosto de 2026.  
*Fecha límite:* 10 de septiembre de 2026.

## Descripción

Este proyecto consiste en el desarrollo de una aplicación web interna para registrar, validar, consultar, consolidar y exportar las novedades mensuales relacionadas con el proceso de remuneraciones de Alimentos Rancagua SpA.

La aplicación busca reemplazar la preparación manual realizada actualmente en Excel y facilitar el envío de información organizada al departamento de contabilidad.

El sistema se enfocará en la gestión de asistencia, horas extras, inasistencias, licencias médicas, vacaciones, feriados, bonos, colación, movilización, anticipos, préstamos y otros descuentos.

## Planteamiento del problema

Actualmente, Alimentos Rancagua SpA registra y consolida manualmente en Excel las novedades mensuales necesarias para el proceso de remuneraciones, incluyendo asistencia, horas extras, inasistencias, vacaciones, feriados, bonos, anticipos y descuentos.

La información se repite entre distintas hojas y depende de colores, formatos horarios y valores digitados manualmente antes de enviarse a contabilidad. Este procedimiento genera riesgos de transcripción e interpretación, dificulta la validación y la trazabilidad histórica y aumenta el tiempo de preparación.

Por ello, se requiere una aplicación web interna que centralice los datos de los colaboradores y permita registrar, validar, consultar y exportar las novedades en formato Excel o CSV para su posterior procesamiento contable.

## Pregunta problema

¿De qué manera la implementación de una aplicación web automatiza la gestión mensual de las novedades de remuneraciones en Alimentos Rancagua SpA?

## Objetivos

### Objetivo general

Desarrollar, antes del 10 de septiembre de 2026, una aplicación web con Python, Django REST, PostgreSQL, HTML5, Tailwind CSS y JavaScript para la gestión de novedades de remuneraciones en Alimentos Rancagua SpA, con validación del 100 % de los campos obligatorios y una puntuación mínima de 80 en Lighthouse.

### Objetivos específicos

1. Diseñar el modelo entidad-relación y la arquitectura web para colaboradores, contratos, entidades previsionales, periodos y novedades de remuneraciones.

2. Implementar los endpoints de la API REST y una interfaz web responsiva para el registro, validación, consulta y exportación de novedades de remuneraciones.

3. Validar la solución mediante pruebas funcionales y de seguridad, una puntuación mínima de 80 en Lighthouse y un despliegue operativo en la nube.

## Alcance del proyecto

La primera versión funcional permitirá:

- Iniciar y cerrar sesión de forma segura.
- Administrar usuarios y roles.
- Registrar colaboradores.
- Registrar contratos y datos laborales.
- Administrar bancos, AFP y entidades de salud.
- Crear periodos mensuales de remuneración.
- Registrar días trabajados.
- Registrar inasistencias y licencias médicas.
- Registrar vacaciones y feriados.
- Registrar horas extras en formato HH:MM.
- Registrar bonos, colación y movilización.
- Registrar anticipos, préstamos y descuentos.
- Validar campos obligatorios y formatos.
- Consultar las novedades por colaborador y periodo.
- Generar un resumen mensual.
- Exportar la información a CSV o Excel.
- Conservar un historial de las novedades registradas.

## Fuera del alcance inicial

La primera versión no realizará:

- El cálculo legal completo de las liquidaciones de sueldo.
- El cálculo automático de impuestos.
- El cálculo de cotizaciones previsionales.
- La emisión de documentos oficiales de remuneraciones.
- La integración directa con Nubox.
- El almacenamiento de información real en el repositorio público.

La aplicación preparará y validará las novedades para su posterior procesamiento por contabilidad.

## Usuarios previstos

### Administrador

Podrá administrar usuarios, colaboradores, contratos, entidades y configuraciones generales.

### Contabilidad

Podrá registrar, revisar, consolidar y exportar las novedades de remuneraciones.

### Consulta

Podrá visualizar información autorizada sin modificar los registros.

## Stack tecnológico

| Componente | Tecnología |
|---|---|
| Lenguaje principal | Python |
| Backend | Django y Django REST Framework |
| Frontend | HTML5, Tailwind CSS y JavaScript Vanilla |
| Base de datos de desarrollo | SQLite |
| Base de datos de producción | PostgreSQL |
| Panel administrativo | Django Admin / Jazzmin |
| Control de versiones | Git |
| Repositorio | GitHub |
| Servidor previsto | Render |
| Base de datos administrada prevista | Supabase |
| Metodología | Agile / Scrum Web |

## Arquitectura inicial

La aplicación utilizará una arquitectura web Full-Stack:

1. El usuario accederá desde un navegador web.
2. El frontend presentará formularios y reportes.
3. Django procesará las reglas del negocio.
4. Django REST Framework proporcionará la API.
5. PostgreSQL almacenará la información.
6. El módulo de reportes generará archivos CSV o Excel.
7. GitHub conservará el código y la documentación.
8. El servicio cloud permitirá el acceso a la aplicación desplegada.

## Seguridad prevista

La aplicación utilizará autenticación mediante JWT o sesiones seguras y permisos según roles.

El acceso CORS estará limitado al dominio autorizado. Los datos serán validados y sanitizados antes de su procesamiento. El ORM de Django ayudará a prevenir inyecciones SQL y el escape de contenido protegerá contra ataques XSS.

La comunicación utilizará HTTPS, las credenciales permanecerán en variables de entorno y las operaciones importantes quedarán registradas para su auditoría.

## Estimación académica de infraestructura

| Recurso | Proveedor | Frecuencia | Costo estimado |
|---|---|---|---:|
| Dominio | Namecheap | Anual | USD 14 |
| Servidor web | Render | Mensual estimado | USD 7 |
| Base de datos PostgreSQL | Supabase | Mensual estimado | USD 10 |
| *Total estimado* |  |  | *USD 31* |

Los precios serán confirmados antes del despliegue. Durante el desarrollo se priorizarán herramientas y planes gratuitos.

## Metodología de trabajo

Se utilizará la metodología *Agile / Scrum Web*, dividiendo el desarrollo en tareas pequeñas y avances verificables.

Cada jornada de trabajo finalizará con:

1. Prueba de la funcionalidad desarrollada.
2. Actualización de la documentación.
3. Registro de evidencias.
4. Creación de un commit.
5. Envío de los cambios a GitHub.

## Documentación técnica

- [Modelo entidad-relación](docs/modelo-entidad-relacion.md): presenta las entidades, relaciones, cardinalidades y decisiones de diseño.
- [Diccionario de datos](docs/diccionario-datos.md): define los campos, tipos, restricciones y reglas de negocio de la base de datos.

Los archivos reales utilizados para analizar el proceso no se incluyen en el repositorio porque contienen información personal, bancaria, previsional y salarial.

## Ruta de desarrollo

- [x] Aprobación de la idea por parte del docente.
- [x] Creación del repositorio público.
- [x] Definición del problema y los objetivos.
- [x] Selección del stack tecnológico.
- [x] Documentación inicial del proyecto.
- [x] Preparación del entorno de desarrollo.
- [x] Creación del proyecto Django.
- [x] Diseño del modelo entidad-relación.
- [x] Desarrollo de los modelos.
- [ ] Desarrollo de la API REST.
- [ ] Desarrollo de la interfaz web.
- [ ] Implementación de las validaciones.
- [ ] Implementación de las exportaciones.
- [ ] Pruebas funcionales y de seguridad.
- [ ] Despliegue en la nube.
- [ ] Presentación y entrega final.

## Bitácora de desarrollo

| Fecha | Actividad | Resultado |
|---|---|---|
| 10-08-2026 | Planificación inicial y actualización del README | Definición del problema, objetivos, alcance, stack tecnológico, metodología y ruta de desarrollo. |
| 11-08-2026 | Preparación del entorno local | Se verificaron Python 3.14.7, Git 2.55.0, Visual Studio Code 1.132.0, Node.js 24.19.0 y npm 11.17.0; se instaló PostgreSQL 18.4 con pgAdmin 4; se creó el entorno virtual `.venv` y se instalaron Django 5.2.17 LTS, Django REST Framework 3.18.0 y Psycopg 3.3.4. Las dependencias quedaron registradas en `requirements.txt`. |
| 13-08-2026 | Creación y configuración inicial del proyecto Django | Se creó el proyecto Django y la aplicación `novedades`; se configuró la conexión segura con PostgreSQL mediante variables de entorno; se aplicaron las migraciones iniciales; se registró Django REST Framework; se prepararon las carpetas de plantillas y archivos estáticos; se creó la página principal y se ejecutó correctamente la primera prueba automática. |
| 14-08-2026 | Diseño del modelo entidad-relación | Se analizaron la planilla Excel y las liquidaciones generadas por Nubox; se definieron las entidades, relaciones, cardinalidades, campos, reglas de negocio, tratamiento de datos sensibles y límites del cálculo legal. Se documentaron el diagrama entidad-relación y el diccionario de datos. |
| 15-08-2026 | Desarrollo de los modelos de dominio | Se implementaron los 10 modelos del sistema con sus relaciones, opciones controladas, validadores y restricciones de integridad; se generó y aplicó la migración inicial en PostgreSQL; se registraron los modelos en el panel administrativo y se ejecutaron correctamente 8 pruebas automáticas. |

## Consideraciones de privacidad

Este repositorio es público. Por esta razón:

- No se publicarán nombres reales de colaboradores.
- No se publicarán RUT reales.
- No se publicarán cuentas bancarias.
- No se publicarán remuneraciones reales.
- No se publicarán contraseñas ni credenciales.
- Los datos utilizados en las demostraciones serán ficticios.
- Los archivos .env estarán excluidos del repositorio.

## Autor

*Fernando Andrés Gómez Cano*

Estudiante de Tecnología en Desarrollo de Software.

## Repositorio

[planilla-novedades-remuneraciones](https://github.com/fernandoandresgc1109-web/planilla-novedades-remuneraciones)

## Licencia

Este proyecto se distribuye bajo la licencia MIT.
