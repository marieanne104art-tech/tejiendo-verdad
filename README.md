# Tejiendo Verdad — versión Streamlit

Construida siguiendo el mismo estilo de código de tu app MindWay: `session_state`
por etapas, CSS inyectado con `st.markdown`, funciones `mostrar_logo_animado` /
`mostrar_imagen_o_aviso` para no romper la página si falta una imagen, y
persistencia en archivos JSON (en vez de base de datos).

## Cómo correrlo en VS Code

```bash
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## El logo

En la barra de navegación y en la portada se llama a `mostrar_logo_animado()`.
Pon tu archivo `logo.png` (fondo transparente, cuadrado) en la misma carpeta
que `app.py` y aparece automáticamente con una animación de entrada. Si no
existe, se muestra un círculo punteado marcando el espacio — así puedes
probar la app sin tener el logo listo todavía.

Lo mismo aplica a las imágenes de la landing (`imagen_rostros.png`,
`imagen_territorio.png`, `imagen_alianza.png`): si no están, queda el aviso
del espacio en vez de romper la página.

## Paleta de color

Todo el morado vive en las variables CSS al inicio del archivo:

```css
--color-acento: #5B3A94;       /* morado principal (botones, títulos) */
--color-acento-hover: #46296F;
--color-acento-suave: #E9E0F7; /* fondo de alertas */
--color-mascota: #F0B429;      /* dorado, para el color secundario */
--color-apoyo: #D65A31;        /* terracota, solo para el botón de apoyo */
```

Cambiar el tono general es editar esas líneas, igual que en MindWay.

## Estructura de datos (JSON en vez de base de datos)

```
data/
  capitulos.json     # {"capitulos": [...]}
  testimonios.json    # {"testimonios": [...]}
  comentarios.json    # {"comentarios": [...]}
  frases.json         # {"frases": [...]}
uploads/audio/         # archivos de audio subidos (testimonios y capítulos)
```

Se crean solos la primera vez que corres la app. No se han incluido `.json`
de ejemplo — para probar la plataforma completa, entra al **Panel de
moderación** (botón al final de cualquier vista dentro de la app) y crea ahí
un capítulo, o deja un testimonio de prueba desde "Dejar mi testimonio".

## Cómo está organizado `app.py`

1. Config de página + `session_state` (`etapa`, `seccion_landing`, `vista`)
2. CSS con la paleta morada
3. `mostrar_logo_animado`, `mostrar_imagen_o_aviso`, `limitar_ancho_central`
4. Persistencia JSON (`cargar_/guardar_` por cada tipo de dato)
5. Moderación: `detectar_riesgo`, `parece_spam`, `estado_inicial_testimonio`
6. `barra_navegacion()` — el nav de la plataforma + botón de apoyo
7. Etapas (`if st.session_state.etapa == ...`):
   - `bienvenida` — landing con secciones (Inicio, El proyecto, Cómo
     funciona, Alianza de apoyo, Privacidad)
   - `testimonio_nuevo` — formulario, sin login
   - `gracias` — confirmación con el código de seguimiento
   - `aprobar` — el/la protagonista pega su código y aprueba la versión final
   - `app` — con `vista` interna: inicio, podcast, podcast_detalle,
     linea_tiempo, galeria, bitacora, colcha, apoyo, moderacion

## El flujo de un testimonio (igual al que definimos)

1. Se envía sin registro, texto o audio, con tipo de violencia opcional y
   público/privado.
2. Filtro de riesgo por palabras clave → si hay señal de crisis, pasa a
   `en_revision_riesgo` antes que cualquier otra cosa.
3. Privado sin riesgo → `solo_desahogo`, nunca se publica.
4. Público → moderación lo cura, lo asigna a un capítulo, genera un código.
5. Aprobación del protagonista con ese código → recién ahí `publicado`.
6. Aparece en podcast, línea de tiempo y galería (si lo autorizó);
   comentarios de la bitácora también pasan por moderación antes de
   publicarse.

## Pendiente antes de producción

- El panel de moderación no tiene login — cualquiera que sepa la URL puede
  entrar. Agrega autenticación (por ejemplo `streamlit-authenticator`).
- Los datos de la línea de apoyo en la vista "Apoyo" son placeholders.
- El filtro de riesgo es una heurística simple, no reemplaza el criterio
  clínico — la revisión humana siempre es obligatoria.
- El envío del enlace de aprobación al correo del protagonista no está
  automatizado todavía (hoy el código se muestra en pantalla y en el panel
  de moderación, para copiarlo y enviarlo manualmente).
