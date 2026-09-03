import streamlit as st
import json
import os
import uuid
import base64
import html
from datetime import date, datetime, timezone

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Tejiendo Verdad", layout="wide")

# --- 2. INICIALIZACIÓN DE ESTADO ---
if 'etapa' not in st.session_state:
    st.session_state.etapa = "principal"
if 'seccion' not in st.session_state:
    st.session_state.seccion = "Inicio"
if 'capitulo_seleccionado_id' not in st.session_state:
    st.session_state.capitulo_seleccionado_id = None
if 'testimonio_recien_enviado' not in st.session_state:
    st.session_state.testimonio_recien_enviado = None

# Si llega un enlace de aprobación con ?token=..., lo tomamos directo.
parametros = st.query_params
if "token" in parametros and st.session_state.etapa == 'principal':
    st.session_state.etapa = 'aprobar'
    st.session_state.token_aprobar_prellenado = parametros["token"]

# --- ESTILOS: todo en morado ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Work+Sans:wght@400;500;600;700&family=Caveat:wght@600;700&display=swap');

    .stApp { background-color: #F5F1FB !important; }
    html, body, div, p, label, li, h1, h2, h3, h4, h5, h6, button, select, input, textarea {
        font-family: 'Work Sans', sans-serif !important;
        color: #201235 !important;
    }
    h1, h2, h3 { font-weight: 700 !important; letter-spacing: -0.3px; }

    div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] {
        margin-bottom: -12px !important;
    }
    hr { margin: 10px 0 !important; }

    .stButton button {
        border-radius: 10px !important;
        font-weight: 600 !important;
    }

    :root {
        --violeta-oscuro: #3E2569;
        --violeta: #5B3A94;
        --violeta-hover: #46296F;
        --violeta-suave: #E9E0F7;
        --violeta-medio: #7C5CB8;
        --violeta-medio-hover: #6A4AA0;
        --violeta-apoyo: #7A2F8F;
        --violeta-apoyo-hover: #631F76;
        --dorado: #C9A44C;
    }

    button[kind="primary"],
    .stButton button[kind="primary"],
    button[data-testid="stBaseButton-primary"] {
        background-color: var(--violeta) !important;
        border-color: var(--violeta) !important;
        color: #FAF6EF !important;
    }
    button[kind="primary"]:hover,
    .stButton button[kind="primary"]:hover,
    button[data-testid="stBaseButton-primary"]:hover {
        background-color: var(--violeta-hover) !important;
        border-color: var(--violeta-hover) !important;
    }

    button[kind="secondary"],
    .stButton button[kind="secondary"],
    button[data-testid="stBaseButton-secondary"] {
        background-color: var(--violeta-medio) !important;
        border-color: var(--violeta-medio) !important;
        color: #FAF6EF !important;
    }
    button[kind="secondary"]:hover,
    .stButton button[kind="secondary"]:hover,
    button[data-testid="stBaseButton-secondary"]:hover {
        background-color: var(--violeta-medio-hover) !important;
        border-color: var(--violeta-medio-hover) !important;
    }

    input[type="radio"], input[type="checkbox"] {
        accent-color: var(--violeta) !important;
    }
    div[data-testid="stProgress"] > div > div > div {
        background-color: var(--violeta) !important;
    }
    div[data-testid="stAlertContainer"] {
        background-color: var(--violeta-suave) !important;
        border-color: var(--violeta) !important;
        color: #201235 !important;
    }

    div[data-testid="stTabs"] button[data-baseweb="tab"] {
        font-weight: 600 !important;
        color: var(--violeta-oscuro) !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: var(--violeta) !important;
    }
    div[data-baseweb="tab-highlight"] {
        background-color: var(--violeta) !important;
    }

    section[data-testid="stSidebar"] {
        background-color: var(--violeta-oscuro) !important;
    }
    section[data-testid="stSidebar"] * {
        color: #FAF6EF !important;
    }

    .tv-tagline {
        font-family: 'Caveat', cursive;
        font-size: 30px;
        color: var(--violeta);
        font-weight: 700;
    }
    .tv-boton-apoyo button {
        background-color: var(--violeta-apoyo) !important;
        border-color: var(--violeta-apoyo) !important;
        color: #FAF6EF !important;
    }
    .tv-boton-apoyo button:hover {
        background-color: var(--violeta-apoyo-hover) !important;
    }
    .tv-boton-testimonio button {
        background-color: var(--dorado) !important;
        border-color: var(--dorado) !important;
        color: #201235 !important;
    }
    .tv-boton-testimonio button:hover {
        background-color: #b4903d !important;
    }

    /* Mazo de cartas de la Colcha por la paz, en la barra lateral */
    .tv-mazo {
        position: relative;
        height: 190px;
        margin: 0.5rem 0 1.5rem;
    }
    .tv-carta-fondo {
        position: absolute;
        top: 10px; left: 50%;
        width: 84%;
        height: 170px;
        background: linear-gradient(160deg, #7C5CB8, #5B3A94);
        border-radius: 14px;
        box-shadow: 0 6px 14px rgba(0,0,0,0.25);
    }
    .tv-carta-fondo.c1 { transform: translateX(-50%) rotate(-8deg); opacity: 0.55; }
    .tv-carta-fondo.c2 { transform: translateX(-50%) rotate(6deg); opacity: 0.75; }
    .tv-carta-hoy {
        position: absolute;
        top: 0; left: 50%;
        transform: translateX(-50%);
        width: 90%;
        min-height: 180px;
        background: linear-gradient(160deg, #FAF6EF, #E9E0F7);
        border: 2px solid var(--dorado);
        border-radius: 14px;
        box-shadow: 0 10px 22px rgba(0,0,0,0.35);
        padding: 14px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .tv-carta-hoy p {
        color: #3E2569 !important;
        font-family: 'Caveat', cursive;
        font-size: 19px;
        font-weight: 700;
        text-align: center;
        margin: 0;
        line-height: 1.25;
    }
    .tv-carta-hoy span {
        display: block;
        text-align: center;
        color: var(--violeta-medio) !important;
        font-size: 11px;
        margin-top: 8px;
    }
    .tv-carta-vacia p {
        color: #6A4AA0 !important;
        font-size: 14px;
        text-align: center;
        font-family: 'Work Sans', sans-serif;
    }

    /* Línea de tiempo literal: una línea vertical con un punto por hecho */
    .tv-timeline { position: relative; padding-left: 40px; margin: 1.5rem 0 2rem; }
    .tv-timeline::before {
        content: '';
        position: absolute;
        left: 12px; top: 6px; bottom: 6px;
        width: 3px;
        background: var(--violeta-medio);
        border-radius: 2px;
    }
    .tv-timeline-item { position: relative; margin-bottom: 2rem; }
    .tv-timeline-dot {
        position: absolute; left: -35px; top: 4px;
        width: 16px; height: 16px; border-radius: 50%;
        background: var(--dorado);
        border: 3px solid var(--violeta-oscuro);
    }
    .tv-timeline-fecha {
        font-weight: 700; color: var(--violeta);
        font-size: 0.82rem; text-transform: uppercase;
        letter-spacing: 0.05em; margin-bottom: 4px;
    }
    .tv-timeline-card {
        background: #FFFFFF; border-radius: 10px;
        padding: 0.9rem 1.1rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    }
    .tv-timeline-card strong { color: var(--violeta-oscuro); display: block; margin-bottom: 4px; }
    .tv-timeline-card p { margin: 0; color: #4B3A6B; font-size: 0.92rem; }

    /* Cuadritos de frases de paz, en la Colcha por la paz */
    .tv-cuadrito-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin: 0.5rem 0 1rem;
    }
    .tv-cuadrito {
        background: linear-gradient(160deg, #7C5CB8, #46296F);
        border-radius: 8px;
        padding: 8px;
        aspect-ratio: 1 / 1;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .tv-cuadrito p {
        color: #FAF6EF !important;
        font-family: 'Caveat', cursive;
        font-weight: 700;
        font-size: 12px;
        text-align: center;
        line-height: 1.2;
        margin: 0;
    }
    </style>
""", unsafe_allow_html=True)


# =============================================================================
# LOGO / IMÁGENES — si el archivo no existe, deja el espacio marcado en vez
# de romper la página.
# =============================================================================
def mostrar_logo_animado(ancho=160):
    if os.path.exists("logo.png"):
        with open("logo.png", "rb") as f:
            datos_b64 = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <style>
            @keyframes tvLogoZoom {{
                0%   {{ transform: scale(2.2); opacity: 0; }}
                60%  {{ opacity: 1; }}
                100% {{ transform: scale(1); opacity: 1; }}
            }}
            .tv-logo-zoom {{
                width: {ancho}px;
                transform-origin: center;
                animation: tvLogoZoom 0.9s cubic-bezier(0.22, 1, 0.36, 1) forwards;
                display: block;
            }}
            </style>
            <img class="tv-logo-zoom" src="data:image/png;base64,{datos_b64}">
        """, unsafe_allow_html=True)
    else:
        st.markdown(
            f"""<div style="width:{ancho}px; height:{ancho}px; border:2px dashed #7C5CB8;
                 border-radius:50%; display:flex; align-items:center; justify-content:center;
                 color:#5B3A94; font-size:13px; text-align:center; padding:8px;">
                 [ Logo Tejiendo Verdad — pon aquí <b>logo.png</b> ]
                 </div>""",
            unsafe_allow_html=True
        )


def mostrar_imagen_o_aviso(nombre_archivo, descripcion, ancho=None):
    if os.path.exists(nombre_archivo):
        st.image(nombre_archivo, width=ancho, use_container_width=(ancho is None))
    else:
        st.markdown(
            f"""<div style="background:#E9E0F7; border:2px dashed #7C5CB8;
                 border-radius:14px; padding:2rem; text-align:center;
                 color:#5B3A94; font-size:14px;">
                 [ {descripcion} — pon aquí el archivo <b>{nombre_archivo}</b> ]
                 </div>""",
            unsafe_allow_html=True
        )


def limitar_ancho_central(max_px=760):
    st.markdown(f"""
        <style>
        .block-container {{
            max-width: {max_px}px !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }}
        </style>
    """, unsafe_allow_html=True)


# =============================================================================
# PERSISTENCIA EN JSON
# =============================================================================
CARPETA_DATOS = "data"
os.makedirs(CARPETA_DATOS, exist_ok=True)
CARPETA_AUDIO = os.path.join("uploads", "audio")
os.makedirs(CARPETA_AUDIO, exist_ok=True)

CAPITULOS_FILE = os.path.join(CARPETA_DATOS, "capitulos.json")
TESTIMONIOS_FILE = os.path.join(CARPETA_DATOS, "testimonios.json")
COMENTARIOS_FILE = os.path.join(CARPETA_DATOS, "comentarios.json")
FRASES_FILE = os.path.join(CARPETA_DATOS, "frases.json")

# Frases de paz curadas para los "cuadritos" del mazo — atribuciones muy
# conocidas, pero verifícalas antes de publicar el sitio (no se buscaron en
# una fuente en vivo, son de memoria).
FRASES_PAZ_CURADAS = [
    ("No hay camino para la paz, la paz es el camino.", "Mahatma Gandhi"),
    ("Si quieres la paz, trabaja por la justicia.", "Papa Pablo VI"),
    ("La paz comienza con una sonrisa.", "Madre Teresa de Calcuta"),
    ("Un ojo por ojo y el mundo acabará ciego.", "Mahatma Gandhi"),
    ("La paz no puede mantenerse por la fuerza; solo se logra con comprensión.", "Albert Einstein"),
    ("La verdadera paz no es solo la ausencia de tensión, sino la presencia de la justicia.", "Martin Luther King Jr."),
    ("Colombia es el único país donde la gente muere de viejo esperando la paz.", "Gabriel García Márquez"),
    ("La paz mundial no puede surgir sino de una paz interior en cada persona.", "Dalái Lama"),
]

TIPOS_VIOLENCIA = [
    "Desplazamiento forzado", "Desaparición forzada", "Reclutamiento forzado",
    "Violencia sexual", "Amenazas", "Masacre o atentado", "Confinamiento",
    "Otro", "Prefiero no decir",
]


def _cargar(ruta, clave):
    if not os.path.exists(ruta):
        return []
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f).get(clave, [])


def _guardar(ruta, clave, lista):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump({clave: lista}, f, ensure_ascii=False, indent=2, default=str)


def cargar_capitulos():
    return _cargar(CAPITULOS_FILE, "capitulos")


def guardar_capitulos(lista):
    _guardar(CAPITULOS_FILE, "capitulos", lista)


def cargar_testimonios():
    return _cargar(TESTIMONIOS_FILE, "testimonios")


def guardar_testimonios(lista):
    _guardar(TESTIMONIOS_FILE, "testimonios", lista)


def cargar_comentarios():
    return _cargar(COMENTARIOS_FILE, "comentarios")


def guardar_comentarios(lista):
    _guardar(COMENTARIOS_FILE, "comentarios", lista)


def cargar_frases():
    return _cargar(FRASES_FILE, "frases")


def guardar_frases(lista):
    _guardar(FRASES_FILE, "frases", lista)


def nuevo_id(lista):
    if not lista:
        return 1
    return max(item["id"] for item in lista) + 1


def asegurar_capitulo_demo():
    """Si todavía no hay ningún capítulo cargado, sembramos uno de ejemplo
    (Toma del Palacio de Justicia) para que se vea cómo funciona la
    plataforma de punta a punta, con un video real de referencia."""
    capitulos = cargar_capitulos()
    if capitulos:
        return
    capitulos.append({
        "id": 1,
        "numero": 1,
        "titulo": "Toma del Palacio de Justicia",
        "descripcion": (
            "El 6 y 7 de noviembre de 1985, la toma del Palacio de Justicia en "
            "Bogotá y la posterior retoma militar dejaron decenas de muertos, "
            "heridos y desaparecidos. Este capítulo de ejemplo reconstruye el "
            "hecho a partir de fuentes públicas, como punto de partida para "
            "tejer después los testimonios de nuestra propia comunidad."
        ),
        "fecha_hecho": "1985-11-06",
        "audio_path": None,
        "video_url": "https://www.youtube.com/watch?v=noMPqtCANhE",
        "publicado": True,
    })
    guardar_capitulos(capitulos)


# =============================================================================
# MODERACIÓN: filtro de riesgo + anti-spam
# -----------------------------------------------------------------------------
# Heurísticas simples por palabras clave para tener algo funcional ya mismo.
# NO reemplazan el criterio clínico: la Capa 1 (riesgo) y la moderación de
# comentarios SIEMPRE deben pasar por revisión humana capacitada -idealmente
# por la alianza de psicólogos- antes de decidir nada.
# =============================================================================
SENALES_RIESGO_ACTUAL = [
    "me quiero morir", "quiero suicidarme", "ya no aguanto más",
    "no quiero seguir viviendo", "voy a hacerme daño", "estoy en peligro ahora",
    "me quieren matar", "tengo el arma",
]
SENALES_SPAM = ["http://", "https://", "www.", "compra ahora", "gratis"]


def detectar_riesgo(texto):
    if not texto:
        return False
    t = texto.lower()
    return any(s in t for s in SENALES_RIESGO_ACTUAL)


def parece_spam(texto):
    if not texto:
        return False
    t = texto.lower()
    return any(s in t for s in SENALES_SPAM)


def estado_inicial_testimonio(texto):
    if detectar_riesgo(texto or ""):
        return "en_revision_riesgo", True
    return "pendiente_moderacion", False


def guardar_audio_subido(archivo_subido):
    extension = archivo_subido.name.rsplit(".", 1)[-1].lower()
    nombre = f"{uuid.uuid4().hex}.{extension}"
    ruta = os.path.join(CARPETA_AUDIO, nombre)
    with open(ruta, "wb") as f:
        f.write(archivo_subido.getbuffer())
    return ruta


# =============================================================================
# BLOQUE REUTILIZABLE: bitácora tipo chat sobre un testimonio.
# en_expander=True  -> se usa en Podcast y Galería (colapsado por defecto).
# en_expander=False -> se usa en la sección Bitácora (siempre visible).
# =============================================================================
def _contenido_bitacora_chat(testimonio, contexto, mostrar_testimonio_como_mensaje=False):
    if mostrar_testimonio_como_mensaje:
        with st.chat_message("assistant"):
            st.markdown("**Testimonio**")
            st.write(testimonio.get("version_editada_texto") or testimonio.get("contenido_texto"))

    comentarios = cargar_comentarios()
    aprobados = [
        c for c in comentarios
        if c["testimonio_id"] == testimonio["id"] and c["estado"] == "aprobado"
    ]
    if aprobados:
        for c in aprobados:
            with st.chat_message("user"):
                st.markdown(f"**{c.get('autor_nombre') or 'Anónimo'}**")
                st.write(c["texto"])
    else:
        st.caption("Todavía no hay comentarios aprobados. Sé el primero en reflexionar.")

    if testimonio["comentarios_habilitados"]:
        autor_key = f"autor_chat_{contexto}_{testimonio['id']}"
        st.text_input("Tu nombre (opcional)", key=autor_key, placeholder="Anónimo")
        nuevo_texto = st.chat_input(
            "Escribe tu reflexión, con respeto...",
            key=f"chat_input_{contexto}_{testimonio['id']}",
        )
        if nuevo_texto:
            if parece_spam(nuevo_texto):
                estado_c = "rechazado"
            else:
                estado_c = "pendiente"
            comentarios.append({
                "id": nuevo_id(comentarios),
                "testimonio_id": testimonio["id"],
                "autor_nombre": st.session_state.get(autor_key) or None,
                "texto": nuevo_texto,
                "estado": estado_c,
                "motivo_rechazo": None,
                "creado_en": datetime.now(timezone.utc).isoformat(),
            })
            guardar_comentarios(comentarios)
            st.success("Gracias. Tu comentario se publicará después de ser revisado.")
            st.rerun()
    else:
        st.caption("Quien contó este testimonio prefirió no recibir comentarios.")


def bloque_bitacora_inline(testimonio, contexto, en_expander=True):
    if en_expander:
        with st.expander("Ver reflexiones y comentarios"):
            _contenido_bitacora_chat(testimonio, contexto)
    else:
        _contenido_bitacora_chat(testimonio, contexto, mostrar_testimonio_como_mensaje=True)


# =============================================================================
# BLOQUE REUTILIZABLE: encabezado — logo grande, tagline, y los dos botones
# que van juntos: dejar testimonio y hablar con alguien ahora.
# =============================================================================
SECCIONES = ["Inicio", "Podcast", "Galería virtual", "Línea del tiempo", "Bitácora", "Testimonio"]


def barra_superior():
    col_logo, col_tagline = st.columns([1, 3.5])
    with col_logo:
        mostrar_logo_animado(ancho=150)
    with col_tagline:
        st.markdown('<p class="tv-tagline">Nunca más el olvido.<br>Siempre más la esperanza.</p>',
                    unsafe_allow_html=True)

    col_espacio, col_testimonio, col_apoyo = st.columns([2.6, 1.6, 2])
    with col_testimonio:
        st.markdown('<div class="tv-boton-testimonio">', unsafe_allow_html=True)
        if st.button("Dejar mi testimonio", key="btn_testimonio_top", use_container_width=True):
            st.session_state.seccion = "Testimonio"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col_apoyo:
        st.markdown('<div class="tv-boton-apoyo">', unsafe_allow_html=True)
        if st.button("Quiero hablar con alguien ahora", key="btn_apoyo_top", use_container_width=True):
            st.session_state.mostrar_apoyo = True
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.get("mostrar_apoyo"):
        with st.container(border=True):
            col_txt, col_cerrar = st.columns([5, 1])
            with col_txt:
                st.markdown("**Línea de apoyo (a definir con la alianza de psicólogos)**")
                st.write("**Teléfono:** Pendiente de confirmar · **WhatsApp:** Pendiente de confirmar")
                st.caption(
                    "Esta línea es independiente de si dejaste o no un testimonio. Si tú o alguien "
                    "más está en peligro inmediato, contacta primero a los servicios de emergencia de tu país."
                )
            with col_cerrar:
                if st.button("Cerrar", key="btn_cerrar_apoyo"):
                    st.session_state.mostrar_apoyo = False
                    st.rerun()

    st.markdown("---")

    # Navegación por botones (en vez de st.tabs) para poder saltar a una
    # sección concreta desde cualquier otro botón de la página.
    cols_nav = st.columns(len(SECCIONES))
    for col, nombre in zip(cols_nav, SECCIONES):
        with col:
            tipo = "primary" if st.session_state.seccion == nombre else "secondary"
            if st.button(nombre, key=f"nav_{nombre}", type=tipo, use_container_width=True):
                st.session_state.seccion = nombre
                st.rerun()
    st.markdown("---")


# =============================================================================
# BARRA LATERAL: Colcha por la paz, como un mazo de cartas — cada día se
# "elige" (muestra) una carta distinta.
# =============================================================================
def colcha_sidebar():
    with st.sidebar:
        st.markdown("### Colcha por la paz")
        st.caption("Cada día se elige una carta del mazo, como el evangelio del día.")

        frases = cargar_frases()
        frase_hoy = next((f for f in frases if f["fecha"] == date.today().isoformat()), None)

        st.markdown('<div class="tv-mazo">', unsafe_allow_html=True)
        st.markdown('<div class="tv-carta-fondo c1"></div>', unsafe_allow_html=True)
        st.markdown('<div class="tv-carta-fondo c2"></div>', unsafe_allow_html=True)
        if frase_hoy:
            st.markdown(
                f'<div class="tv-carta-hoy"><p>“{frase_hoy["texto"]}”</p>'
                f'<span>{"— " + frase_hoy["autor"] if frase_hoy.get("autor") else "Carta de hoy"}</span></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="tv-carta-hoy tv-carta-vacia"><p>Todavía no se ha elegido<br>'
                'la carta de hoy.<br>Vuelve más tarde.</p></div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

        anteriores = sorted(
            [f for f in frases if f["fecha"] != date.today().isoformat()],
            key=lambda f: f["fecha"], reverse=True
        )[:8]
        if anteriores:
            with st.expander("Ver cartas anteriores"):
                for f in anteriores:
                    st.write(f"**{f['fecha']}** — “{f['texto']}”" + (f" — {f['autor']}" if f.get("autor") else ""))

        st.markdown("#### Frases para reflexionar")
        piezas = ['<div class="tv-cuadrito-grid">']
        for texto_frase, autor_frase in FRASES_PAZ_CURADAS:
            texto_seguro = html.escape(texto_frase)
            piezas.append(f'<div class="tv-cuadrito"><p>“{texto_seguro}”<br>— {autor_frase}</p></div>')
        piezas.append('</div>')
        st.markdown("".join(piezas), unsafe_allow_html=True)


# =============================================================================
# ETAPA: APROBACIÓN FINAL DEL PROTAGONISTA (flujo aparte, vía enlace/código)
# =============================================================================
if st.session_state.etapa == 'aprobar':
    limitar_ancho_central()
    st.title("Revisa cómo quedó tu testimonio")
    st.caption("La última palabra siempre es tuya.")

    token_prellenado = st.session_state.pop("token_aprobar_prellenado", "")
    token_ingresado = st.text_input("Pega aquí tu código de seguimiento", value=token_prellenado, key="input_token_aprobar")

    if token_ingresado:
        testimonios = cargar_testimonios()
        testimonio = next((t for t in testimonios if t["token"] == token_ingresado), None)

        if testimonio is None:
            st.error("No encontramos ningún testimonio con ese código.")
        elif testimonio["estado"] != "pendiente_aprobacion_protagonista":
            st.info(f"Este testimonio ya no está esperando aprobación. Estado actual: **{testimonio['estado']}**.")
        else:
            with st.container(border=True):
                st.markdown("**Versión editada por el equipo**")
                st.write(testimonio.get("version_editada_texto") or testimonio.get("contenido_texto"))

            mostrar_en_galeria = st.checkbox("También mostrar en la galería", key="check_galeria_aprobar")
            comentarios_habilitados = st.checkbox("Permitir comentarios de otras personas", value=True, key="check_comentarios_aprobar")

            col_si, col_no = st.columns(2)
            with col_si:
                if st.button("Sí, apruebo esta versión", type="primary", key="btn_aprobar_si", use_container_width=True):
                    testimonio["aprobado_por_protagonista"] = True
                    testimonio["mostrar_en_galeria"] = mostrar_en_galeria
                    testimonio["comentarios_habilitados"] = comentarios_habilitados
                    testimonio["estado"] = "publicado"
                    guardar_testimonios(testimonios)
                    st.success("Listo, tu testimonio quedó publicado tal como lo aprobaste.")
                    st.rerun()
            with col_no:
                if st.button("No, prefiero que quede privado", key="btn_aprobar_no", use_container_width=True):
                    testimonio["aprobado_por_protagonista"] = False
                    testimonio["estado"] = "solo_desahogo"
                    guardar_testimonios(testimonios)
                    st.info("Entendido. Tu testimonio queda privado y no se publicará.")
                    st.rerun()

    if st.button("⬅ Volver al inicio", key="btn_volver_desde_aprobar"):
        st.session_state.etapa = 'principal'
        st.rerun()


# =============================================================================
# ETAPA: PANEL DE MODERACIÓN (aparte, uso interno del equipo)
# =============================================================================
elif st.session_state.etapa == 'moderacion':
    if st.button("⬅ Volver a la plataforma", key="btn_volver_desde_moderacion"):
        st.session_state.etapa = 'principal'
        st.rerun()

    st.markdown("## Panel de moderación")
    st.caption("Este panel no tiene autenticación todavía — agrégala antes de usar en producción.")

    testimonios = cargar_testimonios()
    comentarios = cargar_comentarios()
    capitulos = cargar_capitulos()

    tab_riesgo, tab_pendientes, tab_aprobacion, tab_comentarios, tab_capitulos, tab_frase = st.tabs(
        ["Riesgo", "Pendientes", "Esperando protagonista", "Comentarios", "Capítulos", "Frase del día"]
    )

    with tab_riesgo:
        en_riesgo = [t for t in testimonios if t["estado"] == "en_revision_riesgo"]
        if not en_riesgo:
            st.caption("Sin casos pendientes en esta capa.")
        for t in en_riesgo:
            with st.container(border=True):
                st.write(t.get("contenido_texto") or "(testimonio en audio)")
                revisado_por = st.text_input("Revisado por (alianza de psicólogos)", key=f"riesgo_por_{t['id']}")
                notas = st.text_area("Notas", key=f"riesgo_notas_{t['id']}", height=80)
                siguiente = st.selectbox(
                    "Siguiente estado", ["pendiente_moderacion", "solo_desahogo", "rechazado"],
                    key=f"riesgo_siguiente_{t['id']}",
                )
                if st.button("Guardar revisión", key=f"riesgo_guardar_{t['id']}"):
                    t["riesgo_revisado_por"] = revisado_por or "sin identificar"
                    t["riesgo_notas"] = notas
                    t["estado"] = siguiente
                    guardar_testimonios(testimonios)
                    st.success("Caso de riesgo actualizado.")
                    st.rerun()

    with tab_pendientes:
        pendientes = [t for t in testimonios if t["estado"] == "pendiente_moderacion"]
        if not pendientes:
            st.caption("Sin testimonios pendientes.")
        for t in pendientes:
            with st.container(border=True):
                st.write(t.get("contenido_texto") or "(testimonio en audio)")
                st.caption(f"Visibilidad elegida: {t['visibilidad']}")
                version_editada = st.text_area("Versión editada (si aplica)", key=f"editar_{t['id']}", height=100)
                opciones_cap = {"— sin asignar —": None}
                opciones_cap.update({f"Cap. {c['numero']} — {c['titulo']}": c["id"] for c in capitulos})
                cap_elegido = st.selectbox("Asignar a capítulo", list(opciones_cap.keys()), key=f"cap_{t['id']}")
                col_ok, col_no = st.columns(2)
                with col_ok:
                    if st.button("Enviar a aprobación del protagonista", type="primary", key=f"curar_ok_{t['id']}", use_container_width=True):
                        t["version_editada_texto"] = version_editada or t.get("contenido_texto")
                        t["capitulo_id"] = opciones_cap[cap_elegido]
                        t["estado"] = "pendiente_aprobacion_protagonista"
                        guardar_testimonios(testimonios)
                        st.success("Enviado al protagonista para su aprobación final.")
                        st.rerun()
                with col_no:
                    if st.button("Rechazar", key=f"curar_no_{t['id']}", use_container_width=True):
                        t["estado"] = "rechazado"
                        guardar_testimonios(testimonios)
                        st.info("Testimonio rechazado.")
                        st.rerun()

    with tab_aprobacion:
        esperando = [t for t in testimonios if t["estado"] == "pendiente_aprobacion_protagonista"]
        if not esperando:
            st.caption("Nadie esperando en esta fase.")
        for t in esperando:
            with st.container(border=True):
                st.write(t.get("version_editada_texto"))
                st.caption("Código de aprobación para enviarle a la persona:")
                st.code(t["token"])

    with tab_comentarios:
        pendientes_c = [c for c in comentarios if c["estado"] == "pendiente"]
        if not pendientes_c:
            st.caption("Sin comentarios pendientes.")
        for c in pendientes_c:
            with st.container(border=True):
                st.write(c["texto"])
                st.caption(f"Autor: {c.get('autor_nombre') or 'Anónimo'} · Testimonio #{c['testimonio_id']}")
                col_ok, col_no = st.columns(2)
                with col_ok:
                    if st.button("Aprobar", type="primary", key=f"com_ok_{c['id']}", use_container_width=True):
                        c["estado"] = "aprobado"
                        guardar_comentarios(comentarios)
                        st.rerun()
                with col_no:
                    if st.button("Rechazar", key=f"com_no_{c['id']}", use_container_width=True):
                        c["estado"] = "rechazado"
                        guardar_comentarios(comentarios)
                        st.rerun()

    with tab_capitulos:
        st.markdown("#### Crear nuevo capítulo")
        numero = st.number_input("Número", min_value=1, step=1, key="nuevo_cap_numero")
        titulo = st.text_input("Título", key="nuevo_cap_titulo")
        descripcion = st.text_area("Descripción", key="nuevo_cap_descripcion", height=80)
        fecha_hecho = st.date_input("Fecha del hecho histórico", key="nuevo_cap_fecha")
        video_url = st.text_input(
            "URL de video (YouTube, opcional)", key="nuevo_cap_video",
            placeholder="https://www.youtube.com/watch?v=...",
        )
        audio_capitulo = st.file_uploader("O audio final del capítulo (opcional)", type=["mp3", "wav", "m4a", "ogg"], key="nuevo_cap_audio")
        publicado = st.checkbox("Publicar ya", key="nuevo_cap_publicado")

        if st.button("Crear capítulo", type="primary", key="btn_crear_capitulo"):
            if not titulo:
                st.error("Ponle un título al capítulo.")
            else:
                audio_path = guardar_audio_subido(audio_capitulo) if audio_capitulo else None
                capitulos.append({
                    "id": nuevo_id(capitulos),
                    "numero": int(numero),
                    "titulo": titulo,
                    "descripcion": descripcion,
                    "fecha_hecho": fecha_hecho.isoformat(),
                    "audio_path": audio_path,
                    "video_url": video_url or None,
                    "publicado": publicado,
                })
                guardar_capitulos(capitulos)
                st.success("Capítulo creado.")
                st.rerun()

        st.markdown("---")
        st.markdown("#### Capítulos existentes")
        for cap in sorted(capitulos, key=lambda c: c["numero"]):
            st.write(f"Cap. {cap['numero']} — {cap['titulo']} · {'Publicado' if cap['publicado'] else 'Borrador'}")

    with tab_frase:
        st.markdown("#### Cargar la carta/frase de un día")
        fecha_frase = st.date_input("Fecha", value=date.today(), key="frase_fecha")
        texto_frase = st.text_area("Frase o reflexión", key="frase_texto", height=80)
        autor_frase = st.text_input("Autor (opcional)", key="frase_autor")
        if st.button("Guardar frase", type="primary", key="btn_guardar_frase"):
            if not texto_frase:
                st.error("Escribe una frase antes de guardar.")
            else:
                frases = cargar_frases()
                frases = [f for f in frases if f["fecha"] != fecha_frase.isoformat()]
                frases.append({"fecha": fecha_frase.isoformat(), "texto": texto_frase, "autor": autor_frase or None})
                guardar_frases(frases)
                st.success("Frase guardada.")
                st.rerun()


# =============================================================================
# ETAPA: PRINCIPAL
# =============================================================================
else:
    asegurar_capitulo_demo()
    colcha_sidebar()
    barra_superior()
    seccion = st.session_state.seccion

    # -------------------------------------------------------------------
    # INICIO — Cómo funciona + Quiénes somos + Privacidad
    # -------------------------------------------------------------------
    if seccion == "Inicio":
        st.markdown("## Cómo funciona, capítulo por capítulo")
        st.write(
            "El **podcast** es el eje: cada capítulo se nutre de testimonios "
            "reales marcados como públicos, curados y editados por el equipo, "
            "y publicados solo cuando su protagonista aprueba la versión final."
        )
        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.markdown("**Línea del tiempo**")
                st.write("Un punto por capítulo, ubicado según la fecha del hecho histórico que trata.")
            with st.container(border=True):
                st.markdown("**Galería virtual**")
                st.write("Un museo de imágenes organizado por capítulo, con lo que cada protagonista aprobó mostrar.")
        with c2:
            with st.container(border=True):
                st.markdown("**Bitácora**")
                st.write("Un espacio de chat con reflexiones sobre los testimonios, moderadas antes de publicarse.")
            with st.container(border=True):
                st.markdown("**Colcha por la paz**")
                st.write("Mira la barra lateral: cada día se elige una carta distinta del mazo.")

        st.markdown("---")
        st.markdown("## Quiénes somos")
        col_texto, col_espacio, col_imagen = st.columns([1.6, 0.15, 1])
        with col_texto:
            st.write(
                "Tejiendo Verdad es un espacio donde cada hilo cuenta una "
                "historia y cada historia construye paz, nacido de una "
                "comunidad comprometida con la memoria y la reconciliación."
            )
            st.write(
                "Voces silenciadas por el miedo, heridas sin sanar, memorias "
                "fragmentadas que aún esperan ser reconocidas. Tejiendo Verdad "
                "es una plataforma digital que transforma esa memoria en acción, "
                "co-creada con víctimas y comunidad."
            )
        with col_imagen:
            mostrar_imagen_o_aviso("imagen_rostros.png", "Rostros de la comunidad")

        col_img2, col_espacio2, col_texto2 = st.columns([1, 0.15, 1.6])
        with col_img2:
            mostrar_imagen_o_aviso("imagen_territorio.png", "Territorio de paz")
        with col_texto2:
            st.markdown("#### Público objetivo")
            st.write(
                "Nuestro impacto comienza en casa: nuestra propia comunidad "
                "educativa (estudiantes, docentes, trabajadores y familias). "
                "Buscamos replicar el modelo en otras instituciones, para que "
                "la reconciliación no tenga fronteras: la meta es llegar a 10 "
                "instituciones y más de 1000 jóvenes."
            )

        st.markdown("#### Alianza con psicólogos")
        st.write(
            "**Capa 1 — Filtro de riesgo:** todo testimonio (público o privado) "
            "pasa por un protocolo automático y revisión humana capacitada, que "
            "distingue un relato del pasado de una señal de crisis actual, antes "
            "de guardarlo."
        )
        st.write(
            "**Capa 2 — 'Quiero hablar con alguien ahora':** el botón de arriba "
            "de la página, visible en todo momento, no solo al grabar un "
            "testimonio."
        )

        st.markdown("---")
        st.markdown("## Privacidad y consentimiento")
        st.write("No necesitas mostrarte ni ser visto para dejar tu testimonio.")
        st.write("Puedes elegir que sea solo desahogo, privado y nunca publicado.")
        st.write("Si se va a publicar, siempre ves y apruebas la versión final antes.")
        st.write("Los datos de contacto son opcionales, solo para avisarte del proceso.")

    # -------------------------------------------------------------------
    # PODCAST — con espacio para video
    # -------------------------------------------------------------------
    elif seccion == "Podcast":
        capitulos_pub = sorted([c for c in cargar_capitulos() if c.get("publicado")], key=lambda c: c["numero"])
        st.caption(
            "Rostros y Voces del Conflicto — cada capítulo se construye a partir "
            "de testimonios reales, editados junto a su protagonista y "
            "publicados solo con su aprobación final."
        )
        if not capitulos_pub:
            st.caption("Todavía no hay capítulos publicados.")

        cap_abierto_id = st.session_state.capitulo_seleccionado_id
        for cap in capitulos_pub:
            abierto = (cap_abierto_id == cap["id"])
            with st.container(border=True):
                col_txt, col_btn = st.columns([4, 1])
                with col_txt:
                    st.markdown(f"**Cap. {cap['numero']} — {cap['titulo']}**")
                    st.caption(cap.get("descripcion", ""))
                    st.caption(f"Hecho histórico: {cap['fecha_hecho']}")
                with col_btn:
                    etiqueta = "Cerrar" if abierto else "Abrir"
                    if st.button(etiqueta, key=f"toggle_cap_{cap['id']}", use_container_width=True):
                        st.session_state.capitulo_seleccionado_id = None if abierto else cap["id"]
                        st.rerun()

                if abierto:
                    st.markdown("---")
                    if cap.get("video_url"):
                        st.video(cap["video_url"])
                    elif cap.get("audio_path") and os.path.exists(cap["audio_path"]):
                        st.audio(cap["audio_path"])
                    else:
                        mostrar_imagen_o_aviso(
                            f"video_cap{cap['numero']}.mp4",
                            "Espacio para el video de este capítulo (o audio, desde el panel de moderación)",
                        )

                    testimonios_cap = [
                        t for t in cargar_testimonios()
                        if t.get("capitulo_id") == cap["id"] and t["estado"] == "publicado" and t["aprobado_por_protagonista"]
                    ]
                    if not testimonios_cap:
                        st.caption("Este capítulo aún no tiene testimonios asociados públicamente.")
                    for t in testimonios_cap:
                        st.write(t.get("version_editada_texto") or t.get("contenido_texto"))
                        bloque_bitacora_inline(t, contexto="podcast", en_expander=True)

    # -------------------------------------------------------------------
    # GALERÍA VIRTUAL — museo de imágenes
    # -------------------------------------------------------------------
    elif seccion == "Galería virtual":
        st.caption("Un museo de imágenes, organizado por capítulo. Solo lo que cada protagonista aprobó mostrar.")
        capitulos_gal = sorted([c for c in cargar_capitulos() if c.get("publicado")], key=lambda c: c["numero"])
        testimonios_todos = cargar_testimonios()

        for cap in capitulos_gal:
            st.markdown(f"#### Cap. {cap['numero']} — {cap['titulo']}")
            del_capitulo = [
                t for t in testimonios_todos
                if t.get("capitulo_id") == cap["id"] and t["mostrar_en_galeria"] and t["estado"] == "publicado"
            ]

            if del_capitulo:
                cols = st.columns(3)
                for i, t in enumerate(del_capitulo):
                    with cols[i % 3]:
                        mostrar_imagen_o_aviso(f"galeria_testimonio_{t['id']}.png", "Foto del testimonio")
                        st.caption(t.get("version_editada_texto") or t.get("contenido_texto"))
                        bloque_bitacora_inline(t, contexto=f"galeria_{cap['id']}", en_expander=True)
            else:
                # Espacio reservado: aún no hay testimonios aprobados para
                # este capítulo, pero el "marco" ya queda listo en el museo.
                cols = st.columns(3)
                for i in range(3):
                    with cols[i]:
                        mostrar_imagen_o_aviso(f"galeria_cap{cap['numero']}_{i+1}.png", f"Imagen {i+1} — {cap['titulo']}")
                st.caption("Cuando haya testimonios aprobados para este capítulo, sus imágenes aparecerán aquí.")
            st.markdown("---")

    # -------------------------------------------------------------------
    # LÍNEA DEL TIEMPO
    # -------------------------------------------------------------------
    elif seccion == "Línea del tiempo":
        st.caption("Una línea con las fechas y los sucesos, en el orden en que ocurrieron.")
        capitulos_tiempo = sorted([c for c in cargar_capitulos() if c.get("publicado")], key=lambda c: c["fecha_hecho"])
        if not capitulos_tiempo:
            st.caption("Todavía no hay capítulos publicados en la línea de tiempo.")
        else:
            piezas = ['<div class="tv-timeline">']
            for cap in capitulos_tiempo:
                fecha_legible = datetime.strptime(cap["fecha_hecho"], "%Y-%m-%d").strftime("%d de %B de %Y")
                titulo_seguro = html.escape(cap["titulo"])
                descripcion_segura = html.escape(cap.get("descripcion", ""))
                piezas.append(f'''
                <div class="tv-timeline-item">
                  <div class="tv-timeline-dot"></div>
                  <div class="tv-timeline-fecha">{fecha_legible}</div>
                  <div class="tv-timeline-card">
                    <strong>Cap. {cap["numero"]} — {titulo_seguro}</strong>
                    <p>{descripcion_segura}</p>
                  </div>
                </div>
                ''')
            piezas.append('</div>')
            st.markdown("".join(piezas), unsafe_allow_html=True)

            st.markdown("##### Ir directo a un capítulo")
            cols_ir = st.columns(len(capitulos_tiempo))
            for col, cap in zip(cols_ir, capitulos_tiempo):
                with col:
                    if st.button(f"Cap. {cap['numero']}", key=f"tiempo_cap_{cap['id']}", use_container_width=True):
                        st.session_state.capitulo_seleccionado_id = cap["id"]
                        st.session_state.seccion = "Podcast"
                        st.rerun()

    # -------------------------------------------------------------------
    # BITÁCORA — como un chat, todos los testimonios publicados
    # -------------------------------------------------------------------
    elif seccion == "Bitácora":
        st.caption("Reflexiones tipo chat sobre los testimonios publicados, agrupadas por capítulo.")
        capitulos_bit = sorted([c for c in cargar_capitulos() if c.get("publicado")], key=lambda c: c["numero"])
        testimonios_bit = cargar_testimonios()
        hubo_bitacora = False
        for cap in capitulos_bit:
            del_cap = [
                t for t in testimonios_bit
                if t.get("capitulo_id") == cap["id"] and t["estado"] == "publicado" and t["aprobado_por_protagonista"]
            ]
            if not del_cap:
                continue
            hubo_bitacora = True
            st.markdown(f"#### Cap. {cap['numero']} — {cap['titulo']}")
            for t in del_cap:
                with st.container(border=True):
                    bloque_bitacora_inline(t, contexto="bitacora", en_expander=False)
        if not hubo_bitacora:
            st.caption("Todavía no hay testimonios publicados para reflexionar en el chat.")

    # -------------------------------------------------------------------
    # TESTIMONIO — enviar, sin login
    # -------------------------------------------------------------------
    elif seccion == "Testimonio":
        if st.session_state.testimonio_recien_enviado:
            info = st.session_state.testimonio_recien_enviado
            with st.container(border=True):
                estado = info["estado"]
                if estado == "solo_desahogo":
                    st.write("Tu testimonio quedó guardado solo como desahogo. Nadie más lo verá.")
                elif estado == "en_revision_riesgo":
                    st.warning(
                        "Detectamos algo en tu mensaje que queremos revisar con más "
                        "cuidado y cariño. Alguien del equipo de apoyo va a leerlo pronto."
                    )
                elif estado == "rechazado":
                    st.write("No pudimos procesar este envío.")
                else:
                    st.write(
                        "Tu testimonio quedó guardado y será revisado por el equipo. Si "
                        "elegiste que sea público, antes de publicarlo siempre te "
                        "pediremos que apruebes la versión final."
                    )
                st.caption("Guarda este código para hacer seguimiento y aprobar tu testimonio más adelante:")
                st.code(info["token"])
                if st.button("Dejar otro testimonio", key="btn_otro_testimonio"):
                    st.session_state.testimonio_recien_enviado = None
                    st.rerun()
        else:
            st.write(
                "No necesitas registrarte ni mostrar tu cara. Puedes grabar un audio o "
                "escribir. Tú decides al final si esto se queda solo entre nosotros o si "
                "algún día se comparte."
            )

            tipo_contenido = st.radio(
                "1. ¿Cómo quieres contarlo?",
                ["Escribir mi testimonio", "Grabar un audio contando lo sucedido"],
                key="tipo_contenido_testimonio",
            )

            contenido_texto = None
            archivo_audio = None
            if tipo_contenido == "Escribir mi testimonio":
                contenido_texto = st.text_area(
                    "Tu testimonio", height=200, key="texto_testimonio",
                    placeholder="Escribe con tus propias palabras, sin prisa. Nadie más lo ve hasta que tú lo decidas.",
                )
            else:
                archivo_audio = st.file_uploader(
                    "Archivo de audio (mp3, wav, m4a, ogg)", type=["mp3", "wav", "m4a", "ogg", "webm"],
                    key="audio_testimonio",
                )

            tipo_violencia = st.selectbox(
                "2. Tipo de violencia vivida (opcional)",
                ["Prefiero no especificar"] + TIPOS_VIOLENCIA,
                key="tipo_violencia_testimonio",
            )

            visibilidad = st.radio(
                "3. ¿Qué quieres que pase con tu testimonio?",
                [
                    "Solo desahogo — que quede guardado, no se publica en ningún lado",
                    "Público — puede llegar a la galería o al podcast (te pediremos tu aprobación final antes)",
                ],
                key="visibilidad_testimonio",
            )

            email_contacto = st.text_input(
                "4. Correo de contacto (opcional)", key="email_testimonio",
                placeholder="tucorreo@ejemplo.com",
            )
            st.caption(
                "Solo lo usamos para avisarte si tu testimonio va a publicarse y pedirte "
                "tu aprobación final, o si el equipo de apoyo necesita contactarte."
            )

            if st.button("Enviar mi testimonio", type="primary", key="btn_enviar_testimonio"):
                if tipo_contenido == "Escribir mi testimonio" and not contenido_texto:
                    st.error("Escribe tu testimonio antes de enviarlo.")
                elif tipo_contenido != "Escribir mi testimonio" and archivo_audio is None:
                    st.error("Sube un archivo de audio antes de enviarlo.")
                else:
                    audio_path = guardar_audio_subido(archivo_audio) if archivo_audio is not None else None

                    if parece_spam(contenido_texto):
                        estado, riesgo = "rechazado", False
                    else:
                        estado, riesgo = estado_inicial_testimonio(contenido_texto)

                    es_privado = visibilidad.startswith("Solo desahogo")
                    if es_privado and estado == "pendiente_moderacion":
                        estado = "solo_desahogo"

                    testimonios = cargar_testimonios()
                    testimonio = {
                        "id": nuevo_id(testimonios),
                        "token": uuid.uuid4().hex,
                        "tipo_contenido": "texto" if tipo_contenido == "Escribir mi testimonio" else "audio",
                        "contenido_texto": contenido_texto,
                        "audio_path": audio_path,
                        "tipo_violencia": None if tipo_violencia == "Prefiero no especificar" else tipo_violencia,
                        "visibilidad": "privado" if es_privado else "publico",
                        "estado": estado,
                        "riesgo_detectado": riesgo,
                        "riesgo_revisado_por": None,
                        "riesgo_notas": None,
                        "email_contacto": email_contacto or None,
                        "capitulo_id": None,
                        "version_editada_texto": None,
                        "aprobado_por_protagonista": False,
                        "mostrar_en_galeria": False,
                        "comentarios_habilitados": True,
                        "creado_en": datetime.now(timezone.utc).isoformat(),
                    }
                    testimonios.append(testimonio)
                    guardar_testimonios(testimonios)

                    st.session_state.testimonio_recien_enviado = {
                        "token": testimonio["token"], "estado": testimonio["estado"],
                    }
                    st.rerun()

    st.markdown("---")
    st.caption("Tejiendo Verdad")
    if st.button("Panel de moderación (equipo)", key="btn_ir_moderacion"):
        st.session_state.etapa = 'moderacion'
        st.rerun()