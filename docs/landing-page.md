# Landing Page del Proyecto

## 1. Propósito

La landing page es la página pública de presentación de la aplicación **Planilla de Novedades de Remuneraciones**.

Su función es explicar de forma clara:

- El problema que origina el proyecto.
- La solución web propuesta.
- El flujo mensual de captura, validación y exportación.
- La arquitectura tecnológica utilizada.
- Las medidas de seguridad y privacidad.
- El alcance real de la aplicación.

Esta página responde a la recomendación del docente de incorporar una landing que permita comprender el proyecto antes de acceder a sus módulos internos.

## 2. Dirección principal

La landing está disponible durante el desarrollo en:

```text
http://127.0.0.1:8000/
```

La ruta es administrada por la vista `inicio` de la aplicación `novedades`.

## 3. Contenido de la página

| Sección | Identificador | Propósito |
|---|---|---|
| Presentación principal | `contenido` | Presenta el nombre, propósito y principales beneficios del proyecto. |
| El proyecto | `proyecto` | Explica el problema del proceso manual realizado en Excel. |
| Solución | `solucion` | Describe cómo la aplicación organiza colaboradores, períodos y novedades. |
| Flujo | `flujo` | Explica las etapas de captura, validación y exportación. |
| Tecnología | `tecnologia` | Presenta Django, Django REST Framework, PostgreSQL, Tailwind CSS y JavaScript. |
| Seguridad | `seguridad` | Explica las medidas de autenticación, permisos, trazabilidad y privacidad. |

## 4. Tecnologías utilizadas

La landing utiliza las siguientes tecnologías:

- **Django Templates:** genera el documento HTML desde el servidor.
- **HTML5 semántico:** organiza correctamente encabezado, navegación, contenido, secciones y pie de página.
- **Tailwind CSS 4:** construye el diseño visual y adaptable.
- **JavaScript Vanilla:** controla la apertura y cierre del menú móvil.
- **Django Static Files:** administra los archivos CSS y JavaScript.

Tailwind CSS fue instalado localmente como dependencia de desarrollo. No se utiliza una conexión CDN, por lo que la compilación es controlada desde el proyecto.

## 5. Archivos principales

| Archivo | Responsabilidad |
|---|---|
| `templates/novedades/inicio.html` | Contiene la estructura HTML y el contenido de la landing. |
| `static/novedades/css/input.css` | Define la importación, fuentes de clases, colores y estilos base de Tailwind. |
| `static/novedades/css/landing.css` | Contiene el CSS compilado y utilizado por el navegador. |
| `static/novedades/js/landing.js` | Controla el comportamiento del menú móvil. |
| `package.json` | Define las dependencias y comandos de Tailwind. |
| `package-lock.json` | Conserva las versiones exactas de las dependencias instaladas. |
| `novedades/test_landing.py` | Contiene las pruebas automáticas de la landing. |

## 6. Compilación de Tailwind CSS

El archivo fuente es:

```text
static/novedades/css/input.css
```

Tailwind examina las plantillas y el JavaScript para identificar las clases utilizadas. Después genera:

```text
static/novedades/css/landing.css
```

Para instalar las dependencias del frontend en un equipo nuevo se ejecuta:

```powershell
npm install
```

Para compilar el CSS una vez se utiliza:

```powershell
npm run css:build
```

Durante el desarrollo puede mantenerse una compilación automática con:

```powershell
npm run css:watch
```

El directorio `node_modules` no se publica en GitHub porque puede reconstruirse mediante `npm install`.

## 7. Diseño adaptable

La página fue diseñada con enfoque adaptable para funcionar en computadores y dispositivos móviles.

En escritorio:

- Se muestra la navegación completa.
- El contenido principal utiliza varias columnas.
- Los botones y tarjetas aprovechan el espacio horizontal.

En dispositivos móviles:

- La navegación se reemplaza por un botón de menú.
- Las tarjetas se organizan verticalmente.
- Los botones se adaptan al ancho disponible.
- Se evita el desplazamiento horizontal.
- El contenido conserva una jerarquía legible.

La vista fue comprobada con una simulación de **iPhone 12 Pro de 390 × 844 píxeles**.

## 8. Menú móvil

El archivo `landing.js` administra el menú móvil.

Su funcionamiento es el siguiente:

1. Localiza el botón y el contenedor del menú mediante atributos `data-*`.
2. Abre o cierra el menú cuando el usuario presiona el botón.
3. Actualiza el atributo `aria-expanded`.
4. Cambia el ícono de apertura por el de cierre.
5. Cierra el menú cuando se selecciona un enlace.
6. Permite cerrarlo mediante la tecla `Escape`.
7. Lo restablece cuando la pantalla vuelve al tamaño de escritorio.

## 9. Accesibilidad

La landing incorpora las siguientes consideraciones:

- Idioma principal declarado como español.
- Estructura HTML semántica.
- Enlace para saltar directamente al contenido.
- Etiquetas descriptivas para el menú móvil.
- Indicadores visibles de enfoque mediante teclado.
- Contraste entre texto, fondos y botones.
- Navegación mediante enlaces internos.
- Diseño adaptable para distintos tamaños de pantalla.

## 10. Accesos internos

La landing contiene enlaces hacia:

- El panel administrativo de Django.
- La raíz navegable de la API REST.

Estos módulos internos están protegidos mediante autenticación. La landing presenta el proyecto, pero no permite consultar directamente datos laborales, personales, bancarios o salariales.

## 11. Alcance funcional

La aplicación se encargará de:

- Capturar novedades mensuales.
- Validar información obligatoria.
- Organizar los datos por colaborador y período.
- Mantener trazabilidad por usuario.
- Preparar exportaciones para contabilidad.

La aplicación **no reemplaza a Nubox**, no calcula legalmente las liquidaciones de sueldo y no determina cotizaciones previsionales. Su propósito es organizar y validar la información que posteriormente utilizará el proceso contable.

## 12. Validaciones realizadas

Durante el desarrollo se comprobaron:

- Compilación correcta de Tailwind CSS.
- Sintaxis válida del archivo JavaScript.
- Funcionamiento visual en escritorio.
- Adaptación a una pantalla móvil de 390 píxeles.
- Apertura y cierre del menú móvil.
- Navegación hacia las diferentes secciones.
- Ausencia de desplazamiento horizontal.
- Carga de los archivos CSS y JavaScript.
- Ejecución correcta de las 17 pruebas automáticas del proyecto.

## 13. Explicación breve para la sustentación

La landing funciona como la portada explicativa del proyecto. Django entrega la plantilla HTML, Tailwind CSS se encarga del diseño adaptable y JavaScript controla únicamente el menú móvil. La página permite que el docente o cualquier evaluador comprenda el problema, la solución, el flujo, la tecnología y las medidas de seguridad antes de ingresar a los módulos internos de la aplicación.