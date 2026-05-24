import requests
import streamlit as st

# ==============================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA & ESTILOS CUSTOM (CÓDIGO CSS LIMPIO)
# ==============================================================================
st.set_page_config(
    page_title="UPTC | Predicción de Riesgo",
    page_icon="🎓",
    layout="wide"
)

st.markdown("""
    <style>
        /* Títulos principales */
        .main-title {
            font-size: 2.3rem !important;
            font-weight: 700 !important;
            color: #FFFFFF;
            margin-bottom: 0.2rem;
        }
        .subtitle {
            font-size: 1.1rem !important;
            color: #A3AED0 !important;
            margin-bottom: 2rem;
        }
        .section-header {
            font-size: 1.4rem !important;
            font-weight: 600 !important;
            color: #F4F7FE;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
        }

        /* Contenedor del Formulario */
        div[data-testid="stForm"] {
            border: 1px solid #1E293B !important;
            background-color: #0F172A !important;
            border-radius: 14px !important;
            padding: 2rem !important;
        }

        /* 🎯 ESTILO ESTABLE PARA EL BOTÓN PRINCIPAL DEL FORMULARIO */
        div[data-testid="stForm"] button {
            background-color: #0066CC !important; /* Azul Institucional */
            color: #FFFFFF !important;
            font-weight: bold !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.7rem 2rem !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2) !important;
        }

        div[data-testid="stForm"] button:hover {
            background-color: #0052A3 !important; /* Azul más oscuro en hover */
            box-shadow: 0 4px 15px rgba(0, 102, 204, 0.4) !important;
            transform: translateY(-1px);
        }

        /* 🧼 SIN FONDO AZUL EN LOS BOTONES - Y + DEL INPUT NUMÉRICO */
        div[data-testid="stNumberInput"] button {
            background-color: transparent !important;
            border: none !important;
            color: #FFFFFF !important;
            box-shadow: none !important;
        }
        div[data-testid="stNumberInput"] button:hover {
            background-color: rgba(255, 255, 255, 0.1) !important;
            color: #FFFFFF !important;
        }

        /* Estilos de las cajas de recomendación personalizadas */
        .box-recomendacion {
            padding: 1.5rem;
            border-radius: 10px;
            color: #FFFFFF;
            font-size: 1.05rem;
            font-weight: 500;
            line-height: 1.5;
            margin-top: 0.5rem;
            border-left: 6px solid rgba(0,0,0,0.2);
        }
        .box-alto { background-color: #7A1C1C !important; }  /* Rojo elegante */
        .box-medio { background-color: #8A531C !important; } /* Naranja quemado */
        .box-bajo { background-color: #1C6446 !important; }  /* Verde oscuro */

        /* Tamaño de valores de métricas */
        [data-testid="stMetricValue"] {
            font-size: 1.9rem !important;
            font-weight: 700 !important;
        }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. CONFIGURACIÓN DE VARIABLES Y OPCIONES
# ==============================================================================
API_URL_LOCAL = "https://proyecto-analitica-uptc.onrender.com/predict"
TIMEOUT = 10

MAP_GENERO = {"Masculino": "M", "Femenino": "F"}
MAP_SINO = {"Sí": 1, "No": 0}

OP_FACULTAD = [
    "FACULTAD DE INGENIERIA",
    "FACULTAD DE CIENCIAS",
    "FACULTAD DE CIENCIAS DE LA EDUCACION",
    "FACULTAD DE CIENCIAS ECONOMICAS Y ADMINISTRATIVAS",
    "FACULTAD DE CIENCIAS DE LA SALUD",
    "FACULTAD DE CIENCIAS AGROPECUARIAS",
    "FACULTAD DE DERECHO Y CIENCIAS SOCIALES"
]

OP_JORNADA = ["DIURNA", "NOCTURNA", "EXTENDIDA", "OTRA"]
OP_MODALIDAD = ["PRESENCIAL", "VIRTUAL", "DISTANCIA"]
OP_SEDE = ["TUNJA", "SOGAMOSO", "DUITAMA", "CHIQUINQUIRA", "OTRA"]
OP_ORIGEN = ["TUNJA", "SOGAMOSO", "DUITAMA", "CHIQUINQUIRA", "OTRA"]


def resetear_formulario():
    for k in list(st.session_state.keys()):
        if k.startswith("f_"):
            del st.session_state[k]


# ==============================================================================
# 3. PANEL LATERAL (SIDEBAR)
# ==============================================================================
with st.sidebar:
    st.markdown("### ⚙️ Panel de Control")
    api_url = st.text_input("URL del Servidor API", value=API_URL_LOCAL, key="api_url")
    mostrar_json = st.toggle("Modo Desarrollador (Ver JSON)", value=False, key="toggle_json")

    st.markdown("---")
    st.button("🧹 Limpiar Campos", on_click=resetear_formulario, use_container_width=True)

    st.markdown("---")
    st.markdown("💡 **Ayuda Rápida**")
    st.caption(
        "Este sistema utiliza un modelo de Machine Learning para evaluar variables "
        "socioeconómicas y académicas, estimando la probabilidad de deserción estudiantil."
    )

# ==============================================================================
# 4. ENCABEZADO PRINCIPAL
# ==============================================================================
st.markdown('<p class="main-title">🎓 UPTC | Sistema de Alerta Temprana</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Modelo Analítico de Predicción de Riesgo de Deserción</p>', unsafe_allow_html=True)

# ==============================================================================
# 5. FORMULARIO DE ENTRADA
# ==============================================================================
st.markdown('<p class="section-header">🧾 Formulario de Caracterización Estudiantil</p>', unsafe_allow_html=True)

with st.form("form_pred"):
    # Fila 1 (Ajustada a 4 columnas para integrar FACULTAD)
    c1, c2, c3, c_fac = st.columns(4)
    with c1:
        periodo = st.text_input("PERIODO ACADÉMICO", value="2025-1", key="f_periodo")
    with c2:
        genero_sel = st.selectbox("GÉNERO", list(MAP_GENERO.keys()), index=0, key="f_genero")
    with c3:
        estrato = st.selectbox("ESTRATO SOCIOECONÓMICO", [1, 2, 3, 4, 5, 6], index=1, key="f_estrato")
    with c_fac:
        facultad_sel = st.selectbox("FACULTAD", OP_FACULTAD, index=0, key="f_facultad")

    # Fila 2
    c4, c5, c6 = st.columns(3)
    with c4:
        sede = st.selectbox("SEDE DE ESTUDIO", OP_SEDE, index=0, key="f_sede")
    with c5:
        modalidad = st.selectbox("MODALIDAD DE ESTUDIO", OP_MODALIDAD, index=0, key="f_modalidad")
    with c6:
        jornada = st.selectbox("JORNADA", OP_JORNADA, index=0, key="f_jornada")

    # Fila 3
    c7, c8, c9 = st.columns(3)
    with c7:
        origen_sel = st.selectbox("ORIGEN GEOGRÁFICO", OP_ORIGEN, index=0, key="f_origen_sel")
    with c8:
        promedio = st.number_input(
            "PROMEDIO HISTÓRICO DE LA SEDE",
            min_value=0.0, max_value=5.0, value=3.8, step=0.1, key="f_promedio"
        )
    with c9:
        st.markdown("**Condiciones Especiales**")
        cx, cy = st.columns(2)
        with cx:
            foraneo_txt = st.radio("¿FORÁNEO?", ["No", "Sí"], index=1, horizontal=True, key="f_foraneo")
        with cy:
            joven_txt = st.radio("¿JOVEN?", ["No", "Sí"], index=1, horizontal=True, key="f_joven")

    # Mostrar dinámicamente si se requiere origen manual
    origen_manual = ""
    if origen_sel == "OTRA":
        st.markdown("---")
        origen_manual = st.text_input(
            "Especificar origen geográfico (Requerido para la opción 'OTRA')",
            placeholder="Ej. Paipa, Puerto Boyacá, Villa de Leyva...",
            key="f_origen_manual"
        ).strip()

    st.markdown("<br>", unsafe_allow_html=True)
    calcular = st.form_submit_button("🚀 Ejecutar Análisis de Riesgo", use_container_width=True)

# ==============================================================================
# 6. PROCESAMIENTO DEL PAYLOAD
# ==============================================================================
origen_final = (origen_manual if origen_manual and origen_sel == "OTRA" else origen_sel).upper()

payload = {
    "PERIODO": periodo.strip(),
    "ESTRATO": int(estrato),
    "FORANEO": MAP_SINO[foraneo_txt],
    "JOVEN": MAP_SINO[joven_txt],
    "JORNADA": jornada.upper(),
    "MODALIDAD": modalidad.upper(),
    "NOMBRE_SEDE": sede.upper(),
    "GENERO": MAP_GENERO[genero_sel],
    "ORIGEN_GEOGRAFICO": origen_final,
    "PROMEDIO_HISTORICO_SEDE": float(promedio),
    "FACULTAD": facultad_sel.upper()
}

# Mostrar JSON si está activo el modo desarrollador
if mostrar_json:
    st.caption(f"📌 Facultad seleccionada (NO se envía al API): **{facultad_sel}**")
    with st.expander("📦 [DEBUG] JSON de Entrada que recibirá la API"):
        st.json(payload)

# ==============================================================================
# 7. EJECUCIÓN Y RENDERIZADO DE RESULTADOS (CON COLORES INSTITUCIONALES)
# ==============================================================================
if calcular:
    if "-" not in periodo or not periodo.split("-")[0].strip().isdigit():
        st.error("⚠️ PERIODO inválido. Usa formato AAAA-1 o AAAA-2 (Ej: 2025-1).")
    elif origen_sel == "OTRA" and not origen_manual:
        st.error("⚠️ Por favor, especifique el municipio en el campo 'Especificar origen geográfico'.")
    else:
        st.markdown("---")
        
        # URL local estándar de Flask
        API_URL = "http://127.0.0.1:5000/predict"
        
        with st.spinner("🔄 Conectando con la API de la UPTC... Por favor espere."):
            try:
                # Intentamos la conexión real con la API
                response = requests.post(API_URL, json=payload, timeout=10)
                res_data = response.json()
                
                if response.status_code == 200 and res_data.get('estado') == 'Exitoso':
                    st.success("🎉 ¡Conexión Exitosa con el Modelo Real!")
                    
                    # Extraemos las variables de la respuesta de la API
                    perfil = res_data.get('perfil_riesgo', 'N/A')
                    probabilidad = res_data.get('probabilidad_desercion', 'N/A')
                    recomendacion = res_data.get('recomendacion_institucional', 'No hay recomendación disponible.')
                    
                    # Lógica de colores según el perfil de riesgo detectado
                    if "alto" in perfil.lower():
                        color_banner = "🔴"
                        clase_caja = "box-alto"
                    elif "medio" in perfil.lower():
                        color_banner = "🟠"
                        clase_caja = "box-medio"
                    else:
                        color_banner = "🟢"
                        clase_caja = "box-bajo"
                    
                    st.markdown('<p class="section-header">🎯 Diagnóstico de Permanencia</p>', unsafe_allow_html=True)
                    
                    # Renderizado de las tarjetas de métricas en 3 columnas
                    with st.container(border=True):
                        c_eval, c_prob, c_est = st.columns(3)
                        with c_eval:
                            st.metric(label="Evaluación del Modelo", value=f"{color_banner} {perfil}")
                        with c_prob:
                            st.metric(label="Probabilidad de Deserción", value=probabilidad)
                        with c_est:
                            st.metric(label="Estado de la Consulta", value="Éxito")
                        
                    # Caja de recomendación pintada dinámicamente con CSS custom
                    st.markdown("### 📌 Plan de Acción e Intervención")
                    st.markdown(f'<div class="box-recomendacion {clase_caja}">{recomendacion}</div>', unsafe_allow_html=True)
                
                else:
                    # Si la API respondió pero con un error técnico controlado
                    st.error("⚠️ La API de Flask respondió con un error controlado:")
                    st.warning(f"Código de Estado HTTP: {response.status_code}")
                    st.json(res_data)
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ ERROR DE CONEXIÓN: No se pudo hacer contacto con la API.")
                st.markdown(
                    f"> **¿Qué significa esto?** El servidor de Flask (`app_multimodelo.py`) está apagado "
                    f"o está corriendo en un puerto diferente al **5000**. \n\n"
                    f"**Solución:** Ve a la terminal de VS Code y asegúrate de que esté ejecutándose con `python app_multimodelo.py`."
                )
            except Exception as e:
                st.error(f"💥 Ocurrió un error inesperado en la interfaz: {str(e)}")
                
        # Bloque de Debug en caso de fallos
        if 'res_data' in locals() and response.status_code != 200:
            st.markdown("### 📥 [DEBUG] Respuesta Completa de la API")
            st.json(res_data)